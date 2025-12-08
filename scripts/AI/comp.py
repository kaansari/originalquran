import json
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from tqdm import tqdm

# Load your existing embeddings
with open('quran_embeddings.json', 'r', encoding='utf-8') as f:
    verses = json.load(f)

print(f"Loaded {len(verses)} verses from JSON file")

# Initialize the model (same one used for embeddings)
model = SentenceTransformer('intfloat/multilingual-e5-large')

# Test queries with expected relevant verses
test_queries = [
    {
        "query": "الرحمن الرحيم",
        "expected_verses": [
            "بسم الله الرحمن الرحيم",
            "الرحمن الرحيم",
            "قل ادعوا الله او ادعوا الرحمن"
        ],
        "description": "Names of Allah - Most Gracious, Most Merciful"
    },
    {
        "query": "يوم القيامة",
        "expected_verses": [
            "مالك يوم الدين",
            "وما ادراك ما يوم الدين", 
            "يوم يقوم الناس لرب العالمين"
        ],
        "description": "Day of Judgment"
    },
    {
        "query": "الصلاة",
        "expected_verses": [
            "اقم الصلاة",
            "واياك نستعين",
            "الذين هم على صلاتهم دائمون"
        ],
        "description": "Prayer"
    },
    {
        "query": "الجنة",
        "expected_verses": [
            "جنات تجري من تحتها الانهار",
            "اولئك لهم جنات عدن",
            "وسارعوا الى مغفرة من ربكم وجنة"
        ],
        "description": "Paradise"
    },
    {
        "query": "التوبة والمغفرة",
        "expected_verses": [
            "ان الله يحب التوابين",
            "واستغفروا ربكم ثم توبوا اليه",
            "غافر الذنب وقابل التوب"
        ],
        "description": "Repentance and Forgiveness"
    }
]

def test_semantic_search():
    """Test semantic search on the embedded verses"""
    print("\n" + "="*80)
    print("COMPREHENSIVE SEMANTIC SEARCH TEST")
    print("="*80)
    
    # Convert verses to numpy arrays for efficient computation
    print("\nPreparing embeddings...")
    arabic_texts = [verse['arabic'] for verse in verses]
    embeddings = np.array([verse['embedding'] for verse in verses])
    
    print(f"Embeddings shape: {embeddings.shape}")
    print(f"Sample embedding length: {len(embeddings[0])}")
    
    overall_scores = []
    
    for test in tqdm(test_queries, desc="Testing queries"):
        query = test["query"]
        expected_verses = test["expected_verses"]
        
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")
        print(f"Description: {test['description']}")
        print('='*60)
        
        # Encode query
        query_embedding = model.encode([query], normalize_embeddings=True)
        
        # Calculate similarities
        similarities = np.dot(embeddings, query_embedding.T).flatten()
        
        # Get top 10 results
        top_indices = np.argsort(similarities)[::-1][:10]
        
        # Calculate precision metrics
        found_expected = []
        found_other = []
        
        print(f"\nTop 10 results:")
        print("-" * 80)
        
        for i, idx in enumerate(top_indices):
            verse_text = arabic_texts[idx]
            similarity = similarities[idx]
            
            # Check if this is an expected verse
            is_expected = any(expected in verse_text for expected in expected_verses)
            
            if is_expected:
                found_expected.append(verse_text)
                marker = "✅ EXPECTED"
            else:
                found_other.append(verse_text)
                marker = "📖 OTHER"
            
            print(f"{i+1:2d}. {marker}")
            print(f"    Similarity: {similarity:.4f}")
            print(f"    Verse: {verse_text}")
            print("-" * 80)
        
        # Calculate metrics - FIXED THIS PART
        top_5_verses = [arabic_texts[idx] for idx in top_indices[:5]]
        top_10_verses = [arabic_texts[idx] for idx in top_indices[:10]]
        
        precision_at_5 = len([v for v in top_5_verses 
                            if any(expected in v for expected in expected_verses)]) / 5
        precision_at_10 = len([v for v in top_10_verses 
                             if any(expected in v for expected in expected_verses)]) / 10
        
        # Find positions of expected verses
        expected_positions = []
        for expected in expected_verses:
            # Find this verse in the results
            for pos, idx in enumerate(top_indices):
                if expected in arabic_texts[idx]:
                    expected_positions.append(pos + 1)  # 1-indexed
                    break
        
        print(f"\n📊 Performance Metrics:")
        print(f"  Expected verses found: {len(found_expected)}/{len(expected_verses)}")
        if expected_positions:
            print(f"  Positions in top 10: {expected_positions}")
            print(f"  Average position: {np.mean(expected_positions):.1f}")
        print(f"  Precision@5: {precision_at_5:.2%}")
        print(f"  Precision@10: {precision_at_10:.2%}")
        
        overall_scores.append({
            'query': query,
            'precision_at_5': precision_at_5,
            'precision_at_10': precision_at_10,
            'expected_found': len(found_expected),
            'total_expected': len(expected_verses)
        })
    
    # Print overall statistics
    print("\n" + "="*80)
    print("OVERALL STATISTICS")
    print("="*80)
    
    avg_precision_5 = np.mean([s['precision_at_5'] for s in overall_scores])
    avg_precision_10 = np.mean([s['precision_at_10'] for s in overall_scores])
    total_found = sum(s['expected_found'] for s in overall_scores)
    total_expected = sum(s['total_expected'] for s in overall_scores)
    
    print(f"\nAverage Precision@5: {avg_precision_5:.2%}")
    print(f"Average Precision@10: {avg_precision_10:.2%}")
    print(f"Total expected verses found: {total_found}/{total_expected} ({total_found/total_expected:.1%})")
    
    # Show per-query performance
    print(f"\nPer-query performance:")
    print("-" * 80)
    for score in overall_scores:
        print(f"{score['query']:30s} | P@5: {score['precision_at_5']:6.2%} | P@10: {score['precision_at_10']:6.2%} | Found: {score['expected_found']}/{score['total_expected']}")

def test_chroma_query():
    """Test querying through ChromaDB"""
    print("\n" + "="*80)
    print("CHROMADB QUERY TEST")
    print("="*80)
    
    try:
        # Connect to Chroma
        client = chromadb.PersistentClient(path="quran_chroma")
        collection = client.get_collection("quran_verses")
        
        print(f"Collection size: {collection.count()}")
        
        # Test a few queries
        test_queries_chroma = [
            "الرحمن الرحيم",
            "يوم القيامة", 
            "الجنة والنار",
            "الصبر والصلاة"
        ]
        
        for query in test_queries_chroma:
            print(f"\nQuery: '{query}'")
            
            # Encode query
            query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()
            
            # Query Chroma
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                include=["documents", "distances"]
            )
            
            if results['documents']:
                for i, (verse, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
                    similarity = 1 - distance  # Convert distance to similarity
                    print(f"  {i+1}. Similarity: {similarity:.4f}")
                    print(f"     {verse}")
                    print()
    except Exception as e:
        print(f"Error connecting to ChromaDB: {e}")
        print("Make sure ChromaDB collection exists at 'quran_chroma'")

def analyze_embeddings():
    """Analyze the embedding quality"""
    print("\n" + "="*80)
    print("EMBEDDING QUALITY ANALYSIS")
    print("="*80)
    
    embeddings = np.array([verse['embedding'] for verse in verses])
    
    # Check embedding statistics
    print(f"\nEmbedding Statistics:")
    print(f"  Shape: {embeddings.shape}")
    print(f"  Mean: {np.mean(embeddings):.6f}")
    print(f"  Std: {np.std(embeddings):.6f}")
    print(f"  Min: {np.min(embeddings):.6f}")
    print(f"  Max: {np.max(embeddings):.6f}")
    
    # Check if embeddings are normalized
    norms = np.linalg.norm(embeddings, axis=1)
    print(f"\nNormalization Check:")
    print(f"  Mean norm: {np.mean(norms):.6f}")
    print(f"  Std norm: {np.std(norms):.6f}")
    print(f"  Min norm: {np.min(norms):.6f}")
    print(f"  Max norm: {np.max(norms):.6f}")
    
    # Check for duplicate or very similar verses
    print(f"\nSimilarity Analysis (first 50 verses):")
    
    # Sample some verses to check intra-similarity
    sample_size = min(50, len(verses))
    sample_indices = list(range(0, sample_size))
    sample_embeddings = embeddings[sample_indices]
    sample_texts = [verses[i]['arabic'] for i in sample_indices]
    
    # Compute similarity matrix
    similarity_matrix = np.dot(sample_embeddings, sample_embeddings.T)
    
    print(f"Checking similarities among {sample_size} verses...")
    
    high_similarity_pairs = []
    for i in range(len(sample_indices)):
        for j in range(i+1, len(sample_indices)):
            sim = similarity_matrix[i, j]
            if sim > 0.85:  # High similarity threshold
                high_similarity_pairs.append((i, j, sim))
    
    if high_similarity_pairs:
        print(f"\nFound {len(high_similarity_pairs)} highly similar pairs (>0.85):")
        for i, j, sim in high_similarity_pairs[:5]:  # Show first 5
            print(f"  Similarity: {sim:.3f}")
            print(f"    Verse {i+1}: {sample_texts[i][:60]}...")
            print(f"    Verse {j+1}: {sample_texts[j][:60]}...")
            print()
    else:
        print("No highly similar pairs found (all < 0.85)")

# Run all tests
if __name__ == "__main__":
    print("Quran Embedding Quality Test Suite")
    print("Model: intfloat/multilingual-e5-large")
    print("-" * 80)
    
    # Run tests
    test_semantic_search()
    
    # Ask user if they want to run Chroma test
    run_chroma = input("\nRun ChromaDB test? (y/n): ").strip().lower()
    if run_chroma == 'y':
        test_chroma_query()
    
    # Run embedding analysis
    analyze_embeddings()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    
    # Quick recommendation based on results
    print("\n🎯 INTERPRETATION GUIDE:")
    print("• Precision@5 > 60%: Good performance")
    print("• Precision@5 40-60%: Acceptable but could be better") 
    print("• Precision@5 < 40%: Consider re-embedding with different model")
    print("• Embedding norms should be close to 1.0 for cosine similarity")