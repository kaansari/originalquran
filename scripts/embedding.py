import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm  # optional, for progress bar

# --- Load your current combined_quran JSON ---
with open("../src/json/combined_quran.json", "r", encoding="utf-8") as f:
    verses = json.load(f)

# --- Load multilingual embedding model ---
# E5 large model: accurate, supports multi-language queries
model = SentenceTransformer("intfloat/multilingual-e5-large")

# --- Prepare output list ---
output = []

# --- Loop through each verse and generate embedding ---
for key, value in tqdm(verses.items(), desc="Processing verses"):
    arabic_text = value["arabic"]

    # Generate embedding (Arabic text only)
    embedding = model.encode([arabic_text], convert_to_numpy=True,batch_size=64, show_progress_bar=True)[0].tolist()

    # Append to output
    output.append({
        "key": key,
        "arabic": arabic_text,
        "embedding": embedding
    })

# --- Save final JSON ---
with open("../src/json/quran_verse_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Done! Output saved to quran_verse_embeddings.json")
