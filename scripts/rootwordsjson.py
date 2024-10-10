import json
import csv

# Load Quran words JSON file
with open('../src/json/quran_words.json', 'r', encoding='utf-8') as f:
    quran_words = json.load(f)

# Load the main JSON file (the one with roots)
with open('../src/json/quran_morphology.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Dictionary to hold the output structure
output_data = {}

# Loop through the data
for key, item in data.items():
    id_value = item["id"]
    for word_key, word_info in item["words"].items():
        root = word_info.get("root")
        if root:
            word = quran_words.get(key, "")  # Get the word from quran_words.json using the key
            
            # Initialize root in output_data if not already present
            if root not in output_data:
                output_data[root] = {
                    "Word": {},
                    "RootCount": 0
                }

            # Initialize word in the corresponding root if not already present
            if word not in output_data[root]["Word"]:
                output_data[root]["Word"][word] = {
                    "Verses": [],
                    "WordCount": 0
                }

            # Append the key-ID pair and update counts
            output_data[root]["Word"][word]["Verses"].append({"Key": key, "ID": id_value})
            output_data[root]["Word"][word]["WordCount"] += 1
            output_data[root]["RootCount"] += 1

# Count the total number of verses for each word
for root in output_data:
    for word in output_data[root]["Word"]:
        output_data[root]["Word"][word]["VerseCount"] = len(output_data[root]["Word"][word]["Verses"])

# Output JSON file
output_json = '../src/json/root_words.json'

# Save the output to a JSON file
with open(output_json, 'w', encoding='utf-8') as jsonfile:
    json.dump(output_data, jsonfile, ensure_ascii=False, indent=4)

print(f"JSON file has been saved to {output_json}")

# Create a CSV report
report_file = '../data/reports/root_word_report.txt'

# Open the report file for writing
with open(report_file, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header
    csvwriter.writerow(['Root', 'Word', 'Count'])

    # Write the data
    for root, details in output_data.items():
        for word, word_details in details["Word"].items():
            word_count = word_details["WordCount"]
            csvwriter.writerow([root, word, word_count])

print(f"CSV report has been saved to {report_file}")
