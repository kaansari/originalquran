import json
import csv

# Function to extract key, id, and root from the JSON data
def extract_root_data(json_data):
    root_data = []
    
    for key, value in json_data.items():
        # Loop through each word object under "words"
        for word_key, word_info in value['words'].items():
            root = word_info.get('root')
            if root:  # Only include entries that have a root
                root_data.append([key, value['id'], root])
    
    return root_data

# Function to write the extracted root data to a CSV file
def write_to_csv(root_data, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['Key', 'ID', 'Root'])
        # Write data rows
        writer.writerows(root_data)

# Main function to process the JSON and generate the CSV
def main(input_json_file, output_csv_file):
    # Load JSON data
    with open(input_json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Extract key, id, and root data
    root_data = extract_root_data(json_data)

    # Write to CSV
    write_to_csv(root_data, output_csv_file)

    print(f"Data has been written to {output_csv_file}")

# Define file paths
input_json_file = '../src/json/quran_morphology.json'  # Replace with your actual JSON file path
output_csv_file = '../data/root.csv'      # Output CSV file path



# Run the script
main(input_json_file, output_csv_file)
