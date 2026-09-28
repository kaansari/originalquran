import json
from collections import OrderedDict

TARGET_PAGES = 360
TOTAL_WORDS = 77430
TARGET_WORDS_PER_PAGE = TOTAL_WORDS // TARGET_PAGES  # ≈215
MAX_WORDS_PER_PAGE = TARGET_WORDS_PER_PAGE + 15      # tolerance

# -------------------------
# Load JSON files
# -------------------------
with open("sura.json", "r", encoding="utf-8") as f:
    sura_data = json.load(f)

with open("verses.json", "r", encoding="utf-8") as f:
    verse_data = json.load(f)

# -------------------------
# Build ordered ayah list
# -------------------------
# Each entry:
# {
#   surah, ayah, start_word, end_word, word_count
# }

ayahs = []

for surah_id in sorted(sura_data.keys(), key=lambda x: int(x)):
    surah = sura_data[surah_id]
    start = surah["start"]
    end = surah["end"]

    for global_ayah_id in range(start, end + 1):
        ayah = verse_data[str(global_ayah_id)]
        word_count = ayah["end_word"] - ayah["start_word"] + 1

        ayahs.append({
            "surah": int(surah_id),
            "ayah": global_ayah_id - start + 1,
            "global_ayah": global_ayah_id,
            "words": word_count
        })

# -------------------------
# Pagination logic
# -------------------------
pages = OrderedDict()

page_num = 1
page_words = 0
page_start = ayahs[0]

for ayah in ayahs:
    if page_words + ayah["words"] <= MAX_WORDS_PER_PAGE:
        page_words += ayah["words"]
    else:
        pages[page_num] = {
            "start": page_start,
            "end": prev_ayah,
            "words": page_words
        }
        page_num += 1
        page_start = ayah
        page_words = ayah["words"]

    prev_ayah = ayah

# last page
pages[page_num] = {
    "start": page_start,
    "end": prev_ayah,
    "words": page_words
}

# -------------------------
# Output pagination map
# -------------------------
output = []

for page, data in pages.items():
    output.append({
        "page": page,
        "from": f'{data["start"]["surah"]}:{data["start"]["ayah"]}',
        "to": f'{data["end"]["surah"]}:{data["end"]["ayah"]}',
        "word_count": data["words"]
    })

with open("pagination_map.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Pagination complete: {len(pages)} pages created.")
