import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('markers', ROOT / 'scripts/extract_section_markers.py')
markers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(markers)


class SectionMarkerTests(unittest.TestCase):
    def test_extracts_local_boundaries_without_counting_verse_or_pause_glyphs(self):
        load = lambda name: json.loads((ROOT / 'src/json' / name).read_text(encoding='utf-8'))
        data = markers.extract(load('indian/lines.json'), load('sura.json'), load('combined_quran.json'))
        self.assertEqual(data['counts'], {'juz_end': 30, 'quarter': 30, 'half': 30, 'three_quarters': 29})
        self.assertEqual(len(data['markers']), 119)
        self.assertEqual(len(data['juzStarts']), 30)
        self.assertEqual(data['markers'][0]['verse'], '2:46')
        self.assertEqual(data['markers'][-1]['verse'], '114:6')
        missing = data['issues']
        self.assertEqual(len(missing), 1)
        self.assertEqual((missing[0]['juz'], missing[0]['kind']), (27, 'three_quarters'))
        inside = [m for m in data['markers'] if m['codePoint'] == 'U+F64F'][0]
        self.assertEqual((inside['verse'], inside['afterWordId'], inside['placement']), ('6:73', 17407, 'after_word'))
        self.assertTrue(all(1 <= m['afterWordId'] <= 77430 for m in data['markers']))
        self.assertEqual(data['juzStarts'][0], {'juz': 1, 'beforeWordId': 1})

    def test_anchors_after_verse_markers_use_the_shared_last_word(self):
        layout = {'pages': {'1': [{'number': 1, 'tokens': [
            {'ref': '1:1', 'wordId': 1, 'text': 'أ\uf64c\uf64a'},
            {'ref': '1:1', 'wordId': 2, 'text': 'ب\uf64d'},
            {'ref': '1:1', 'wordId': 3, 'text': 'ج\uf64f'},
            {'ref': '1:2', 'text': '\uf650\uf500'},
        ]}]}}
        data = markers.extract(layout, {'1': {'start': 1, 'nAyah': 2}},
                               {'1': {'start_word': 1, 'end_word': 3}, '2': {'start_word': 4, 'end_word': 5}}, expected_juz=1)
        self.assertEqual(len(data['markers']), 4)
        self.assertEqual(data['markers'][-1]['afterWordId'], 5)
        self.assertEqual(data['markers'][-1]['placement'], 'after_verse')
        self.assertEqual(data['issues'], [])


if __name__ == '__main__':
    unittest.main()
