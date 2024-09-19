import json

# Define file paths
arabic_file = './uthmani.md'  # Update with actual file path
english_file = './en.md'      # Update with actual file path

# Function to read the file and store verse numbers and text
def parse_file(filepath):
    data = {}
    key = None  # To store the verse number
    verse_text = []  # To accumulate the verse text
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('-'):  # Detecting verse number
                if key and verse_text:  # Store the previous verse if exists
                    data[key] = ' '.join(verse_text).strip()
                key = line.strip('-').strip()  # Extract the verse number
                verse_text = []  # Reset for the next verse
            elif line:  # If it's a non-empty line, add it to the current verse
                verse_text.append(line)
        if key and verse_text:  # Don't forget to add the last verse
            data[key] = ' '.join(verse_text).strip()
    return data

# Parse both Arabic and English files
arabic_data = parse_file(arabic_file)
english_data = parse_file(english_file)

# Combine the data based on the verse number
combined_data = {}
for key in arabic_data:
    combined_data[key] = {
        'arabic': arabic_data.get(key, ''),
        'en': english_data.get(key, '')
    }

# Convert combined data to JSON format
combined_json = json.dumps(combined_data, ensure_ascii=False, indent=2)

# Saving combined JSON to a file
output_file_path = 'combined_quran.json'
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(combined_json)

# Output the path of the saved file
print(f"Combined data has been saved to {output_file_path}")
