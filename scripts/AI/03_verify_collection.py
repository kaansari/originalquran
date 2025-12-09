# filename: 03_verify_collection.py
import chromadb

def verify_collection():
    """Verify the created collection"""
    
    print("Verifying ChromaDB collection...")
    
    # Connect to Chroma
    client = chromadb.PersistentClient(path="quran_chroma")
    
    # List all collections
    collections = client.list_collections()
    print(f"\nAvailable collections: {[c.name for c in collections]}")
    
    # Get the collection
    collection = client.get_collection("quran_verses")
    
    # Basic info
    print(f"\nCollection: {collection.name}")
    print(f"Total items: {collection.count()}")
    print(f"Metadata: {collection.metadata}")
    
    # Get a few sample items
    print("\nSample items (first 3):")
    samples = collection.peek(limit=3)
    
    if 'documents' in samples and samples['documents']:
        for i, doc in enumerate(samples['documents']):
            print(f"\n{i+1}. {doc}")
            if 'metadatas' in samples and samples['metadatas'] and samples['metadatas'][i]:
                print(f"   Metadata: {samples['metadatas'][i]}")
    
    # Test a simple query
    print("\n" + "="*60)
    print("Test Query: Get random 3 items")
    print("="*60)
    
    test_results = collection.get(limit=3)
    for i, doc in enumerate(test_results['documents']):
        print(f"{i+1}. {doc}")

if __name__ == "__main__":
    verify_collection()