import json
import re
import os

# Function to process the Arabic morphology file
def process_arabic_file(file_path):
    arabic_data = {}
    current_id = 1  # Sequential id for each parent object

    # Regular expressions to extract ROOT and LEM information
    root_pattern = re.compile(r"ROOT:([^|]+)")
    lemma_pattern = re.compile(r"LEM:([^|]+)")

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

                    # Extract the lemma from the morphology if available
                    lemma_match = lemma_pattern.search(morphology)
                    lemma = lemma_match.group(1) if lemma_match else None

                    # Remove ROOT and LEM from the morphology string
                    morphology_cleaned = re.sub(r"ROOT:[^|]+\|?", "", morphology)  # Remove ROOT
                    morphology_cleaned = re.sub(r"LEM:[^|]+\|?", "", morphology_cleaned)  # Remove LEM
                    morphology_cleaned = morphology_cleaned.strip("|")  # Clean up any trailing pipes

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
                        "root": root,  # Add the root if available
                        "lemma": lemma,  # Add the lemma if available
                        "morphology": morphology_cleaned  # Add cleaned morphology
                    }

    return arabic_data

# Function to merge the data (Arabic-only)
def merge_data(arabic_data):
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
                "lemma": word_info.get("lemma", "N/A"),  # Add the lemma attribute
                "morphology": word_info.get("morphology", "N/A")  # Use cleaned morphology from the Arabic file
            }
        
        current_id += 1  # Increment the ID for each parent

    return merged_data

# Main function to parse and merge the files
def main(arabic_file, output_file):
    arabic_data = process_arabic_file(arabic_file)
    
    merged_data = merge_data(arabic_data)
    
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
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script dir {script_dir}")
print(f"json output dir {json_output_dir}")

# Define the file paths for input and output
arabic_file = os.path.join(script_dir, '../data/quran-morphology.txt')
output_file = os.path.join(json_output_dir, 'quran_morphology.json')

# Run the script
main(arabic_file, output_file)
