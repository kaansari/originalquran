import json
import tempfile
import unittest
from pathlib import Path
import build_page

class PageBuilderTests(unittest.TestCase):
    def test_markdown_newer_than_manifest_is_included_and_missing_text_remains_browsable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'entries').mkdir()
            source = 'https://arabiclexicon.hawramani.com/entry/?book=9'
            (root / 'index.json').write_text(json.dumps({'entries': [
                {'id': 'aaa', 'heading': 'رَحَمَ', 'url': source, 'text': 'older text'},
                {'id': 'bbb', 'heading': 'كَتَبَ', 'url': source},
                {'id': 'ccc', 'heading': 'عَلَمَ', 'url': source},
            ]}), encoding='utf-8')
            for entry_id, heading in [('aaa', 'رَحَمَ'), ('bbb', 'كَتَبَ')]:
                (root / 'entries' / (entry_id + '.md')).write_text(
                    f'# {heading}\n\nDictionary: Ibn Faris\n\nSource: {source}\n\nDefinition {entry_id}.\n\nSecond paragraph.', encoding='utf-8')
            result = build_page.collect(root)
            self.assertEqual(result['available'], 2)
            self.assertEqual(result['total'], 3)
            self.assertEqual(result['entries'][0]['text'], 'Definition aaa.\n\nSecond paragraph.')
            self.assertEqual(result['entries'][1]['text'], 'Definition bbb.\n\nSecond paragraph.')
            self.assertEqual(result['entries'][2]['text'], '')

    def test_embedded_dictionary_cannot_close_script_or_execute_html(self):
        template = '<html><script id="dictionary-data" type="application/json">__DICTIONARY_DATA__</script><script>__DICTIONARY_CORE__</script></html>'
        html = build_page.render(template, {'entries': [{'text': '</script><img src=x onerror=alert(1)>'}]}, '// core')
        self.assertEqual(html.count('</script>'), 2)
        embedded = html.split('application/json">', 1)[1].split('</script>', 1)[0]
        self.assertEqual(json.loads(embedded)['entries'][0]['text'], '</script><img src=x onerror=alert(1)>')

    def test_invalid_template_fails_before_overwriting_page(self):
        with self.assertRaises(ValueError):
            build_page.render('<html></html>', {'entries': []}, '// core')

if __name__ == '__main__':
    unittest.main()
