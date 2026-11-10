import tempfile
import unittest
import ssl
import socket
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
import download

INDEX = '''<h1>Book</h1><a href="/about/">About</a>
<a href="/أَبَّ/?book=9">أَبَّ</a><a href="/أَبَّ/?book=9">أَبَّ</a>
<a href="/أَثَرَ/?book=9">أَثَرَ</a>
<a href="https://other.example/x?book=9">other</a>
<a href="/foo/?book=8">Other dictionary</a>'''
ENTRY = '''<script>unwanted script</script><div>Navigation</div>
<h2>Entries on أَبَّ in 1 Arabic dictionary by the author Ibn Fāris, Maqāyīs al-Lugha</h2>
<a href="/ibn-faris-maqayis-al-lugha/">Ibn Fāris, Maqāyīs al-Lugha</a>
<p><a href="/?p=11182&amp;book=9#15bece">Permalink</a> (الرابط القصير إلى هذا الباب):</p>
<p>https://arabiclexicon.hawramani.com/?p=11182&amp;book=9#15bece</p>
<p>(أَبَّ) اعْلَمْ أَنَّ لِلْهَمْزَةِ وَالْبَاءِ أَصْلَيْنِ.</p>
<p>قَالَ الْخَلِيلُ: الْمَرْعَى.</p>
<div>You are viewing The Arabic Lexicon in filtered mode.</div>
<h2>Similar and related entries:</h2><p>Other dictionary definition</p>'''

class ExtractionTests(unittest.TestCase):
    def test_timeout_skips_entry_and_rerun_retries_only_missing_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'raw').mkdir()
            (out / 'raw/index.html').write_text(INDEX, encoding='utf-8')
            first, second = download.parse_index(INDEX)
            def request(url):
                if url.endswith('/robots.txt'):
                    return 'User-agent: *\nAllow: /'
                if url == first['url']:
                    raise socket.timeout('The read operation timed out')
                return ENTRY
            with patch.object(download.Fetcher, 'request', side_effect=request):
                result = download.run(out, delay=0, timeout=2, retries=0)
            self.assertFalse(result['complete'])
            self.assertEqual(result['downloaded'], 1)
            self.assertEqual(result['skipped'][0]['url'], first['url'])
            self.assertFalse((out / 'raw' / (first['id'] + '.html')).exists())
            self.assertTrue((out / 'raw' / (second['id'] + '.html')).exists())
            self.assertEqual(len(json.loads((out / 'skipped.json').read_text())), 1)
            with patch.object(download.Fetcher, 'request', return_value=ENTRY) as request_again:
                result = download.run(out, delay=0, timeout=2, retries=0)
            requested = [call[0][0] for call in request_again.call_args_list]
            self.assertIn(first['url'], requested)
            self.assertNotIn(second['url'], requested)
            self.assertTrue(result['complete'])
            self.assertEqual(result['downloaded'], 2)
            self.assertEqual(json.loads((out / 'skipped.json').read_text()), [])

    def test_request_uses_configured_timeout(self):
        with patch.object(download, 'urlopen') as opener:
            response = MagicMock()
            response.read.return_value = b'text'
            response.headers.get_content_charset.return_value = 'utf-8'
            opener.return_value.__enter__.return_value = response
            download.Fetcher(0, False, timeout=7).request(download.INDEX_URL)
            self.assertEqual(opener.call_args[1]['timeout'], 7)

    def test_tls_verification_is_enabled_unless_explicitly_disabled(self):
        for insecure in (False, True):
            with self.subTest(insecure=insecure):
                with patch.object(download, 'urlopen') as opener:
                    response = MagicMock()
                    response.read.return_value = 'نص'.encode('utf-8')
                    response.headers.get_content_charset.return_value = 'utf-8'
                    opener.return_value.__enter__.return_value = response
                    fetcher = download.Fetcher(delay=0, offline=False, insecure=insecure)
                    self.assertEqual(fetcher.request(download.INDEX_URL), 'نص')
                    context = opener.call_args[1]['context']
                    self.assertEqual(context.verify_mode, ssl.CERT_NONE if insecure else ssl.CERT_REQUIRED)
                    self.assertEqual(context.check_hostname, not insecure)
        self.assertEqual(download.Fetcher(0, False).ssl_context.verify_mode, ssl.CERT_REQUIRED)

    def test_insecure_cli_option_reaches_downloader(self):
        with patch.object(download, 'run', return_value={'downloaded': 0, 'total_index_entries': 2}) as run:
            with patch('sys.argv', ['download.py', '--insecure', '--limit', '2']):
                self.assertEqual(download.main(), 0)
            self.assertTrue(run.call_args[1]['insecure'])

    def test_index_deduplicates_and_excludes_other_books_and_hosts(self):
        entries = download.parse_index(INDEX)
        self.assertEqual([e['heading'] for e in entries], ['أَبَّ', 'أَثَرَ'])
        self.assertTrue(all(e['url'].endswith('?book=9') for e in entries))

    def test_post_id_urls_remain_distinct(self):
        entries = download.parse_index('<a href="/?p=10&amp;book=9">أب</a><a href="/?p=20&amp;book=9">أثر</a>')
        self.assertEqual(len(entries), 2)
        self.assertIn("p=10", entries[0]["url"])

    def test_entry_preserves_arabic_and_excludes_related_dictionaries(self):
        text = download.parse_entry(ENTRY)
        self.assertEqual(text, '(أَبَّ) اعْلَمْ أَنَّ لِلْهَمْزَةِ وَالْبَاءِ أَصْلَيْنِ.\n\nقَالَ الْخَلِيلُ: الْمَرْعَى.')

    def test_unrecognized_page_is_rejected_instead_of_saved_as_definition(self):
        for html in ('<h1>Access denied</h1>', ENTRY.replace('Ibn Fāris', 'Another author')):
            with self.assertRaises(ValueError):
                download.parse_entry(html)

    def test_multiple_ibn_faris_definitions_exclude_related_entries(self):
        html = Path(__file__).with_name('multiple_definitions.html').read_text(encoding='utf-8')
        self.assertEqual(download.parse_entry(html),
                         '(الْحَشْرَجَةُ) : تَرَدُّدُ صَوْتِ النَّفَسِ\n\n'
                         '(الْحَشْرَجَةُ) : حُفَيْرَةٌ تُحْفَرُ كَالْحِسْيِ.')

    def test_cached_run_writes_json_and_markdown_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            raw = out / 'raw'
            raw.mkdir()
            (raw / 'index.html').write_text(INDEX, encoding='utf-8')
            for entry in download.parse_index(INDEX):
                (raw / (entry['id'] + '.html')).write_text(ENTRY, encoding='utf-8')
            manifest = download.run(out, delay=0, limit=None, offline=True)
            self.assertEqual(manifest['downloaded'], 2)
            self.assertTrue(manifest['complete'])
            self.assertEqual(len(list((out / 'entries').glob('*.md'))), 2)
            import json
            saved = json.loads((out / 'index.json').read_text())
            self.assertIn('قَالَ الْخَلِيلُ', saved['entries'][0]['text'])
            download.run(out, delay=0, limit=1, offline=True)
            saved = json.loads((out / 'index.json').read_text())
            self.assertEqual(saved['downloaded'], 2)

if __name__ == '__main__':
    unittest.main()
