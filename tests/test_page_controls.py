"""Public page contracts: controls remain reachable without a settings menu."""
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
    def test_all_public_pages_have_logo_and_no_hamburger(self):
        for path in (ROOT / 'src').glob('*.html'):
            with self.subTest(page=path.name):
                elements = Markup(path.read_text()).elements
                self.assertFalse(any(a.get('id') == 'menu-toggle' or
                    {'hamburger-menu', 'header-settings'} & set(a.get('class', '').split())
                    for _, a, _ in elements))
                logos = [(a, parents) for tag, a, parents in elements
                         if tag == 'img' and 'site-logo' in a.get('class', '').split()]
                self.assertEqual(len(logos), 1)
                self.assertTrue(any(tag == 'a' and 'site-brand' in a.get('class', '').split()
                                    for tag, a in logos[0][1]))

    def test_reader_options_are_visible_once_and_keep_font_choices(self):
        choices = {
            'index.html': ['Amiri Quran', 'Raqq'],
            'simple.html': ['Qahiri', 'Amiri Quran', 'Raqq'],
            'page.html': ['Amiri Quran', 'Raqq'],
            'warsh.html': ['Amiri Quran', 'Raqq'],
            'quran.html': ['Amiri Quran', 'Raqq'],
            'root.html': None,
            'writing.html': ['Qahiri', 'Amiri Quran', 'System Arabic', 'Raqq', 'Amiri', 'Noto Naskh Arabic', 'Noto Sans Arabic'],
        }
        for filename, fonts in choices.items():
            with self.subTest(page=filename):
                text = (ROOT / 'src' / filename).read_text()
                elements = Markup(text).elements
                for identifier in ['translation-toggle'] + (['font-select'] if fonts else []):
                    matches = [(a, parents) for _, a, parents in elements if a.get('id') == identifier]
                    self.assertEqual(len(matches), 1)
                    self.assertFalse(any(tag in ('header', 'details') for tag, _ in matches[0][1]))
                    self.assertTrue(any(tag == 'label' and a.get('for') == identifier
                                        for tag, a, _ in elements))
                if fonts:
                    select = re.search(r'<select[^>]*id="font-select"[^>]*>(.*?)</select>', text, re.S)[1]
                    self.assertEqual(re.findall(r'<option value="([^"]+)"', select), fonts)

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
