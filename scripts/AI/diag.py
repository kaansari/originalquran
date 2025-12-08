import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load your embeddings
with open('quran_embeddings.json', 'r', encoding='utf-8') as f:
    verses = json.load(f)

print(f"Loaded {len(verses)} verses")

# Get a sample verse
sample_verse = verses[0]
print(f"\nSample verse: {sample_verse['arabic']}")
print(f"Embedding length: {len(sample_verse['embedding'])}")

# Check if embeddings are normalized
embeddings = np.array([v['embedding'] for v in verses[:100]])  # First 100
norms = np.linalg.norm(embeddings, axis=1)

print(f"\nEmbedding Norm Analysis (first 100):")
print(f"Mean norm: {np.mean(norms):.6f}")
print(f"Std norm: {np.std(norms):.6f}")
print(f"Min norm: {np.min(norms):.6f}")
print(f"Max norm: {np.max(norms):.6f}")

# Check embedding statistics
print(f"\nEmbedding Value Statistics:")
print(f"Mean: {np.mean(embeddings):.6f}")
print(f"Std: {np.std(embeddings):.6f}")
print(f"Min: {np.min(embeddings):.6f}")
print(f"Max: {np.max(embeddings):.6f}")

# Test semantic quality with fresh embeddings
print("\n" + "="*70)
print("COMPARISON: Your embeddings vs Fresh embeddings")
print("="*70)

model = SentenceTransformer('intfloat/multilingual-e5-large')

# Test cases
test_cases = [
    ("يوم القيامة", "مالك يوم الدين"),
    ("الصلاة", "اقم الصلاة"), 
    ("الجنة", "جنات تجري من تحتها الانهار"),
]

for query, target in test_cases:
    print(f"\nQuery: '{query}'")
    print(f"Target: '{target}'")
    
    # 1. Find target in your embeddings
    target_idx = None
    for i, v in enumerate(verses):
        if target in v['arabic']:
            target_idx = i
            break
    
    if target_idx is not None:
        # Use your stored embedding
        target_embedding_yours = np.array([verses[target_idx]['embedding']])
        
        # 2. Create fresh embedding of query
        query_embedding_fresh = model.encode([query], normalize_embeddings=True)
        
        # 3. Calculate similarity
        similarity_yours = float(np.dot(target_embedding_yours, query_embedding_fresh.T)[0][0])
        
        # 4. Create fresh embedding of target for comparison
        target_embedding_fresh = model.encode([target], normalize_embeddings=True)
        similarity_fresh = float(np.dot(target_embedding_fresh, query_embedding_fresh.T)[0][0])
        
        print(f"  Your embedding similarity: {similarity_yours:.4f}")
        print(f"  Fresh embedding similarity: {similarity_fresh:.4f}")
        print(f"  Difference: {abs(similarity_yours - similarity_fresh):.4f}")
        
        if abs(similarity_yours - similarity_fresh) > 0.1:
            print(f"  ⚠️ LARGE DIFFERENCE - Your embeddings may be corrupted!")
    else:
        print(f"  ❌ Target not found in your data")

# Check for duplicate verses
print("\n" + "="*70)
print("CHECKING FOR DUPLICATE/CORRUPTED EMBEDDINGS")
print("="*70)

# Look for verses with identical or near-identical embeddings
from collections import defaultdict

# Group by text
text_to_embeddings = defaultdict(list)
for i, verse in enumerate(verses[:500]):  # Check first 500
    text = verse['arabic']
    text_to_embeddings[text].append(i)

# Check duplicates
duplicates_found = False
for text, indices in text_to_embeddings.items():
    if len(indices) > 1:
        print(f"\nDuplicate text found: '{text[:50]}...'")
        print(f"  Found at indices: {indices}")
        
        # Compare embeddings
        emb1 = np.array(verses[indices[0]]['embedding'])
        emb2 = np.array(verses[indices[1]]['embedding'])
        similarity = float(np.dot(emb1, emb2.T))
        
        print(f"  Embedding similarity: {similarity:.4f}")
        if similarity < 0.99:
            print(f"  ⚠️ Different embeddings for same text!")
        duplicates_found = True

if not duplicates_found:
    print("No duplicate texts found in first 500 verses")