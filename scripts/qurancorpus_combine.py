import json
import re

# Function to process the first file (Arabic morphology)
def process_arabic_file(file_path):
    arabic_data = {}
    current_id = 1

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
                    sub_key = location

                    if main_key not in arabic_data:
                        arabic_data[main_key] = {
                            "id": current_id,
                            "words": {}
                        }
                        current_id += 1

                    arabic_data[main_key]["words"][sub_key] = {
                        "word": word,
                        "pos": pos,
                        "morphology": morphology,
                        "root": root  # Add the root if available
                    }
    return arabic_data

# Function to process the second file (English morphology)
def process_english_file(file_path):
    english_data = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                parts = line.split("\t")
                if len(parts) >= 4:
                    location = parts[0].strip().strip("()")  # Location without parentheses
                    form = parts[1].strip()  # Form of the word
                    tag = parts[2].strip()  # Tag (POS)
                    features = parts[3].strip()  # Morphological features in English
                    
                    # Split location to extract the higher-level key (1:1:1) and sub-key (1:1:1:1)
                    main_key = ":".join(location.split(":")[:3])
                    sub_key = location

                    if main_key not in english_data:
                        english_data[main_key] = {}

                    english_data[main_key][sub_key] = {
                        "form": form,
                        "tag": tag,
                        "morphology_en": features
                    }
    return english_data

# Function to merge the two files based on location
def merge_data(arabic_data, english_data):
    merged_data = {}

    for main_key, arabic_info in arabic_data.items():
        merged_data[main_key] = {
            "id": arabic_info["id"],
            "words": {}
        }
        
        for sub_key, word_info in arabic_info["words"].items():
            merged_data[main_key]["words"][sub_key] = {
                "word": word_info["word"],
                "pos": word_info["pos"],
                "morphology": word_info["morphology"],
                "root": word_info.get("root", "N/A"),  # Add the root attribute
                "morphology_en": english_data.get(main_key, {}).get(sub_key, {}).get("morphology_en", "N/A")
            }

    return merged_data

# Main function to parse and merge the files
def main(arabic_file, english_file, output_file):
    arabic_data = process_arabic_file(arabic_file)
   # english_data = process_english_file(english_file)
    
   # merged_data = merge_data(arabic_data, english_data)
    
    # Save the merged data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(arabic_data, f, ensure_ascii=False, indent=2)

    print(f"Merged data has been saved to {output_file}")

# File paths (update with your actual file path)
arabic_file = 'quran-morphology.txt'
english_file = 'quranic-corpus-morphology-0.4.txt'
output_file = 'quran_morphology_output.json'

# Run the script
main(arabic_file, english_file, output_file)
