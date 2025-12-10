# filename: quran_chat_auto_translate.py
import chromadb
from sentence_transformers import SentenceTransformer
from deep_translator import GoogleTranslator
import sys

class QuranChatAutoTranslate:
    def __init__(self, chroma_path: str = "quran_chroma"):
        """Initialize Quran Chat with auto-translation"""
        print("🕋 Initializing Quran Chat with Auto-Translation...")
        
        # Load embedding model
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')
        print("✓ Embedding model loaded")
        
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_collection("quran_verses")
        print(f"✓ Connected to Quran database ({self.collection.count()} verses)")
        
        # Initialize translator
        print("Loading translator...")
        self.translator = GoogleTranslator(source='auto', target='ar')
        print("✓ Translator ready")
        
        # Common translations cache
        self.common_translations = {
            'who is allah': 'من هو الله',
            'who is god': 'من هو الله',
            'allah': 'الله',
            'god': 'الله',
            'who is moses': 'من هو موسى',
            'moses': 'موسى',
            'who is mohammed': 'من هو محمد',
            'mohammed': 'محمد',
            'prophet': 'النبي',
            'messenger': 'الرسول',
            'quran': 'القرآن',
            'prayer': 'الصلاة',
            'fasting': 'الصيام',
            'charity': 'الزكاة',
            'paradise': 'الجنة',
            'hell': 'النار',
            'judgment day': 'يوم القيامة',
            'faith': 'الإيمان',
            'patience': 'الصبر',
            'mercy': 'الرحمة',
            'forgiveness': 'المغفرة'
        }
        
        print("\n" + "="*60)
        print("Quran Chat Assistant (Auto-Translate)")
        print("="*60)
        print("\nSpeak in English or Arabic. I'll search in pure Arabic.")
        print("Commands: 'quit', 'clear', 'help'")
        print("-" * 60)
    
    def translate_to_arabic(self, text: str) -> str:
        """Translate English to Arabic, with caching"""
        text_lower = text.lower().strip()
        
        # Check common translations first
        for eng, ar in self.common_translations.items():
            if eng in text_lower:
                return ar
        
        try:
            # Use translator for other phrases
            translated = self.translator.translate(text)
            print(f"   [Translated: '{text}' → '{translated}']")
            return translated
        except Exception as e:
            print(f"   [Translation failed: {e}]")
            return text  # Return original if translation fails
    
    def is_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        arabic_chars = 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
        return any(char in arabic_chars for char in text)
    
    def search_verses(self, query: str, n_results: int = 5) -> list:
        """Search for Quran verses"""
        # Auto-translate if not Arabic
        search_query = query
        if not self.is_arabic(query):
            search_query = self.translate_to_arabic(query)
        
        print(f"   Searching with: '{search_query}'")
        
        # Generate embedding
        query_embedding = self.model.encode(
            [search_query], 
            normalize_embeddings=True
        )[0].tolist()
        
        # Search in ChromaDB
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
        
        return verses, search_query
    
    def format_response(self, query: str, translated_query: str, verses: list) -> str:
        """Format the response"""
        response_parts = []
        
        # Show translation info if applicable
        if query != translated_query:
            response_parts.append(f"🔍 Translated query: '{translated_query}'")
            response_parts.append("")
        
        if not verses:
            response_parts.append("لم أجد آيات قرآنية تناسب سؤالك.")
            response_parts.append("حاول صياغة السؤال بشكل مختلف.")
            return "\n".join(response_parts)
        
        # Add verses
        response_parts.append("**الآيات القرآنية المناسبة:**")
        response_parts.append("")
        
        for i, verse in enumerate(verses):
            text = verse['text']
            similarity = verse['similarity']
            metadata = verse['metadata']
            
            response_parts.append(f"{i+1}. {text}")
            
            # Add metadata if available
            if metadata:
                meta_info = []
                if metadata.get('surah_name'):
                    meta_info.append(f"سورة {metadata['surah_name']}")
                if metadata.get('surah'):
                    meta_info.append(f"({metadata['surah']})")
                if metadata.get('ayah'):
                    meta_info.append(f"الآية {metadata['ayah']}")
                
                if meta_info:
                    response_parts.append(f"   📖 {' | '.join(meta_info)}")
            
            response_parts.append(f"   🔍 التطابق: {similarity:.1%}")
            response_parts.append("-" * 50)
        
        # Simple analysis
        response_parts.append("\n💡 **ملاحظة:**")
        response_parts.append("هذه الآيات تم اختيارها بناءً على التشابه الدلالي مع سؤالك.")
        response_parts.append("التحليل يعتمد على النص العربي القرآني فقط.")
        
        return "\n".join(response_parts)
    
    def chat_loop(self):
        """Main chat loop"""
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'خروج']:
                    print("\n🕋 مع السلامة...")
                    break
                
                if user_input.lower() in ['clear', 'مسح']:
                    print("✓ Chat cleared")
                    continue
                
                if user_input.lower() == 'help':
                    print("\n📖 **Help:**")
                    print("  • Ask in English or Arabic")
                    print("  • I'll translate and search in pure Arabic")
                    print("  • Results are based on semantic similarity")
                    print("  • No external interpretations used")
                    continue
                
                if not user_input:
                    continue
                
                print("\n🤖 Assistant: ", end="", flush=True)
                
                # Search for verses
                verses, translated_query = self.search_verses(user_input)
                
                # Generate response
                response = self.format_response(user_input, translated_query, verses)
                
                # Print response
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n🕋 مع السلامة...")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}")

def main():
    """Main function"""
    try:
        # Install required package if not present
        try:
            from deep_translator import GoogleTranslator
        except ImportError:
            print("Installing deep-translator...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "deep-translator"])
            from deep_translator import GoogleTranslator
        
        assistant = QuranChatAutoTranslate()
        assistant.chat_loop()
    except Exception as e:
        print(f"Initialization failed: {e}")
        print("\nMake sure:")
        print("1. You've run the setup scripts first")
        print("2. You have internet connection for translation")

if __name__ == "__main__":
    main()