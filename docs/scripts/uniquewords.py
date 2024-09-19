import json
import os
from collections import Counter

# Function to process the words and generate the desired JSON and report
def process_unique_words(input_file):
    # Load the input JSON file
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Get all words and count their occurrences
    words = list(data.values())
    word_counts = Counter(words)

    # Create a dictionary where the word is the key and 'count' is an attribute
    unique_words = {word: {"count": count} for word, count in word_counts.items()}

    # Create the output file name with _unique suffix
    output_file = os.path.splitext(input_file)[0] + '_unique.json'

    # Save the unique words with counts to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(unique_words, file, ensure_ascii=False, indent=2)

    # Create a report file listing the words and their frequencies
    report_file = os.path.splitext(input_file)[0] + '_report.txt'
    
    with open(report_file, 'w', encoding='utf-8') as file:
        for word, count in word_counts.items():
            file.write(f"{word}: {count}\n")

    print(f"Unique words with counts saved to: {output_file}")
    print(f"Word frequency report saved to: {report_file}")

# Example usage
if __name__ == "__main__":
    # Replace with your file path
    input_file = "quran_words.json"
    process_unique_words(input_file)

