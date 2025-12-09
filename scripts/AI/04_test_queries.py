# filename: 04_test_queries.py
import chromadb
from sentence_transformers import SentenceTransformer

def test_queries():
    """Test semantic search queries on the collection"""
    
    print("Testing semantic search queries...")
    
    # Connect to Chroma
    client = chromadb.PersistentClient(path="quran_chroma")
    collection = client.get_collection("quran_verses")
    
    # Load the same model used for embeddings
    print("Loading embedding model...")
    model = SentenceTransformer('intfloat/multilingual-e5-large')
    
    # Test queries
    test_cases = [
        ("الرحمن الرحيم", "Most Gracious, Most Merciful"),
        ("يوم القيامة", "Day of Judgment"),
        ("الصلاة", "Prayer"),
        ("الجنة", "Paradise"),
        ("التوبة", "Repentance"),
        ("الزكاة", "Charity"),
        ("الصبر", "Patience"),
        ("العدل", "Justice"),
    ]
    
    print(f"\nTesting {len(test_cases)} queries...")
    print("="*70)
    
    for arabic_query, english_translation in test_cases:
        print(f"\n🔍 Query: '{arabic_query}' ({english_translation})")
        print("-" * 70)
        
        # Generate embedding for query
        query_embedding = model.encode([arabic_query], normalize_embeddings=True)[0].tolist()
        
        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            include=["documents", "distances", "metadatas"]
        )
        
        if results['documents']:
            for i in range(len(results['documents'][0])):
                verse = results['documents'][0][i]
                distance = results['distances'][0][i]
                similarity = 1 - distance
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                
                print(f"\n{i+1}. Similarity: {similarity:.2%}")
                print(f"   Verse: {verse}")
                
                if metadata:
                    meta_info = []
                    if metadata.get('surah'):
                        meta_info.append(f"Surah: {metadata['surah']}")
                    if metadata.get('ayah'):
                        meta_info.append(f"Ayah: {metadata['ayah']}")
                    if meta_info:
                        print(f"   {' | '.join(meta_info)}")
        
        print("-" * 70)

if __name__ == "__main__":
    test_queries()