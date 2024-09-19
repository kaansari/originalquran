import re
import json

def process_file(input_file, output_file):
    # Initialize an empty dictionary to store words with their indices
    word_map = {}
    word_index = 1

    # Regular expression to remove numbers, dashes, and extra newlines
    pattern = re.compile(r'[0-9\-]+|\n')

    # Open the file and read lines
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        # Iterate through each line
        for line in lines:
            # Remove numbers, dashes, and newlines
            clean_line = pattern.sub('', line)
            
            # Split the clean line into words
            words = clean_line.split()

            # Add each word to the dictionary with its index
            for word in words:
                word_map[str(word_index)] = word
                word_index += 1

    # Convert the dictionary to JSON format
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(word_map, json_file, ensure_ascii=False, indent=2)

    print(f"Words have been parsed and saved to {output_file}")

# Example usage
process_file('uthmani-tanzil.md', 'word-harakat.json')
