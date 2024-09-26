import json
import os



# Get the mode (default to 'development' if not set)
mode = os.getenv('MODE', 'development')

# Set the directories based on the mode
if mode == 'development':
    json_output_dir = os.path.join(os.path.dirname(__file__), '../src/json')
elif mode == 'deployment':
    json_output_dir = os.path.join(os.path.dirname(__file__), '../build/json')
else:
    raise ValueError(f"Unknown MODE: {mode}")

# Ensure the output directory exists
os.makedirs(json_output_dir, exist_ok=True)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))


# Define the file paths for input 
arabic_file = os.path.join(script_dir, '../data/arabic.md')
english_file = os.path.join(script_dir, '../data/en.md')

#Define thte file paths for the output files
combined_output_file_path = os.path.join(json_output_dir, 'combined_quran.json')
words_output_file_path = os.path.join(json_output_dir, 'quran_words.json')





# Function to read the file and store verse numbers and text
def parse_file(filepath):
    data = {}
    key = None  # To store the verse number
    verse_text = []  # To accumulate the verse text
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#'):  # Detecting verse number
                if key and verse_text:  # Store the previous verse if exists
                    data[key] = ' '.join(verse_text).strip()
                key = line.strip('#').strip()  # Extract the verse number
                verse_text = []  # Reset for the next verse
            elif line:  # If it's a non-empty line, add it to the current verse
                verse_text.append(line)
        if key and verse_text:  # Don't forget to add the last verse
            data[key] = ' '.join(verse_text).strip()
    return data

# Function to parse Arabic words and track start/end indices
def parse_words(verses_data):
    word_map = {}
    combined_data_with_indices = {}
    word_index = 1

    # Iterate over each verse
    for verse_key, verse_text in verses_data.items():
        words = verse_text.split()  # Split the verse into words
        start_word_index = word_index
        end_word_index = word_index + len(words) - 1

        # Add each word to the word map with its index
        for word in words:
            word_map[str(word_index)] = word
            word_index += 1

        # Add the verse along with start and end word indices
        combined_data_with_indices[verse_key] = {
            "arabic": verse_text,
            "start_word": start_word_index,
            "end_word": end_word_index
        }

    return combined_data_with_indices, word_map

# Parse both Arabic and English files
arabic_data = parse_file(arabic_file)
english_data = parse_file(english_file)

# Parse the Arabic words and get start and end word indices
combined_arabic_data, words_data = parse_words(arabic_data)

# Combine the data based on the verse number (Arabic and English)
combined_data = {}
for key in combined_arabic_data:
    combined_data[key] = {
        'arabic': combined_arabic_data.get(key, {}).get('arabic', ''),
        'en': english_data.get(key, ''),
        'start_word': combined_arabic_data.get(key, {}).get('start_word', 0),
        'end_word': combined_arabic_data.get(key, {}).get('end_word', 0)
    }

# Convert combined data to JSON format
combined_json = json.dumps(combined_data, ensure_ascii=False, indent=2)

# Convert words data to JSON format
words_json = json.dumps(words_data, ensure_ascii=False, indent=2)





with open(combined_output_file_path, 'w', encoding='utf-8') as output_file:
    output_file.write(combined_json)

# Saving the words data to a separate file

with open(words_output_file_path, 'w', encoding='utf-8') as words_file:
    words_file.write(words_json)

# Output the paths of the saved files
print(f"Combined data has been saved to {combined_output_file_path}")
print(f"Words data has been saved to {words_output_file_path}")
