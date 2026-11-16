import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('sections', ROOT / 'scripts/build_quran_sections.py')
sections = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sections)


class QuranSectionsTests(unittest.TestCase):
    def test_export_preserves_all_boundaries_and_adds_merge_keys(self):
        load = lambda name: json.loads((ROOT / 'src/json' / name).read_text(encoding='utf-8'))
        source, suras, combined = load('section_markers.json'), load('sura.json'), load('combined_quran.json')
        data = sections.build(source, suras, combined)
        self.assertEqual(len(data['chapters']), 114)
        self.assertEqual(len(data['juz']), 30)
        self.assertEqual(len(data['markers']), 119)
        self.assertEqual(data['chapters']['1']['start_word'], 1)
        self.assertEqual(data['chapters']['114']['end_word'], 77430)
        self.assertEqual(data['chapters']['2']['juz'], [1, 2, 3])
        self.assertEqual(data['juz']['1']['from'], '1:1')
        self.assertEqual(data['juz']['1']['to'], '2:141')
        self.assertEqual(data['juz']['30']['to'], '114:6')
        previous = 0
        for number in range(1, 31):
            record = data['juz'][str(number)]
            self.assertEqual(record['start_word'], previous + 1)
            previous = record['end_word']
        self.assertEqual(previous, 77430)
        for original, exported in zip(source['markers'], data['markers']):
            self.assertEqual(exported['wordId'], original['afterWordId'])
            self.assertEqual(exported['verseKey'], original['verse'])
            meta = combined[str(exported['verseId'])]
            self.assertEqual(exported['wordId'], meta['start_word'] + exported['word'] - 1)
        inside = [m for m in data['markers'] if m['codePoint'] == 'U+F64F'][0]
        self.assertEqual((inside['sura'], inside['verse'], inside['wordId'], inside['placement']),
                         (6, 73, 17407, 'after_word'))
        self.assertEqual(data['issues'], source['issues'])
        self.assertEqual(data['convention'], source['convention'])


if __name__ == '__main__':
    unittest.main()
