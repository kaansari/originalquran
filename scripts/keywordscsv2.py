import csv
import json

# Load Quran words JSON file
with open('../src/json/quran_words.json', 'r', encoding='utf-8') as f:
    quran_words = json.load(f)

# Load the main JSON file (the one with roots)
with open('../src/json/quran_morphology.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# CSV output file
output_csv = 'output_with_words.csv'

# Open the CSV file for writing
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow(['Key', 'ID', 'Root', 'Word'])

    # Loop through the data
    for key, item in data.items():
        id_value = item["id"]
        for word_key, word_info in item["words"].items():
            root = word_info.get("root")
            if root:
                word = quran_words.get(key, "")  # Get the word from quran_words.json using the key
                csvwriter.writerow([key, word_key, word, root])

print(f"CSV file has been saved to {output_csv}")
