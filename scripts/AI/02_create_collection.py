# filename: 02_create_collection.py
import json
import chromadb
from tqdm import tqdm

def create_chroma_collection():
    """Create new ChromaDB collection from JSON file"""
    
    # Load your JSON data
    print("Loading JSON data...")
    with open('quran_embeddings.json', 'r', encoding='utf-8') as f:
        verses = json.load(f)
    
    print(f"Loaded {len(verses)} verses")
    
    # Initialize Chroma client
    client = chromadb.PersistentClient(path="quran_chroma")
    
    # Create collection
    collection = client.create_collection(
        name="quran_verses",
        metadata={
            "hnsw:space": "cosine",
            "description": "Quran verses with Arabic text",
            "embedding_model": "intfloat/multilingual-e5-large"
        }
    )
    
    print("Created collection: 'quran_verses'")
    
    # Add data in batches (for better performance)
    batch_size = 100
    total_batches = (len(verses) + batch_size - 1) // batch_size
    
    print(f"\nAdding {len(verses)} verses in batches of {batch_size}...")
    
    for batch_num in tqdm(range(total_batches), desc="Processing batches"):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(verses))
        
        batch_verses = verses[start_idx:end_idx]
        
        ids = [str(verse['key']) for verse in batch_verses]
        documents = [verse['arabic'] for verse in batch_verses]
        embeddings = [verse['embedding'] for verse in batch_verses]
        
        # Add metadata if available
        metadatas = []
        for verse in batch_verses:
            metadata = {}
            if 'surah' in verse:
                metadata['surah'] = verse['surah']
            if 'ayah' in verse:
                metadata['ayah'] = verse['ayah']
            if 'surah_name' in verse:
                metadata['surah_name'] = verse['surah_name']
            metadatas.append(metadata)
        
        # Add to collection
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas if metadatas[0] else None
        )
    
    print(f"\n✓ Successfully added {collection.count()} items to collection")
    
    # Verify
    print("\nCollection info:")
    print(f"  Name: {collection.name}")
    print(f"  Count: {collection.count()}")
    print(f"  Metadata: {collection.metadata}")

if __name__ == "__main__":
    create_chroma_collection()