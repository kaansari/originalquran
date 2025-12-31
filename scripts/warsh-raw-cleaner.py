import re
import sys

def process_quran(input_file, output_file):
    # Arabic-Indic digits range: ٠١٢٣٤٥٦٧٨٩
    verse_number_pattern = re.compile(r'\s*[\u0660-\u0669]+\s*')

    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Split by verse numbers
    verses = verse_number_pattern.split(text)

    # Clean and keep non-empty verses
    verses = [v.strip() for v in verses if v.strip()]

    with open(output_file, 'w', encoding='utf-8') as f:
        for verse in verses:
            f.write(verse + '\n')

    print(f"Done. Total verses written: {len(verses)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process_quran.py input.txt output.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    process_quran(input_file, output_file)
