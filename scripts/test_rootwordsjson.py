import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


class RootGeneratorTests(unittest.TestCase):
    def test_generator_reads_markdown_sources_without_changing_them(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            for folder in ['scripts', 'data/notes_dir', 'src/json']:
                (project / folder).mkdir(parents=True)
            shutil.copy2(Path(__file__).with_name('rootwordsjson.py'),
                         project / 'scripts/rootwordsjson.py')
            fixtures = {
                'data/root_notes.json': {
                    'رحم': {'source': 'notes_dir/رحم.md'},
                    'كتب': {'source': 'notes_dir/كتب.md'},
                },
                'src/json/quran_words.json': {'1': 'رحيم', '2': 'كتاب'},
                'src/json/quran_morphology.json': {
                    '1': {'id': '1:1:1', 'words': {'1:1:1:1': {'root': 'رحم'}}},
                    '2': {'id': '1:1:2', 'words': {'1:1:2:1': {'root': 'كتب'}}},
                },
            }
            for name, data in fixtures.items():
                (project / name).write_text(json.dumps(data), encoding='utf-8')
            markdown = '**A personal note**\n\nArabic رحم, "quoted text", and [a link](https://example.com).\n'
            markdown_path = project / 'data/notes_dir/رحم.md'
            markdown_path.write_text(markdown, encoding='utf-8')
            (project / 'data/notes_dir/كتب.md').write_text('   ', encoding='utf-8')
            original_source = markdown_path.read_bytes()
            original_notes = (project / 'data/root_notes.json').read_bytes()
            result = subprocess.run([sys.executable, str(project / 'scripts/rootwordsjson.py')],
                                    cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads((project / 'src/json/root_words.json').read_text())
            self.assertNotIn('Meaning', output['رحم'])
            self.assertEqual(output['رحم']['RootCount'], 1)
            self.assertEqual(output['رحم']['Word']['رحيم']['Verses'],
                             [{'Key': '1', 'ID': '1:1:1'}])
            self.assertNotIn('Meaning', output['كتب'])
            self.assertEqual(output['رحم']['Notes'], markdown)
            self.assertNotIn('Notes', output['كتب'])
            self.assertEqual(markdown_path.read_bytes(), original_source)
            self.assertEqual((project / 'data/root_notes.json').read_bytes(), original_notes)
            published_index = json.loads((project / 'src/json/root_notes.json').read_text())
            self.assertEqual(set(published_index), {'رحم'})
            self.assertEqual((project / 'src/notes/رحم.md').read_text(encoding='utf-8'), markdown)

            # Publishing notes alone must not regenerate the existing Quran index.
            output_path = project / 'src/json/root_words.json'
            previous_output = output_path.read_bytes()
            markdown_path.write_text(markdown + 'Updated note.\n', encoding='utf-8')
            result = subprocess.run([sys.executable, str(project / 'scripts/rootwordsjson.py'), '--notes-only'],
                                    cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(output_path.read_bytes(), previous_output)
            self.assertEqual((project / 'src/notes/رحم.md').read_text(encoding='utf-8'), markdown + 'Updated note.\n')

            # Invalid notes must not replace a previously generated output.
            output_path = project / 'src/json/root_words.json'
            previous_output = output_path.read_bytes()
            for invalid in [{'unknown-root': fixtures['data/root_notes.json']['رحم']},
                            {'رحم': {'source': 'notes_dir/missing.md'}},
                            {'رحم': {'source': '../outside.md'}},
                            {'رحم': {'source': '/absolute.md'}},
                            {'رحم': {'source': 123}},
                            {'رحم': [{'title': 'Incomplete note'}]}]:
                (project / 'data/root_notes.json').write_text(json.dumps(invalid))
                result = subprocess.run([sys.executable, str(project / 'scripts/rootwordsjson.py')],
                                        cwd=directory, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(output_path.read_bytes(), previous_output)


if __name__ == '__main__':
    unittest.main()
