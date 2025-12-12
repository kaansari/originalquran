#!/usr/bin/env python3
"""
Working Q&A Engine with direct search
"""

import re
import json

class WorkingQAEngine:
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        """Load data directly"""
        print("Loading data...")
        
        # Load words
        with open('quran_words.json', 'r', encoding='utf-8') as f:
            self.words = json.load(f)
        
        # Load verses
        with open('verses.json', 'r', encoding='utf-8') as f:
            self.verses = json.load(f)
        
        # Load word-to-verse mapping from verses.json
        self.word_to_verse = {}
        for verse_id_str, verse_data in self.verses.items():
            try:
                verse_id = int(verse_id_str)
                start = int(verse_data['start_word'])
                end = int(verse_data['end_word'])
                
                for word_id in range(start, end + 1):
                    self.word_to_verse[word_id] = verse_id
            except:
                continue
        
        print(f"Loaded {len(self.words)} words, {len(self.verses)} verses")
    
    def direct_search(self, arabic_term: str, limit: int = 10):
        """Direct search in words dictionary"""
        results = []
        
        for word_id_str, arabic_word in self.words.items():
            if arabic_term in arabic_word:
                try:
                    word_id = int(word_id_str)
                    verse_id = self.word_to_verse.get(word_id)
                    
                    if verse_id:
                        verse_data = self.verses.get(str(verse_id), {})
                        
                        results.append({
                            'word_id': word_id,
                            'arabic': arabic_word,
                            'verse_id': verse_id,
                            'verse_arabic': verse_data.get('arabic', ''),
                            'translation': verse_data.get('en', '')
                        })
                        
                        if len(results) >= limit:
                            break
                except:
                    continue
        
        return results
    
    def answer_question(self, question: str):
        """Simple Q&A"""
        # Extract Arabic word from question
        arabic_pattern = re.compile(r'([\u0600-\u06FF]{2,})')
        matches = arabic_pattern.findall(question)
        
        if not matches:
            # Try common English terms
            english_map = {
                'allah': 'الله',
                'prayer': 'الصلاة',
                'charity': 'الزكاة',
                'fasting': 'الصيام',
                'paradise': 'الجنة',
                'hell': 'النار',
                'quran': 'القرآن'
            }
            
            question_lower = question.lower()
            for eng, arb in english_map.items():
                if eng in question_lower:
                    matches = [arb]
                    break
        
        if not matches:
            return {
                'success': False,
                'error': 'No Arabic term found in question',
                'suggestion': 'Try: الله, الصلاة, الزكاة'
            }
        
        arabic_term = matches[0]
        results = self.direct_search(arabic_term, limit=5)
        
        if not results:
            return {
                'success': False,
                'error': f'No verses found containing "{arabic_term}"'
            }
        
        # Format answer
        answer_lines = [f"Found {len(results)} verses with '{arabic_term}':\n"]
        
        for i, result in enumerate(results, 1):
            answer_lines.append(f"{i}. {result['verse_arabic']}")
            if result.get('translation'):
                answer_lines.append(f"   ({result['translation']})")
            answer_lines.append(f"   [Verse {result['verse_id']}]\n")
        
        return {
            'success': True,
            'term': arabic_term,
            'count': len(results),
            'answer': "\n".join(answer_lines)
        }

def main():
    """Main function"""
    print("Working Quran Q&A Engine")
    print("="*60)
    
    engine = WorkingQAEngine()
    
    print("\n" + "="*60)
    print("READY - Ask questions")
    print("="*60)
    
    while True:
        try:
            question = input("\n❓ Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if not question:
                continue
            
            result = engine.answer_question(question)
            
            print("\n" + "="*60)
            if result['success']:
                print(result['answer'])
            else:
                print(f"❌ {result['error']}")
                if 'suggestion' in result:
                    print(f"💡 {result['suggestion']}")
            print("="*60)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()