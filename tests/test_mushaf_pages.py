import importlib.util
import json
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('build_mushaf_pages', ROOT / 'scripts/build_mushaf_pages.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class MushafPagesTests(unittest.TestCase):
    def test_all_604_pages_cover_the_whole_quran_once(self):
        starts = json.loads((ROOT / 'data/mushaf-page-starts.json').read_text())['starts']
        surahs = json.loads((ROOT / 'src/json/sura.json').read_text())
        pages = builder.build_pages(starts, surahs)
        self.assertEqual(len(pages), 604)
        self.assertEqual(pages[0], {'page': 1, 'from': '1:1', 'to': '1:7'})
        self.assertEqual(pages[1], {'page': 2, 'from': '2:1', 'to': '2:5'})
        self.assertEqual(pages[-1], {'page': 604, 'from': '112:1', 'to': '114:6'})
        def global_id(ref):
            chapter, verse = map(int, ref.split(':'))
            self.assertTrue(1 <= verse <= surahs[str(chapter)]['nAyah'])
            return surahs[str(chapter)]['start'] + verse - 1
        next_verse = 1
        for page in pages:
            self.assertEqual(global_id(page['from']), next_verse)
            next_verse = global_id(page['to']) + 1
        self.assertEqual(next_verse, 6237)
