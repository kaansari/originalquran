import re
import json
from collections import defaultdict

# Function to process the morphology data and categorize by root
def categorize_by_root(file_path):
    root_data = defaultdict(lambda: {'count': 0, 'variations': set()})  # Initialize a dictionary to hold root info

    # Regular expression to extract ROOT information
    root_pattern = re.compile(r"ROOT:([^|]+)")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():  # Skip empty lines
                parts = line.split("\t")
                if len(parts) >= 4:
                    word = parts[1].strip()  # Word in Arabic
                    morphology = parts[3].strip()  # Morphological details
                    
                    # Extract the root(s) from the morphology if available
                    root_match = root_pattern.search(morphology)
                    if root_match:
                        roots = root_match.group(1).split("،")  # Split multiple roots if they exist
                        
                        for root in roots:
                            root = root.strip()  # Clean up any spaces
                            root_data[root]['count'] += 1  # Increment the count for this root
                            root_data[root]['variations'].add(word)  # Add the word to the variations set

    # Convert variations set to a list for JSON serialization
    for root in root_data:
        root_data[root]['variations'] = list(root_data[root]['variations'])

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
output_file = '../data/categorized_by_root.json'

# Run the script
main(input_file, output_file)
