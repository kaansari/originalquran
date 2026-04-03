import json
import os
from openai import OpenAI

# ================= CONFIG =================
SIMULATION_MODE = True      # True = print payload only, False = call API
BATCH_SIZE = 25

SURA_FILE = "../../src/json/sura.json"
COMBINED_QURAN_FILE = "../../src/json/combined_quran.json"
QURAN_WORDS_FILE = "../../src/json/quran_words.json"
UNIQUE_WORD_TRANSLATIONS_FILE = "unique_word_translations.json"
OUTPUT_FILE = "output.json"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# ================= HELPERS =================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_input(user_input):
    if ":" not in user_input:
        raise ValueError("Use format like 1:1-7 or 2:255")

    sura_part, ayah_part = user_input.split(":")
    sura_number = int(sura_part)

    if "-" in ayah_part:
        start_ayah, end_ayah = map(int, ayah_part.split("-"))
    else:
        start_ayah = end_ayah = int(ayah_part)

    if start_ayah > end_ayah:
        raise ValueError("Start ayah cannot be greater than end ayah")

    return sura_number, start_ayah, end_ayah


def chunk_list(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def get_words_from_quran_words(quran_words, start_word, end_word):
    words = []
    for i in range(start_word, end_word + 1):
        key = str(i)
        if key not in quran_words:
            raise ValueError(f"Word index {i} not found in quran_words.json")
        words.append(quran_words[key].strip())
    return words


def build_canonical(batch, unique_map):
    canonical = {}

    for verse in batch:
        for word in verse["words"]:
            if word not in canonical:
                entry = unique_map.get(word, {"translations": []})
                canonical[word] = entry.get("translations", [])

    return canonical


# ================= AI =================

def translate_batch_with_canonical(
    sura_number,
    sura_name,
    batch_number,
    canonical,
    verses_payload,
    previous_translations
):
    system_prompt = """
STRICT MODE.

You are producing restricted English renderings of Quran verses.

HARD RULES:
1. Use ONLY the translation options provided in CANONICAL.
2. Each Arabic word in a verse must be interpreted only through CANONICAL[word].
3. If CANONICAL[word] has one option, that option is fixed.
4. If CANONICAL[word] has multiple options, choose only from those listed options.
5. Do NOT invent any new lexical meaning.
6. Do NOT paraphrase beyond the provided options.
7. You may do only minimal English cleanup:
   - slight reordering
   - capitalization
   - punctuation
   - tiny grammatical filler only when absolutely necessary
8. Keep consistency across the whole batch.
9. Return valid JSON only.

Return exactly:
{
  "translations": [
    {
      "verse_number_in_sura": 1,
      "ayah_global": 1,
      "restricted_translation": "...",
      "notes": ["...", "..."]
    }
  ]
}
""".strip()

    payload = {
        "sura_number": sura_number,
        "sura_name": sura_name,
        "batch_number": batch_number,
        "previous_translations": previous_translations,
        "CANONICAL": canonical,
        "verses": verses_payload
    }

    if SIMULATION_MODE:
        print("\n================= API REQUEST =================")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("==============================================\n")

        return {
            "translations": [
                {
                    "verse_number_in_sura": v["verse_number_in_sura"],
                    "ayah_global": v["ayah_global"],
                    "restricted_translation": "[SIMULATED]",
                    "notes": ["simulation mode - no API call made"]
                }
                for v in verses_payload
            ]
        }

    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
        ]
    )

    text = response.output_text.strip()

    try:
        parsed = json.loads(text)
    except Exception:
        parsed = {
            "translations": [
                {
                    "verse_number_in_sura": v["verse_number_in_sura"],
                    "ayah_global": v["ayah_global"],
                    "restricted_translation": text,
                    "notes": ["model did not return valid JSON"]
                }
                for v in verses_payload
            ]
        }

    if "translations" not in parsed or not isinstance(parsed["translations"], list):
        raise ValueError("Model response missing 'translations' array")

    return parsed


# ================= MAIN =================

def main():
    user_input = input("Enter (e.g. 1:1-7 or 2:255): ").strip()

    sura_number, start_ayah_in_sura, end_ayah_in_sura = parse_input(user_input)

    sura_data = load_json(SURA_FILE)
    combined = load_json(COMBINED_QURAN_FILE)
    quran_words = load_json(QURAN_WORDS_FILE)
    unique_map = load_json(UNIQUE_WORD_TRANSLATIONS_FILE)

    sura_key = str(sura_number)
    if sura_key not in sura_data:
        raise ValueError(f"Sura {sura_number} not found in sura.json")

    sura_info = sura_data[sura_key]
    sura_name = sura_info["name"]
    n_ayah = sura_info["nAyah"]
    sura_start_global = sura_info["start"]

    if start_ayah_in_sura < 1 or end_ayah_in_sura > n_ayah:
        raise ValueError(
            f"Sura {sura_number} has {n_ayah} ayahs. "
            f"You requested {start_ayah_in_sura}-{end_ayah_in_sura}."
        )

    global_start = sura_start_global + (start_ayah_in_sura - 1)
    global_end = sura_start_global + (end_ayah_in_sura - 1)

    prepared_verses = []

    for verse_number_in_sura, ayah_global in enumerate(
        range(global_start, global_end + 1),
        start=start_ayah_in_sura
    ):
        ayah_key = str(ayah_global)
        if ayah_key not in combined:
            raise ValueError(f"Ayah {ayah_global} not found in combined_quran.json")

        verse = combined[ayah_key]

        words = get_words_from_quran_words(
            quran_words,
            verse["start_word"],
            verse["end_word"]
        )

        prepared_verses.append({
            "verse_number_in_sura": verse_number_in_sura,
            "ayah_global": ayah_global,
            "arabic": verse["arabic"],
            "start_word": verse["start_word"],
            "end_word": verse["end_word"],
            "words": words
        })

    output = {
        "sura": sura_number,
        "name": sura_name,
        "start_ayah_in_sura": start_ayah_in_sura,
        "end_ayah_in_sura": end_ayah_in_sura,
        "global_start": global_start,
        "global_end": global_end,
        "batch_size": BATCH_SIZE,
        "verses": []
    }

    previous_translations = []

    for batch_number, batch in enumerate(chunk_list(prepared_verses, BATCH_SIZE), start=1):
        canonical = build_canonical(batch, unique_map)

        verses_payload = []
        for verse in batch:
            verses_payload.append({
                "verse_number_in_sura": verse["verse_number_in_sura"],
                "ayah_global": verse["ayah_global"],
                "words": verse["words"]
            })

        result = translate_batch_with_canonical(
            sura_number=sura_number,
            sura_name=sura_name,
            batch_number=batch_number,
            canonical=canonical,
            verses_payload=verses_payload,
            previous_translations=previous_translations
        )

        translations_by_ayah = {
            item["ayah_global"]: item for item in result["translations"]
        }

        for verse in batch:
            item = translations_by_ayah.get(verse["ayah_global"], {})
            restricted_translation = item.get("restricted_translation", "")
            notes = item.get("notes", [])

            output["verses"].append({
                "verse_number_in_sura": verse["verse_number_in_sura"],
                "ayah_global": verse["ayah_global"],
                "arabic": verse["arabic"],
                "start_word": verse["start_word"],
                "end_word": verse["end_word"],
                "words": verse["words"],
                "translation": restricted_translation,
                "notes": notes
            })

            previous_translations.append({
                "verse_number_in_sura": verse["verse_number_in_sura"],
                "ayah_global": verse["ayah_global"],
                "translation": restricted_translation
            })

        print(f"Processed batch {batch_number} with {len(batch)} verse(s)")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()