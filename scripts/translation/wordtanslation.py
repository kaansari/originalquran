import json
from collections import defaultdict

ARABIC_FILE = "../../src/json/quran_words.json"
ENGLISH_FILE = "../../src/json/en-word.json"
OUTPUT_FILE = "unique_word_translations.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(word):
    return word.strip()


def build_unique_translation_map(arabic_data, english_data):
    result = defaultdict(lambda: {"translations": set(), "count": 0})

    keys = sorted(arabic_data.keys(), key=lambda x: int(x))

    for key in keys:
        arabic_word = normalize(arabic_data.get(key, ""))
        english_word = english_data.get(key, "").strip()

        if not arabic_word:
            continue

        # IMPORTANT: arabic_word is used directly as key
        result[arabic_word]["count"] += 1

        if english_word:
            result[arabic_word]["translations"].add(english_word)

    # Convert to final JSON-safe structure
    final_result = {}
    for arabic_word in result:
        final_result[arabic_word] = {
            "count": result[arabic_word]["count"],
            "translations": list(result[arabic_word]["translations"])
        }

    return final_result


def main():
    arabic_data = load_json(ARABIC_FILE)
    english_data = load_json(ENGLISH_FILE)

    unique_map = build_unique_translation_map(arabic_data, english_data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_map, f, ensure_ascii=False, indent=2)

    print("Done.")


if __name__ == "__main__":
    main()