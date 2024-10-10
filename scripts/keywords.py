import re
import json
from collections import defaultdict

# Function to process the morphology data and categorize by ROOT and words
def categorize_by_root(file_path):
    root_data = defaultdict(lambda: {
        "total_count": 0,  # Total occurrences of the root
        "words": {}
    })

    # Regular expression to extract ROOT information
    root_pattern = re.compile(r"ROOT:([^|]+)")

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                parts = line.split("\t")
                if len(parts) >= 4:
                    key = parts[0].strip()  # Full location key, like 1:1:3:2
                    word = parts[1].strip()  # Word in Arabic
                    morphology = parts[3].strip()  # Morphological details

                    # Extract the root from the morphology
                    root_match = root_pattern.search(morphology)
                    root = root_match.group(1) if root_match else None  # Skip words with no root

                    if root:  # Only process words that have a root
                        # Increment the total count for this root
                        root_data[root]["total_count"] += 1

                        # Initialize the word entry under the root if not exists
                        if word not in root_data[root]["words"]:
                            root_data[root]["words"][word] = {
                                "count": 0,
                                "wordkeys": []
                            }

                        # Increment the count for this word
                        root_data[root]["words"][word]["count"] += 1

                        # Append the location ID (key) to the wordkeys list
                        root_data[root]["words"][word]["wordkeys"].append(key)

    return root_data

# Main function to process the file and save the output as JSON
def main(input_file, output_file):
    root_data = categorize_by_root(input_file)
    
    # Save the categorized data to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
       json.dump(root_data, f, ensure_ascii=False, indent=2)

    print(f"Root-categorized data has been saved to {output_file}")


# Define the file paths for input and output
input_file = '../data/quran-morphology.txt'  # Replace with the actual file path
output_file = '../data/root.json'

# Run the script
main(input_file, output_file)
