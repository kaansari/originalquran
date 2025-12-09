# filename: quran_chat.py
import chromadb
from sentence_transformers import SentenceTransformer
import json
from typing import List, Dict, Tuple
import textwrap
import sys

class QuranChatAssistant:
    def __init__(self, chroma_path: str = "quran_chroma"):
        """Initialize the Quran Chat Assistant"""
        print("🕋 Initializing Quran Chat Assistant...")
        
        # Load embedding model
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')
        print("✓ Embedding model loaded")
        
        # Connect to ChromaDB
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_collection("quran_verses")
        print(f"✓ Connected to Quran database ({self.collection.count()} verses)")
        
        # System prompt
        self.system_prompt = """أنت مساعد ذكي متخصص في القرآن الكريم. مهمتك هي:
1. الإجابة على أسئلة المستخدم بناءً على آيات القرآن
2. استخراج الآيات المناسبة من قاعدة البيانات
3. تقديم تفسير بسيط للآيات عند الحاجة
4. الإجابة بلغة المستخدم (العربية أو الإنجليزية)

قواعد:
- استشهد بالآيات القرآنية المناسبة دائمًا
- اذكر رقم السورة والآية إذا كان متوفرًا
- كن دقيقًا في نقل الآيات
- إذا لم تجد آية مناسبة، قل بصراحة
"""
        
        # Context memory
        self.conversation_history = []
        
        print("\n" + "="*60)
        print("مرحباً! أنا مساعد القرآن الكريم الذكي")
        print("يمكنك سؤالي عن أي موضوع وسأجد لك الآيات المناسبة")
        print("أدخل 'quit' للخروج، 'clear' لمسح الذاكرة")
        print("="*60 + "\n")
    
    def search_verses(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for relevant Quran verses"""
        # Generate embedding for query
        query_embedding = self.model.encode(
            [query], 
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
                verse_text = results['documents'][0][i]
                distance = results['distances'][0][i]
                similarity = 1 - distance
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                
                verses.append({
                    'text': verse_text,
                    'similarity': similarity,
                    'metadata': metadata
                })
        
        return verses
    
    def format_verse(self, verse: Dict, index: int) -> str:
        """Format a verse for display"""
        text = verse['text']
        similarity = verse['similarity']
        metadata = verse['metadata']
        
        formatted = f"\n{index}. {text}\n"
        
        # Add metadata if available
        meta_parts = []
        if metadata.get('surah_name'):
            meta_parts.append(f"سورة {metadata['surah_name']}")
        if metadata.get('surah'):
            meta_parts.append(f"({metadata['surah']})")
        if metadata.get('ayah'):
            meta_parts.append(f"الآية {metadata['ayah']}")
        
        if meta_parts:
            formatted += f"   📖 {' | '.join(meta_parts)}\n"
        
        formatted += f"   🔍 التطابق: {similarity:.1%}\n"
        formatted += "-" * 60
        
        return formatted
    
    def generate_response(self, query: str, verses: List[Dict]) -> str:
        """Generate a response based on query and found verses"""
        
        if not verses:
            return "لم أجد آيات قرآنية تناسب سؤالك. يمكنك صياغة السؤال بشكل مختلف أو طرح موضوع آخر."
        
        # Build response
        response_parts = []
        
        # Arabic response
        if any(char in query for char in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'):
            response_parts.append("**الآيات القرآنية المناسبة:**\n")
        else:
            response_parts.append("**Relevant Quranic Verses:**\n")
        
        # Add top verses
        for i, verse in enumerate(verses[:3]):  # Show top 3
            response_parts.append(self.format_verse(verse, i+1))
        
        # Add interpretation
        response_parts.append("\n**💡 التفسير الموجز:**")
        
        # Simple interpretation based on query
        query_lower = query.lower()
        if 'رحمن' in query_lower or 'رحيم' in query_lower:
            response_parts.append("هذه الآيات تتحدث عن رحمة الله الواسعة التي وسعت كل شيء.")
        elif 'صلاة' in query_lower:
            response_parts.append("الصلاة عماد الدين وهي الصلة بين العبد وربه.")
        elif 'جنة' in query_lower or 'نار' in query_lower:
            response_parts.append("الآيات تتناول الثواب والعقاب في الآخرة.")
        elif 'توبة' in query_lower:
            response_parts.append("الله يتقبل توبة التائبين ويغفر الذنوب.")
        elif 'صبر' in query_lower:
            response_parts.append("الصبر من أعظم العبادات وأجلّها عند الله.")
        else:
            response_parts.append("هذه الآيات تتناول جوانب من الموضوع الذي تسأل عنه.")
        
        response_parts.append("\n**ملاحظة:** هذه الآيات مختارة بناءً على التشابه الدلالي مع سؤالك.")
        
        return "\n".join(response_parts)
    
    def chat_loop(self):
        """Main chat loop"""
        while True:
            try:
                # Get user input
                user_input = input("\n👤 أنت: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'خروج']:
                    print("\n🕋 مع السلامة...")
                    break
                
                if user_input.lower() in ['clear', 'مسح']:
                    self.conversation_history = []
                    print("✓ تم مسح ذاكرة المحادثة")
                    continue
                
                if not user_input:
                    continue
                
                # Add to history
                self.conversation_history.append(("user", user_input))
                
                print("\n🤖 المساعد: ", end="", flush=True)
                
                # Search for relevant verses
                verses = self.search_verses(user_input)
                
                # Generate and display response
                response = self.generate_response(user_input, verses)
                
                # Print response with typing effect
                for line in response.split('\n'):
                    print(line)
                    sys.stdout.flush()
                
                # Add to history
                self.conversation_history.append(("assistant", response))
                
            except KeyboardInterrupt:
                print("\n\n🕋 مع السلامة...")
                break
            except Exception as e:
                print(f"\n⚠️  حدث خطأ: {e}")

def main():
    """Main function"""
    try:
        assistant = QuranChatAssistant()
        assistant.chat_loop()
    except Exception as e:
        print(f"فشل التهيئة: {e}")
        print("تأكد من:")
        print("1. تشغيل 02_create_collection.py أولاً")
        print("2. وجود مجلد quran_chroma في نفس الدليل")

if __name__ == "__main__":
    main()