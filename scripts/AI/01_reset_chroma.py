# filename: 01_reset_chroma.py
import os
import shutil
import chromadb

def reset_chroma_db():
    """Delete existing ChromaDB and create fresh"""
    
    # Path to your ChromaDB
    chroma_path = "quran_chroma"
    
    # Method 1: Delete the directory
    if os.path.exists(chroma_path):
        print(f"Deleting existing ChromaDB at: {chroma_path}")
        shutil.rmtree(chroma_path)
        print("✓ ChromaDB deleted successfully")
    
    # Method 2: Or use Chroma client to delete collection
    # try:
    #     client = chromadb.PersistentClient(path=chroma_path)
    #     collections = client.list_collections()
    #     for collection in collections:
    #         client.delete_collection(collection.name)
    #         print(f"✓ Deleted collection: {collection.name}")
    # except:
    #     print("No existing collections found")
    
    print("\nChromaDB is ready for fresh data!")

if __name__ == "__main__":
    reset_chroma_db()