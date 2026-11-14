"""Public page contracts: chapter and page remain visible; secondary options are disclosed."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class Markup(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.stack = []
        self.elements = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs, list(self.stack)))
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append((tag, attrs))
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

class PageControlsTests(unittest.TestCase):
    def test_all_public_pages_have_navigation_without_branding_or_hamburger(self):
        for path in (ROOT / 'src').glob('*.html'):
            with self.subTest(page=path.name):
                elements = Markup(path.read_text()).elements
                self.assertFalse(any(a.get('id') == 'menu-toggle' or
                    {'hamburger-menu', 'header-settings'} & set(a.get('class', '').split())
                    for _, a, _ in elements))
                logos = [(a, parents) for tag, a, parents in elements
                         if tag == 'img' and 'site-logo' in a.get('class', '').split()]
                self.assertEqual(len(logos), 0)
                self.assertFalse(any('site-brand' in a.get('class', '').split() for _, a, _ in elements))
                self.assertTrue(any('site-toplinks' in a.get('class', '').split() for _, a, _ in elements))

    def test_reader_options_are_visible_once_and_keep_font_choices(self):
        choices = {
            'index.html': ['Amiri Quran', 'Raqq', 'Uthmani Hafs', 'System Arabic', 'Amiri', 'Noto Naskh Arabic', 'Noto Sans Arabic'],
            'simple.html': ['Qahiri', 'Amiri Quran', 'Raqq'],
            'page.html': ['Amiri Quran', 'Raqq', 'Uthmani Hafs', 'System Arabic', 'Amiri', 'Noto Naskh Arabic', 'Noto Sans Arabic'],
            'warsh.html': ['Amiri Quran', 'Raqq'],
            'quran.html': ['Amiri Quran', 'Raqq', 'Uthmani Hafs', 'System Arabic', 'Amiri', 'Noto Naskh Arabic', 'Noto Sans Arabic'],
            'root.html': None,
            'indian.html': ['IndoPak Nastaleeq'],
            'writing.html': ['Amiri Quran', 'System Arabic', 'Raqq', 'Amiri', 'Noto Naskh Arabic', 'Noto Sans Arabic'],
        }
        for filename, fonts in choices.items():
            with self.subTest(page=filename):
                text = (ROOT / 'src' / filename).read_text()
                elements = Markup(text).elements
                for identifier in ['translation-toggle'] + (['font-select'] if fonts else []):
                    matches = [(a, parents) for _, a, parents in elements if a.get('id') == identifier]
                    self.assertEqual(len(matches), 1)
                    self.assertFalse(any(tag == 'header' for tag, _ in matches[0][1]))
                    self.assertTrue(any(tag == 'details' and 'reader-filters' in a.get('class', '').split() for tag, a in matches[0][1]))
                    self.assertTrue(any(tag == 'label' and a.get('for') == identifier
                                        for tag, a, _ in elements))
                if fonts:
                    select = re.search(r'<select[^>]*id="font-select"[^>]*>(.*?)</select>', text, re.S)[1]
                    self.assertEqual(re.findall(r'<option value="([^"]+)"', select), fonts)

    def test_chapter_and_page_stay_outside_collapsed_filters(self):
        for name in ['index.html', 'page.html', 'warsh.html', 'simple.html', 'indian.html', 'writing.html', 'quran.html']:
            elements = Markup((ROOT / 'src' / name).read_text()).elements
            for identifier in ['sura-select', 'verse-select'] + ([] if name == 'quran.html' else ['page-number']):
                nodes = [parents for _, attrs, parents in elements if attrs.get('id') == identifier]
                self.assertEqual(len(nodes), 1, name)
                self.assertFalse(any(tag == 'details' for tag, _ in nodes[0]), name)
                if identifier == 'page-number':
                    self.assertTrue(any(attrs.get('id') == 'reader-page-heading' for _, attrs in nodes[0]), name)
            verse = [attrs for _, attrs, _ in elements if attrs.get('id') == 'verse-select'][0]
            self.assertEqual(verse.get('aria-label'), 'Verse', name)
            filters = [attrs for tag, attrs, _ in elements if tag == 'details' and 'reader-filters' in attrs.get('class', '').split()]
            self.assertEqual(len(filters), 1, name)
            self.assertNotIn('open', filters[0])

    def test_dictionary_controls_live_in_reader_toolbar_in_page_and_template(self):
        for path in [ROOT / 'src/maqayis.html', ROOT / 'src/json/maqayis_tools/maqayis.template.html']:
            elements = Markup(path.read_text()).elements
            for identifier in ['vowels', 'smaller', 'larger']:
                matches = [(a, parents) for _, a, parents in elements if a.get('id') == identifier]
                self.assertEqual(len(matches), 1)
                self.assertTrue(any('reader-toolbar' in a.get('class', '').split()
                                    for _, a in matches[0][1]))
                self.assertFalse(any(tag == 'details' for tag, _ in matches[0][1]))

if __name__ == '__main__':
    unittest.main()
