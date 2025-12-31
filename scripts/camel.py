import json
import sys
from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer

# -----------------------------
# CONFIG
# -----------------------------

# Custom root overrides (you can add more)
ROOT_OVERRIDES = {
    "الله": "لوه"
}

# Parts of speech to skip (particles, prepositions, etc.)
SKIP_POS = {
    "prep",     # prepositions (في، على...)
    "conj",     # conjunctions (و، ف...)
    "part",     # particles
    "pron",      # pronouns
    "abbrev",
    "pron_rel",
    "adv"
}

# -----------------------------
# HELPERS
# -----------------------------

def normalize_root(root):
    if not root:
        return None

    # Remove dot-separated root letters (ر.ح.م → رحم)
    root = root.replace('.', '')

    # Normalize hamza forms
    root = root.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')

    return root


# -----------------------------
# MAIN
# -----------------------------

def main(input_file, output_file):
    # Load morphology DB
    db = MorphologyDB.builtin_db('calima-msa-r13')
    analyzer = Analyzer(db)

    # Load Qur'an words JSON
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    output = {}

    for key, word in data.items():
        analyses = analyzer.analyze(word)

        if not analyses:
            continue

        # Take best analysis
        a = analyses[0]

        pos = a.get("pos")

        # Skip particles etc.
        if pos in SKIP_POS:
            continue

        # Root override
        if word in ROOT_OVERRIDES:
            root = ROOT_OVERRIDES[word]
        else:
            root = normalize_root(a.get("root"))

        output[key] = {
            "word": word,
            "root": root,
            "pos": pos,
            "diac": a.get("diac")
        }

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Done ✔ Processed {len(output)} words")


# -----------------------------
# ENTRY POINT
# -----------------------------

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python camel.py input.json output.json")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
