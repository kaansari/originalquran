import json
from chromadb import Client
from chromadb.config import Settings

# Use local persistent DB
client = Client(Settings(
    chroma_api_impl="local",
    persist_directory="./chroma-db"
))
collection = client.get_or_create_collection("quran")

# Load your verse file
with open("/home/kaansari/Work/originalquran/src/json/quran_embeddings.json", "r") as f:
    data = json.load(f)

ids = []
documents = []
embeddings = []

for verse_id, row in data.items():
    ids.append(verse_id)
    documents.append(row["arabic"])
    embeddings.append(row["embedding"])

collection.add(ids=ids, embeddings=embeddings, documents=documents)
client.persist()
