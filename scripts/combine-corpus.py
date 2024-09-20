import json
import re
import os

# Function to process the first file (Arabic morphology)
def process_arabic_file(file_path):
    arabic_data = {}
    current_id = 1  # Sequential id for each parent object

    # Regular expression to extract ROOT information
    root_pattern = re.compile(r"ROOT:([^|]+)")

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                parts = line.split("\t")
                if len(parts) >= 4:
                    location = parts[0].strip()  # Full location like 1:1:1:1
                    word = parts[1].strip()  # Word in Arabic
                    pos = parts[2].strip()  # Part of speech
                    morphology = parts[3].strip()  # Morphological details
                    
                    # Extract the root from the morphology if available
                    root_match = root_pattern.search(morphology)
                    root = root_match.group(1) if root_match else None
                    
                    # Split location to extract the higher-level key (1:1:1) and sub-key (1:1:1:1)
                    main_key = ":".join(location.split(":")[:3])
                    sub_key = location  # Full sequence number, like "1:1:1:1"

                    if main_key not in arabic_data:
                        arabic_data[main_key] = {
                            "id": main_key,
                            "words": {}
                        }

                    arabic_data[main_key]["words"][sub_key] = {
                        "word": word,
                        "pos": pos,
                        "root": root  # Add the root if available
                    }

    return arabic_data

# Function to process the second file (English morphology)
def process_english_file(file_path):
    english_data = {}

    # Regular expression to extract LEM information
    lemma_pattern = re.compile(r"LEM:([^|]+)")

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                parts = line.split("\t")
                if len(parts) >= 4:
                    location = parts[0].strip().strip("()")  # Location without parentheses
                    form = parts[1].strip()  # Form of the word
                    tag = parts[2].strip()  # Tag (POS)
                    features = parts[3].strip()  # Morphological features in English
                    
                    # Extract the lemma (LEM) from the features
                    lemma_match = lemma_pattern.search(features)
                    lemma = lemma_match.group(1) if lemma_match else None
                    
                    # Split location to extract the higher-level key (1:1:1) and sub-key (1:1:1:1)
                    main_key = ":".join(location.split(":")[:3])
                    sub_key = location  # Full sequence number, like "1:1:1:1"

                    if main_key not in english_data:
                        english_data[main_key] = {}

                    english_data[main_key][sub_key] = {
                        "form": form,
                        "tag": tag,
                        "lemma": lemma,  # Add the lemma field
                        "morphology_en": features  # Keep the morphology_en for reference
                    }
    return english_data

# Function to merge the two files based on location
def merge_data(arabic_data, english_data):
    merged_data = {}
    current_id = 1  # Sequential ID counter

    for parent_key, arabic_info in arabic_data.items():
        merged_data[current_id] = {
            "id": parent_key,  # Full location like 1:1:1
            "words": {}
        }
        
        for word_key, word_info in arabic_info["words"].items():
            merged_data[current_id]["words"][word_key] = {
                "word": word_info["word"],
                "pos": word_info["pos"],
                "root": word_info.get("root", "N/A"),  # Add the root attribute
                "lemma": english_data.get(parent_key, {}).get(word_key, {}).get("lemma", "N/A"),  # Add the lemma attribute
                "morphology_en": english_data.get(parent_key, {}).get(word_key, {}).get("morphology_en", "N/A")
            }
        
        current_id += 1  # Increment the ID for each parent

    return merged_data

# Main function to parse and merge the files
def main(arabic_file, english_file, output_file):
    arabic_data = process_arabic_file(arabic_file)
    english_data = process_english_file(english_file)
    
    merged_data = merge_data(arabic_data, english_data)
    
    # Save the merged data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
       json.dump(merged_data, f, ensure_ascii=False, indent=2)
        

    print(f"Merged data has been saved to {output_file}")



# Get the mode (default to 'development' if not set)
mode = os.getenv('MODE', 'deployment')

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
script_dir = os.path.dirname(os.path.dirname(__file__))

# Define the file paths for input and output
arabic_file = os.path.join(script_dir, '../data/quran-morphology.txt')
english_file = os.path.join(script_dir, '../data/quranic-corpus-morphology-0.4.txt')
output_file = os.path.join(json_output_dir, 'quran_morphology_output.json')


# Run the script
main(arabic_file, english_file, output_file)
