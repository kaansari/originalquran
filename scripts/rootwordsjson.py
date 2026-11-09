import json
import csv
import argparse
from pathlib import Path
from urllib.parse import quote

parser = argparse.ArgumentParser(description='Generate the root index and publish Markdown notes.')
parser.add_argument('--notes-only', action='store_true', help='Publish notes without rewriting root_words.json or the CSV report')
args = parser.parse_args()

project_dir = Path(__file__).resolve().parent.parent

# Markdown sources are relative to the note index, independent of the working directory.
notes_path = project_dir / 'data/root_notes.json'
root_notes = json.loads(notes_path.read_text(encoding='utf-8')) if notes_path.exists() else {}
if not isinstance(root_notes, dict):
    raise ValueError('root_notes.json must contain an object keyed by root')
note_contents = {}
for root, entry in root_notes.items():
    if not isinstance(entry, dict) or not isinstance(entry.get('source'), str) or not entry['source'].strip():
        raise ValueError(f'Notes for root {root!r} must specify a Markdown source path')
    source = Path(entry['source'])
    if source.is_absolute() or source.suffix != '.md':
        raise ValueError(f'Notes for root {root!r} must use a relative .md path')
    source = (notes_path.parent / source).resolve()
    try:
        source.relative_to(notes_path.parent.resolve())
    except ValueError:
        raise ValueError(f'Notes for root {root!r} must stay inside the data directory')
    note_contents[root] = source.read_text(encoding='utf-8')

# Load Quran words JSON file
with open(project_dir / 'src/json/quran_words.json', 'r', encoding='utf-8') as f:
    quran_words = json.load(f)

# Load the main JSON file (the one with roots)
with open(project_dir / 'src/json/quran_morphology.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Dictionary to hold the output structure
output_data = {}

# Loop through the data
for key, item in data.items():
    id_value = item["id"]
    for word_key, word_info in item["words"].items():
        root = word_info.get("root")
        if root:
            word = quran_words.get(key, "")  # Get the word from quran_words.json using the key
            
            # Initialize root in output_data if not already present
            if root not in output_data:
                output_data[root] = {
                    "Word": {},
                    "RootCount": 0
                }

            # Initialize word in the corresponding root if not already present
            if word not in output_data[root]["Word"]:
                output_data[root]["Word"][word] = {
                    "Verses": [],
                    "WordCount": 0
                }

            # Append the key-ID pair and update counts
            output_data[root]["Word"][word]["Verses"].append({"Key": key, "ID": id_value})
            output_data[root]["Word"][word]["WordCount"] += 1
            output_data[root]["RootCount"] += 1

# Count the total number of verses for each word
for root in output_data:
    for word in output_data[root]["Word"]:
        output_data[root]["Word"][word]["VerseCount"] = len(output_data[root]["Word"][word]["Verses"])

# Reject misspelled roots before replacing the generated file.
unknown_note_roots = root_notes.keys() - output_data.keys()
if unknown_note_roots:
    raise ValueError(f'Unknown roots in root_notes.json: {sorted(unknown_note_roots)}')

for root, notes in note_contents.items():
    if notes.strip():
        output_data[root]['Notes'] = notes

# Only src/ is deployed. Publish notes and a small index for morphology links.
published_notes = project_dir / 'src/notes'
published_notes.mkdir(parents=True, exist_ok=True)
note_index = {}
for root, notes in note_contents.items():
    if notes.strip():
        (published_notes / f'{root}.md').write_text(notes, encoding='utf-8')
        note_index[root] = {'source': f'notes/{quote(root, safe="")}.md'}
with open(project_dir / 'src/json/root_notes.json', 'w', encoding='utf-8') as f:
    json.dump(note_index, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'Published {len(note_index)} root notes')
if args.notes_only:
    raise SystemExit(0)

# Output JSON file
output_json = project_dir / 'src/json/root_words.json'

# Save the output to a JSON file
with open(output_json, 'w', encoding='utf-8') as jsonfile:
    json.dump(output_data, jsonfile, ensure_ascii=False, indent=4)

print(f"JSON file has been saved to {output_json}")

# Create a CSV report
report_file = project_dir / 'data/reports/root_word_report.txt'
report_file.parent.mkdir(parents=True, exist_ok=True)

# Open the report file for writing
with open(report_file, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow(['Root', 'Word', 'Count'])

    # Write the data
    for root, details in output_data.items():
        for word, word_details in details["Word"].items():
            word_count = word_details["WordCount"]
            csvwriter.writerow([root, word, word_count])

print(f"CSV report has been saved to {report_file}")
