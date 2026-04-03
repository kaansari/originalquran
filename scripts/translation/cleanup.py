import json
import re
from collections import OrderedDict

INPUT_FILE = "unique_word_translations.json"
OUTPUT_FILE = "unique_word_translations_cleaned.json"

# Set to True if you want more aggressive deduplication.
# Example: "(of) the prayer" and "(to) the prayer" may collapse closer to "prayer"
AGGRESSIVE_MODE = True


def normalize_spaces(text: str) -> str:
    """Collapse repeated whitespace and trim."""
    return re.sub(r"\s+", " ", text).strip()


def normalize_basic(text: str) -> str:
    """
    Conservative normalization for duplicate detection.
    Keeps meaning mostly intact.
    """
    text = text.strip().lower()

    # Normalize curly quotes/apostrophes if any
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')

    # Collapse spaces
    text = normalize_spaces(text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    # Strip outer punctuation/spaces only
    text = text.strip(" \t\n\r\"'.,;:!?-")

    return text


def strip_parenthetical_tokens(text: str) -> str:
    """
    Removes parenthetical helper words like:
    '(of) the prayer' -> 'the prayer'
    '(to) the prayer' -> 'the prayer'
    """
    text = re.sub(r"\([^)]*\)", "", text)
    return normalize_spaces(text)


def simplify_articles(text: str) -> str:
    """
    Optional stronger simplification:
    'the prayer' -> 'prayer'
    """
    text = re.sub(r"^(the|a|an)\s+", "", text, flags=re.IGNORECASE)
    return normalize_spaces(text)


def aggressive_key(text: str) -> str:
    """
    Stronger normalization key for redundancy detection.
    """
    text = normalize_basic(text)
    text = strip_parenthetical_tokens(text)
    text = simplify_articles(text)
    return text


def conservative_key(text: str) -> str:
    """
    Safer normalization key for duplicate detection.
    """
    text = normalize_basic(text)

    # Normalize parentheses spacing only, but keep content
    text = re.sub(r"\(\s*", "(", text)
    text = re.sub(r"\s*\)", ")", text)

    return text


def choose_best_variant(existing: str, candidate: str) -> str:
    """
    When two entries normalize to the same key,
    prefer the cleaner / simpler display form.
    """
    e = normalize_spaces(existing.strip())
    c = normalize_spaces(candidate.strip())

    # Prefer fewer weird wrappers / punctuation
    e_score = score_translation(e)
    c_score = score_translation(c)

    return c if c_score < e_score else e


def score_translation(text: str) -> tuple:
    """
    Lower score = better / cleaner.
    """
    lowered = text.lower()
    parenthetical_count = lowered.count("(")
    punctuation_noise = len(re.findall(r"[\"']", lowered))
    length = len(lowered)
    starts_with_article = 1 if re.match(r"^(the|a|an)\s+", lowered) else 0

    # Prefer:
    # - fewer parentheses
    # - fewer quotes
    # - shorter strings
    # - slightly prefer no leading article
    return (parenthetical_count, punctuation_noise, starts_with_article, length)


def clean_translations(translations):
    """
    Clean and deduplicate one translations list.
    """
    if not isinstance(translations, list):
        return []

    seen = OrderedDict()

    for raw in translations:
        if not isinstance(raw, str):
            continue

        cleaned_display = normalize_spaces(raw)
        if not cleaned_display:
            continue

        key = aggressive_key(cleaned_display) if AGGRESSIVE_MODE else conservative_key(cleaned_display)

        if not key:
            continue

        if key in seen:
            seen[key] = choose_best_variant(seen[key], cleaned_display)
        else:
            seen[key] = cleaned_display

    # Optional second-pass redundancy removal
    # In aggressive mode, remove entries that are basically the same except wrappers/articles
    if AGGRESSIVE_MODE:
        final_seen = OrderedDict()
        for item in seen.values():
            k = aggressive_key(item)
            if k in final_seen:
                final_seen[k] = choose_best_variant(final_seen[k], item)
            else:
                final_seen[k] = item
        return list(final_seen.values())

    return list(seen.values())


def clean_json(data):
    """
    Process the whole JSON structure.
    Expected shape:
    {
      "الصلوة": {
        "count": 58,
        "translations": [...]
      },
      ...
    }
    """
    if not isinstance(data, dict):
        raise ValueError("Top-level JSON must be an object/dictionary.")

    cleaned = {}
    total_before = 0
    total_after = 0

    for word, entry in data.items():
        if not isinstance(entry, dict):
            cleaned[word] = entry
            continue

        new_entry = dict(entry)

        translations = entry.get("translations", [])
        if isinstance(translations, list):
            total_before += len(translations)
            cleaned_translations = clean_translations(translations)
            total_after += len(cleaned_translations)
            new_entry["translations"] = cleaned_translations

        cleaned[word] = new_entry

    return cleaned, total_before, total_after


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data, total_before, total_after = clean_json(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print(f"Done.")
    print(f"Input file : {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Total translations before: {total_before}")
    print(f"Total translations after : {total_after}")
    print(f"Removed                  : {total_before - total_after}")
    print(f"AGGRESSIVE_MODE          : {AGGRESSIVE_MODE}")


if __name__ == "__main__":
    main()