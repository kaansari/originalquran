import json
import re

def parse_quranic_text(input_file, output_file):
    """
    Parse Quranic text file and create a JSON file with numbered words.
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path to the output JSON file
    """
    
    # Read the content from the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Clean and prepare the text
    # Remove any extra whitespace and normalize
    text = text.strip()
    
    # Split into words - using regex to split on whitespace and punctuation
    # This preserves Arabic words correctly
    words = re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', text)
    
    # Create the dictionary with numbered words
    result = {}
    for i, word in enumerate(words, start=1):
        result[str(i)] = word
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully created {output_file} with {len(words)} words.")
    return result

# Alternative version that handles the specific format better
def parse_quranic_text_enhanced(input_file, output_file):
    """
    Enhanced version that handles the specific format with more control.
    """
    
    # Read the content from the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Replace the specific ellipsis with regular dot for splitting
    text = text.replace('...', '.')
    
    # Split by whitespace and filter out empty strings
    words = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            # Split by whitespace and handle words with punctuation
            line_words = line.split()
            for word in line_words:
                # Clean each word (remove dots but keep Arabic text)
                # The dot at the end is a special Unicode character
                word = word.strip(' .،؛؟')
                if word:
                    words.append(word)
    
    # Create the dictionary with numbered words
    result = {}
    for i, word in enumerate(words, start=1):
        result[str(i)] = word
    
    # Write to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully created {output_file} with {len(words)} words.")
    
    # Print first few words for verification
    print("\nFirst 13 words from the output:")
    for i in range(1, min(14, len(words) + 1)):
        print(f'{i}: {result[str(i)]}')
    
    return result

if __name__ == "__main__":
    # Configuration
    input_filename = "../data/uthmani-warsh.txt"  # Your input file name
    output_filename = "../src/json/quranic_warsh_words.json"  # Output JSON file name
    
    # Run the parser
    try:
        # Use the enhanced version
        result = parse_quranic_text_enhanced(input_filename, output_filename)
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")
        print("Please ensure the input file exists in the same directory.")
    except Exception as e:
        print(f"An error occurred: {e}")