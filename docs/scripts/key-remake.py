import json
import os

# Function to reassign keys sequentially and output to a new file
def reassign_keys_sequentially(input_file):
    # Load the input JSON file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Reassign sequential keys
    new_data = {}
    for i, value in enumerate(data.values(), start=1):
        new_data[str(i)] = value

    # Create new file path by adding _output to the file name
    output_file = os.path.splitext(input_file)[0] + '_output.json'

    # Save the new JSON file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(new_data, file, ensure_ascii=False, indent=2)

    print(f"New file saved as: {output_file}")

# Example usage
if __name__ == "__main__":
    # Replace with your file path
    input_file = "ar-hafs-pronounce.json"
    reassign_keys_sequentially(input_file)
