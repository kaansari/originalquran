# filename: quran_chat_llm.py
import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os
from typing import List, Dict
import sys

class QuranChatWithLLM:
    def __init__(self, use_openai: bool = False):
        """Initialize Quran Chat with optional LLM enhancement"""
        print("🕋 Initializing Advanced Quran Chat...")
        
        # Load embedding model
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')
        print("✓ Embedding model loaded")
        
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path="quran_chroma")
        self.collection = self.client.get_collection("quran_verses")
        print(f"✓ Connected to Quran database ({self.collection.count()} verses)")
        
        # Optional: OpenAI integration for better responses
        self.use_openai = use_openai
        self.openai_client = None
        
        if use_openai:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                print("✓ OpenAI integration enabled")
            else:
                print("⚠️  OpenAI API key not found, using basic mode")
                self.use_openai = False
        
        # Conversation memory
        self.history = []
        
        print("\n" + "="*60)
        print("Advanced Quran Chat Assistant")
        print("="*60)
        print("\nCommands:")
        print("  /clear  - Clear conversation history")
        print("  /mode   - Switch response mode")
        print("  /help   - Show this help")
        print("  /quit   - Exit\n")
    
    def search_verses(self, query: str, n_results: int = 7) -> List[Dict]:
        """Search for relevant Quran verses"""
        query_embedding = self.model.encode([query], normalize_embeddings=True)[0].tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        verses = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                verses.append({
                    'text': results['documents'][0][i],
                    'similarity': 1 - results['distances'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                })
        
        return verses
    
    def generate_with_llm(self, query: str, verses: List[Dict]) -> str:
        """Generate enhanced response using LLM"""
        if not self.openai_client or not verses:
            return self.generate_basic_response(query, verses)
        
        # Prepare context
        context = "Relevant Quran verses:\n"
        for i, verse in enumerate(verses[:5]):
            text = verse['text']
            metadata = verse['metadata']
            
            context += f"\n{i+1}. {text}"
            if metadata.get('surah_name'):
                context += f" (سورة {metadata['surah_name']}"
                if metadata.get('ayah'):
                    context += f، الآية {metadata['ayah']}"
                context += ")"
        
        # Create prompt
        prompt = f"""You are a knowledgeable Quran assistant. Answer the user's question based on the provided Quran verses.

User Question: {query}

{context}

Instructions:
1. Answer in the same language as the question (Arabic or English)
2. Reference specific verses when appropriate
3. Provide brief explanation
4. Be accurate and respectful
5. If verses don't fully answer, say so honestly

Response:"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful Quran expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️  LLM Error: {e}")
            return self.generate_basic_response(query, verses)
    
    def generate_basic_response(self, query: str, verses: List[Dict]) -> str:
        """Generate basic response without LLM"""
        if not verses:
            return "I couldn't find relevant Quran verses for your query. Please try rephrasing."
        
        # Determine language
        is_arabic = any(char in query for char in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        
        if is_arabic:
            response = "**الآيات القرآنية ذات الصلة:**\n\n"
        else:
            response = "**Relevant Quranic Verses:**\n\n"
        
        for i, verse in enumerate(verses[:5]):
            text = verse['text']
            similarity = verse['similarity']
            metadata = verse['metadata']
            
            response += f"{i+1}. {text}\n"
            
            if metadata:
                meta_parts = []
                if metadata.get('surah_name'):
                    meta_parts.append(f"سورة {metadata['surah_name']}")
                if metadata.get('ayah'):
                    meta_parts.append(f"الآية {metadata['ayah']}")
                
                if meta_parts:
                    response += f"   ({' | '.join(meta_parts)})\n"
            
            response += f"   Similarity: {similarity:.1%}\n"
            response += "-" * 40 + "\n"
        
        if is_arabic:
            response += "\n💡 *تم اختيار هذه الآيات بناءً على تشابهها مع سؤالك*"
        else:
            response += "\n💡 *These verses were selected based on semantic similarity to your query*"
        
        return response
    
    def process_command(self, cmd: str) -> bool:
        """Process special commands"""
        cmd = cmd.lower().strip()
        
        if cmd == '/clear':
            self.history = []
            print("✓ Conversation cleared")
            return True
        
        elif cmd == '/mode':
            self.use_openai = not self.use_openai
            mode = "Enhanced (LLM)" if self.use_openai else "Basic"
            print(f"✓ Switched to {mode} mode")
            return True
        
        elif cmd == '/help':
            print("\nAvailable commands:")
            print("  /clear  - Clear conversation history")
            print("  /mode   - Toggle between basic and enhanced mode")
            print("  /quit   - Exit the chat")
            print("\nYou can ask questions in Arabic or English about:")
            print("  - Quranic verses and their meanings")
            print("  - Islamic concepts and teachings")
            print("  - Guidance on various life aspects")
            return True
        
        return False
    
    def chat_loop(self):
        """Main chat loop"""
        print("\n💬 Start chatting (type /help for commands)...\n")
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['/quit', 'quit', 'exit']:
                    print("\n🕋 Goodbye...")
                    break
                
                # Check for commands
                if user_input.startswith('/'):
                    self.process_command(user_input)
                    continue
                
                if not user_input:
                    continue
                
                # Add to history
                self.history.append({"role": "user", "content": user_input})
                
                print("\n🤖 Assistant: ", end="", flush=True)
                
                # Search for verses
                verses = self.search_verses(user_input)
                
                # Generate response
                if self.use_openai and self.openai_client:
                    response = self.generate_with_llm(user_input, verses)
                else:
                    response = self.generate_basic_response(user_input, verses)
                
                # Print response
                print(response)
                
                # Add to history
                self.history.append({"role": "assistant", "content": response})
                
            except KeyboardInterrupt:
                print("\n\n🕋 Goodbye...")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Quran Chat Assistant')
    parser.add_argument('--llm', action='store_true', help='Enable LLM enhancement (requires OpenAI API key)')
    args = parser.parse_args()
    
    try:
        assistant = QuranChatWithLLM(use_openai=args.llm)
        assistant.chat_loop()
    except Exception as e:
        print(f"Initialization failed: {e}")
        print("\nMake sure you've run the setup scripts first!")

if __name__ == "__main__":
    main()