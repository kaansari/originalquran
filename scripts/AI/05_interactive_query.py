# filename: 05_interactive_query.py
import chromadb
from sentence_transformers import SentenceTransformer

def interactive_query():
    """Interactive query interface"""
    
    print("Quran Semantic Search - Interactive Mode")
    print("="*50)
    
    # Connect to Chroma
    client = chromadb.PersistentClient(path="quran_chroma")
    collection = client.get_collection("quran_verses")
    
    # Load the model
    print("Loading embedding model...")
    model = SentenceTransformer('intfloat/multilingual-e5-large')
    
    print(f"\nCollection ready: {collection.name} ({collection.count()} verses)")
    print("\nType your queries in Arabic. Commands: 'quit', 'help', 'info'")
    print("-" * 50)
    
    while True:
        query = input("\n📝 Enter Arabic query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if query.lower() == 'help':
            print("\nAvailable commands:")
            print("  'quit' - Exit the program")
            print("  'info' - Show collection info")
            print("  'help' - Show this help message")
            print("\nExample Arabic queries:")
            print("  الرحمن الرحيم")
            print("  يوم القيامة")
            print("  الصلاة والزكاة")
            continue
        
        if query.lower() == 'info':
            print(f"\nCollection: {collection.name}")
            print(f"Total verses: {collection.count()}")
            print(f"Embedding model: intfloat/multilingual-e5-large")
            continue
        
        if not query:
            continue
        
        # Perform query
        print(f"\nSearching for: '{query}'")
        print("-" * 60)
        
        try:
            # Generate embedding
            query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()
            
            # Query with more results
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                include=["documents", "distances", "metadatas"]
            )
            
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    verse = results['documents'][0][i]
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    print(f"\n{i+1}. Similarity: {similarity:.1%}")
                    print(f"   {verse}")
                    
                    if metadata:
                        meta_info = []
                        if metadata.get('surah_name'):
                            meta_info.append(f"{metadata['surah_name']}")
                        if metadata.get('surah'):
                            meta_info.append(f"Surah {metadata['surah']}")
                        if metadata.get('ayah'):
                            meta_info.append(f"Ayah {metadata['ayah']}")
                        if meta_info:
                            print(f"   ({' | '.join(meta_info)})")
                
                print("-" * 60)
                print(f"Found {len(results['documents'][0])} relevant verses")
            else:
                print("No results found.")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    interactive_query()