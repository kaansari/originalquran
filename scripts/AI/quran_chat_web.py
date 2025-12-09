# filename: quran_chat_web.py
from flask import Flask, render_template, request, jsonify
import chromadb
from sentence_transformers import SentenceTransformer
import json

app = Flask(__name__)

# Initialize components
print("Loading Quran Chat Web App...")
model = SentenceTransformer('intfloat/multilingual-e5-large')
client = chromadb.PersistentClient(path="quran_chroma")
collection = client.get_collection("quran_verses")
print(f"Ready! {collection.count()} verses loaded")

@app.route('/')
def home():
    return render_template('quran_chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'No query provided'})
    
    try:
        # Search for verses
        query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        
        verses = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                verses.append({
                    'text': results['documents'][0][i],
                    'similarity': float(1 - results['distances'][0][i]),
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                })
        
        # Generate response
        is_arabic = any(char in query for char in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        
        if is_arabic:
            response = "**الآيات القرآنية المناسبة:**\n\n"
        else:
            response = "**Relevant Quranic Verses:**\n\n"
        
        for i, verse in enumerate(verses):
            response += f"{i+1}. {verse['text']}\n"
            
            if verse['metadata']:
                meta = verse['metadata']
                if meta.get('surah_name'):
                    response += f"   (سورة {meta['surah_name']}"
                    if meta.get('ayah'):
                        response += f، الآية {meta['ayah']}"
                    response += ")\n"
            
            response += f"   Similarity: {verse['similarity']:.1%}\n"
            response += "---\n"
        
        return jsonify({
            'response': response,
            'verses': verses,
            'count': len(verses)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/search', methods=['GET'])
def api_search():
    """API endpoint for programmatic access"""
    query = request.args.get('q', '')
    n_results = int(request.args.get('n', 5))
    
    if not query:
        return jsonify({'error': 'No query parameter'})
    
    try:
        query_embedding = model.encode([query], normalize_embeddings=True)[0].tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        verses = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                verses.append({
                    'verse': results['documents'][0][i],
                    'similarity': float(1 - results['distances'][0][i]),
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                })
        
        return jsonify({
            'query': query,
            'results': verses,
            'count': len(verses)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)