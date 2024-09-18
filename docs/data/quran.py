import json
import re

# Define file paths
arabic_file = './uthmani.md'  # Update with actual file path
english_file = './en.md'      # Update with actual file path

# Function to count Arabic words
def count_arabic_words(text):
    # Match Arabic words using a regular expression
    arabic_words = re.findall(r'[\u0600-\u06FF]+', text)
    return len(arabic_words)

# Function to read the file and store verse numbers and text
def parse_file(filepath, file_type="text"):
    data = {}
    unprocessed_lines = []
    total_lines = 0
    key = None  # To store the verse number
    verse_text = []  # To accumulate the verse text
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            total_lines += 1
            line = line.strip()
            if line.startswith('-'):  # Detecting verse number
                if key and verse_text:  # Store the previous verse if exists
                    data[key] = ' '.join(verse_text).strip()
                key = line.strip('-').strip()  # Extract the verse number
                verse_text = []  # Reset for the next verse
            elif line:  # If it's a non-empty line, add it to the current verse
                verse_text.append(line)
            # No need to warn for cases with no associated text if the line is empty
        if key and verse_text:  # Don't forget to add the last verse
            data[key] = ' '.join(verse_text).strip()
        # Only if key is not None and we had non-empty lines that didn't process
    return data, unprocessed_lines, total_lines

# Parse both Arabic and English files
arabic_data, arabic_warnings, arabic_total_lines = parse_file(arabic_file, file_type="Arabic")
english_data, english_warnings, english_total_lines = parse_file(english_file, file_type="English")

# Combine the data based on the verse number
combined_data = {}
arabic_word_count = 0
for key in arabic_data:
    arabic_text = arabic_data.get(key, '')
    english_text = english_data.get(key, '')
    combined_data[key] = {
        'arabic': arabic_text,
        'en': english_text
    }
    # Count the Arabic words in the current verse
    arabic_word_count += count_arabic_words(arabic_text)

# Convert combined data to JSON format
combined_json = json.dumps(combined_data, ensure_ascii=False, indent=2)

# Saving combined JSON to a file
output_file_path = 'combined_quran.json'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(combined_json)

# Output statistics
total_lines_processed = arabic_total_lines + english_total_lines
warnings = arabic_warnings + english_warnings

# Print out the stats and any warnings
print(f"Combined data has been saved to {output_file_path}")
print(f"Total lines processed: {total_lines_processed}")
print(f"Total Arabic words processed: {arabic_word_count}")
if warnings:
    print("\nWarnings for unprocessed lines (non-empty):")
    for warning in warnings:
        print(warning)
else:
    print("No warnings. All lines processed successfully.")
