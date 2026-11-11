import importlib.util
import unittest
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('indian', Path(__file__).parents[1] / 'scripts/build_indian_quran.py')
indian = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indian)


class IndianImportTest(unittest.TestCase):
    def test_indian_word_file_follows_the_other_readers_convention(self):
        root = Path(__file__).parents[1]
        path = root / 'src/json/quranic_indian_words.json'
        text = path.read_text(encoding='utf-8')
        indian_words = json.loads(text)
        canonical = json.loads((root / 'src/json/quran_words.json').read_text(encoding='utf-8'))
        self.assertEqual(list(indian_words), list(canonical))
        self.assertTrue(all(isinstance(value, str) for value in indian_words.values()))
        self.assertEqual(text, json.dumps(indian_words, ensure_ascii=False, indent=2) + '\n')
        self.assertIn('content="json/quranic_indian_words.json"', (root / 'src/indian.html').read_text())
        self.assertFalse((root / 'src/json/indian/words.json').exists())

    def test_supplied_qul_archives_cover_the_complete_quran(self):
        root = Path(__file__).parents[1]
        lines = indian.read_rows(root / 'tools/json.zip', 'pages')
        source = indian.read_rows(root / 'tools/indopak-nastaleeq.json.zip', 'words')
        suras = json.loads((root / 'src/json/sura.json').read_text())
        combined = json.loads((root / 'src/json/combined_quran.json').read_text())
        pages, words, layout = indian.convert(lines, source, suras, combined)
        self.assertEqual(len(pages), 610)
        self.assertEqual(len(words), combined['6236']['end_word'])
        self.assertEqual(sum(len(line.get('tokens', [])) for page in layout['pages'].values() for line in page), len(source) - 2)
        self.assertEqual(pages[-1]['to'], '114:6')
        self.assertEqual([(d['page'], d['line']) for d in layout['textDifferences']], [(378, 8), (547, 8)])
        split = [t for page in layout['pages'].values() for line in page for t in line.get('tokens', []) if t['ref'] == '2:181']
        for ref, word_id in [('2:181', 3289), ('8:6', 22614), ('13:37', 32556)]:
            tokens = [t for page in layout['pages'].values() for line in page for t in line.get('tokens', []) if t.get('wordId') == word_id]
            self.assertEqual(len(tokens), 1, ref)
            self.assertEqual(tokens[0]['text'], 'بَعْدَمَا', ref)
            self.assertEqual(words[str(word_id)], 'بَعْدَمَا', ref)
        lexical = [t for page in layout['pages'].values() for line in page for t in line.get('tokens', []) if t.get('wordId') or t.get('parts')]
        self.assertEqual(len(lexical), 77430)
        self.assertEqual([t['wordId'] for t in lexical], list(range(1, 77431)))
        self.assertTrue(all(t['text'] == words[str(t['wordId'])] for t in lexical))
        merged = [t for page in layout['pages'].values() for line in page for t in line.get('tokens', []) if t['ref'] == '37:130']
        self.assertEqual([t['text'] for t in merged[:4]], ['سَلٰمٌ', 'عَلٰۤی', 'اِلْ', 'یَاسِیْنَ'])
        self.assertEqual([t['wordId'] for t in merged[:4]], [58036, 58037, 58038, 58039])

    def fixture(self):
        words = [
            dict(id=1, surah=1, ayah=1, word=1, text='بِسْمِ'),
            dict(id=2, surah=1, ayah=1, word=2, text='اللّٰهِ'),
            dict(id=3, surah=1, ayah=1, word=3, text='۟'),
            dict(id=4, surah=1, ayah=2, word=1, text='اَلْحَمْدُ'),
            dict(id=5, surah=1, ayah=2, word=2, text='۟ۙ'),
        ]
        lines = [dict(page_number=1, line_number=1, line_type='surah_name', surah_number=1, is_centered=True),
                 dict(page_number=1, line_number=2, line_type='ayah', first_word_id=1, last_word_id=1, is_centered=True),
                 dict(page_number=2, line_number=1, line_type='ayah', first_word_id=2, last_word_id=5, is_centered=False)]
        suras = {'1': dict(start=1, nAyah=2)}
        combined = {'1': dict(start_word=1, end_word=2), '2': dict(start_word=3, end_word=3)}
        return lines, words, suras, combined

    def test_split_verse_markers_and_shared_word_ids(self):
        pages, words, layout = indian.convert(*self.fixture(), expected_pages=2)
        self.assertEqual(pages, [dict(page=1, **{'from': '1:1', 'to': '1:1'}), dict(page=2, **{'from': '1:1', 'to': '1:2'})])
        self.assertEqual(words, {'1': 'بِسْمِ', '2': 'اللّٰهِ', '3': 'اَلْحَمْدُ'})
        tokens = layout['pages']['2'][0]['tokens']
        self.assertEqual([t.get('wordId') for t in tokens], [2, None, 3, None])
        self.assertEqual(tokens[1]['text'], '۟')
        self.assertEqual(layout['pages']['1'][0]['type'], 'surah_name')

    def test_reject_missing_source_word(self):
        lines, words, suras, combined = self.fixture()
        del words[1]
        with self.assertRaises(ValueError):
            indian.convert(lines, words, suras, combined, expected_pages=2)

    def test_reject_word_count_mismatch(self):
        lines, words, suras, combined = self.fixture()
        words[1]['word'] = 7
        with self.assertRaises(ValueError):
            indian.convert(lines, words, suras, combined, expected_pages=2)

    def test_reject_duplicate_or_missing_layout_tokens(self):
        for first in [1, 3]:
            lines, words, suras, combined = self.fixture()
            lines[-1]['first_word_id'] = first
            with self.assertRaises(ValueError):
                indian.convert(lines, words, suras, combined, expected_pages=2)

    def test_reject_more_than_fifteen_lines(self):
        lines, words, suras, combined = self.fixture()
        lines[-1]['line_number'] = 16
        with self.assertRaises(ValueError):
            indian.convert(lines, words, suras, combined, expected_pages=2)


if __name__ == '__main__':
    unittest.main()
