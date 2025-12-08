import json
import chromadb
from chromadb.config import Settings

# Load your file
with open("../../src/json/quran_embeds.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Initialize Chroma (local folder: ./quran_db)
client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                  persist_directory="./quran_db"))

# Create a collection
collection = client.get_or_create_collection(
    name="quran",
    embedding_function=None  # we already have embeddings
)

ids = []
embeds = []
metadatas = []

for verse_id, info in data.items():
    ids.append(verse_id)
    embeds.append(info["embedding"])
    metadatas.append({"arabic": info["arabic"]})

# Insert data
collection.add(
    ids=ids,
    embeddings=embeds,
    metadatas=metadatas
)

# Save DB
print("Done! Vector DB created at ./quran_db")
