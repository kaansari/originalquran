#!/usr/bin/env python3
"""
Fixed Quran Q&A Engine with better concept detection
"""

import re
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

class QuranQAFixed:
    """Fixed Quran Question Answering Engine"""
    
    def __init__(self, unified_index, syntax_parser):
        self.index = unified_index
        self.parser = syntax_parser
        
        # Simplified concept mapping - focus on exact Arabic matches
        self.concept_map = {
            'الله': ['الله', 'رب', 'الإله'],
            'الصلاة': ['الصلاة', 'صلاة'],
            'الزكاة': ['الزكاة', 'زكاة'],
            'الصيام': ['الصيام', 'الصوم', 'صيام', 'صوم'],
            'الجنة': ['الجنة'],
            'النار': ['النار'],
            'القرآن': ['القرآن', 'الكتاب'],
            'يوم القيامة': ['يوم القيامة', 'يوم الدين'],
        }
        
        # English to Arabic mapping
        self.english_to_arabic = {
            'allah': 'الله',
            'god': 'الله',
            'prayer': 'الصلاة',
            'salat': 'الصلاة',
            'charity': 'الزكاة',
            'zakat': 'الزكاة',
            'fasting': 'الصيام',
            'sawm': 'الصيام',
            'paradise': 'الجنة',
            'jannah': 'الجنة',
            'hell': 'النار',
            'jahannam': 'النار',
            'quran': 'القرآن',
            'judgment day': 'يوم القيامة',
            'qiyamah': 'يوم القيامة',
        }
        
        # Answer templates
        self.templates = {
            'ar': {
                'definition': "تعريف {concept} في القرآن:\n\n{verses}",
                'attributes': "صفات {concept} في القرآن:\n\n{verses}",
                'how_to': "كيفية {concept} في القرآن:\n\n{verses}",
                'general': "آيات عن {concept} في القرآن:\n\n{verses}",
            },
            'en': {
                'definition': "Definition of {concept} in Quran:\n\n{verses}",
                'attributes': "Attributes of {concept} in Quran:\n\n{verses}",
                'how_to': "How to {concept} according to Quran:\n\n{verses}",
                'general': "Verses about {concept} in Quran:\n\n{verses}",
            }
        }
    
    def detect_language(self, text: str) -> str:
        """Detect if text is Arabic or English"""
        arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        if arabic_pattern.search(text):
            return 'ar'
        return 'en'
    
    def extract_arabic_word(self, text: str) -> Optional[str]:
        """Extract Arabic word from text"""
        arabic_pattern = re.compile(r'([\u0600-\u06FF]{2,})')
        matches = arabic_pattern.findall(text)
        
        if matches:
            # Return the longest Arabic word found
            return max(matches, key=len)
        return None
    
    def extract_concept(self, question: str) -> Tuple[Optional[str], str]:
        """Extract primary concept from question"""
        lang = self.detect_language(question)
        
        if lang == 'ar':
            # Try to extract Arabic word
            arabic_word = self.extract_arabic_word(question)
            if arabic_word:
                # Check if it's a known concept
                for concept, variations in self.concept_map.items():
                    if arabic_word in variations:
                        return concept, lang
                # Return the Arabic word itself
                return arabic_word, lang
        
        else:  # English
            question_lower = question.lower()
            
            # Check for English terms
            for eng_term, arabic_concept in self.english_to_arabic.items():
                if eng_term in question_lower:
                    return arabic_concept, lang
            
            # Try to find any Arabic word even in English question
            arabic_word = self.extract_arabic_word(question)
            if arabic_word:
                return arabic_word, lang
        
        return None, lang
    
    def find_verses_simple(self, arabic_concept: str, limit: int = 10) -> List[Dict]:
        """Simple verse finding by Arabic text search"""
        verses_found = []
        seen_ids = set()
        
        # Search for the concept
        search_results = self.index.search_by_arabic(arabic_concept)
        
        for word_info in search_results:
            verse_id = word_info.get('verse_id')
            if not verse_id or verse_id in seen_ids:
                continue
            
            verse_data = self.index.verses.get(verse_id, {})
            if not verse_data:
                continue
            
            verses_found.append({
                'verse_id': verse_id,
                'arabic': verse_data.get('arabic', ''),
                'translation': verse_data.get('en', ''),
                'context': self.get_verse_context(verse_id, arabic_concept)
            })
            
            seen_ids.add(verse_id)
            
            if len(verses_found) >= limit:
                break
        
        return verses_found
    
    def get_verse_context(self, verse_id: int, search_term: str) -> str:
        """Get context around search term in verse"""
        verse_data = self.index.verses.get(verse_id, {})
        verse_text = verse_data.get('arabic', '')
        
        # Find position of search term
        pos = verse_text.find(search_term)
        if pos == -1:
            return ""
        
        # Get context (words before and after)
        words = verse_text.split()
        for i, word in enumerate(words):
            if search_term in word:
                start = max(0, i - 2)
                end = min(len(words), i + 3)
                context_words = words[start:end]
                return " ".join(context_words)
        
        return ""
    
    def detect_intent_simple(self, question: str, lang: str) -> str:
        """Simple intent detection"""
        question_lower = question.lower()
        
        if lang == 'ar':
            if any(word in question for word in ['ما هو', 'ما هي', 'تعريف', 'ماهو', 'ماهي']):
                return 'definition'
            elif any(word in question for word in ['صفات', 'أسماء', 'صفة']):
                return 'attributes'
            elif any(word in question for word in ['كيف', 'طريقة', 'كيفية']):
                return 'how_to'
        
        else:  # English
            if any(phrase in question_lower for phrase in ['what is', 'what are', 'define', 'definition']):
                return 'definition'
            elif 'attribute' in question_lower or 'name of' in question_lower:
                return 'attributes'
            elif 'how to' in question_lower or 'how do' in question_lower:
                return 'how_to'
        
        return 'general'
    
    def format_verse(self, verse: Dict, lang: str) -> str:
        """Format verse for display"""
        if lang == 'ar':
            return f"• {verse['arabic']}\n  ({verse.get('translation', '')}) [الآية {verse['verse_id']}]"
        else:
            return f"• {verse['arabic']}\n  ({verse.get('translation', '')}) [Verse {verse['verse_id']}]"
    
    def answer_question(self, question: str) -> Dict:
        """Main Q&A function"""
        # Extract concept and language
        concept, lang = self.extract_concept(question)
        
        if not concept:
            error_msg = {
                'ar': 'لم أتمكن من فهم المفهوم الذي تبحث عنه. حاول استخدام كلمة عربية واضحة.',
                'en': 'Could not understand the concept you\'re asking about. Try using a clear Arabic word.'
            }
            return {
                'success': False,
                'error': error_msg[lang],
                'suggestions': list(self.concept_map.keys())[:5]
            }
        
        # Detect intent
        intent = self.detect_intent_simple(question, lang)
        
        # Find verses
        verses = self.find_verses_simple(concept, limit=8 if intent == 'general' else 5)
        
        if not verses:
            error_msg = {
                'ar': f'لم أجد آيات تحتوي على "{concept}"',
                'en': f'No verses found containing "{concept}"'
            }
            return {
                'success': False,
                'error': error_msg[lang],
                'concept': concept
            }
        
        # Format verses
        formatted_verses = "\n\n".join([self.format_verse(v, lang) for v in verses])
        
        # Select template
        template = self.templates[lang][intent]
        answer_text = template.format(
            concept=concept,
            verses=formatted_verses
        )
        
        # Add analysis note if we have syntax parser
        try:
            if verses and self.parser:
                first_verse = verses[0]
                analysis = self.parser.analyze_verse_syntax(first_verse['verse_id'])
                if 'summary' in analysis:
                    note = {
                        'ar': f"\n\n📝 تحليل نحوي: {analysis['summary']}",
                        'en': f"\n\n📝 Syntax analysis: {analysis['summary']}"
                    }
                    answer_text += note[lang]
        except:
            pass  # Skip if parser fails
        
        return {
            'success': True,
            'question': question,
            'language': lang,
            'concept': concept,
            'intent': intent,
            'verses_found': len(verses),
            'answer': answer_text
        }

def run_simple_tests(engine: QuranQAFixed):
    """Run simple Q&A tests"""
    print("\n" + "="*70)
    print("RUNNING SIMPLE Q&A TESTS")
    print("="*70)
    
    test_questions = [
        ("ما هو الله؟", "ar"),
        ("الله", "ar"),
        ("الصلاة", "ar"),
        ("What is Allah?", "en"),
        ("prayer", "en"),
        ("الزكاة", "ar"),
    ]
    
    passed = 0
    failed = 0
    
    for question, expected_lang in test_questions:
        print(f"\nTesting: '{question}'")
        
        try:
            result = engine.answer_question(question)
            
            if not result['success']:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
                failed += 1
                continue
            
            # Check language detection
            if result['language'] != expected_lang:
                print(f"  ✗ Language mismatch: expected {expected_lang}, got {result['language']}")
                failed += 1
                continue
            
            # Check if we found verses
            if result['verses_found'] == 0:
                print(f"  ✗ No verses found")
                failed += 1
                continue
            
            print(f"  ✓ Success: {result['verses_found']} verses found")
            print(f"     Concept: {result['concept']}")
            print(f"     Intent: {result['intent']}")
            
            # Show first verse snippet
            if result['verses_found'] > 0:
                lines = result['answer'].split('\n')
                if len(lines) > 1:
                    print(f"     Sample: {lines[1][:60]}...")
            
            passed += 1
            
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"Q&A TESTS COMPLETE: {passed} passed, {failed} failed")
    print("="*70)

def interactive_qa_simple(engine: QuranQAFixed):
    """Simple interactive Q&A"""
    print("\n" + "="*70)
    print("SIMPLE QURAN Q&A")
    print("="*70)
    print("\nAsk questions about Quranic concepts in Arabic or English")
    print("Examples: 'الله', 'الصلاة', 'What is prayer?', 'الزكاة'")
    print("\nType 'quit' to exit")
    print("-" * 70)
    
    while True:
        try:
            question = input("\n❓ سؤالك / Your question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'خروج']:
                print("\nمع السلامة / Goodbye!")
                break
            
            print("\n" + "="*70)
            result = engine.answer_question(question)
            
            if not result['success']:
                print(f"❌ {result['error']}")
                if 'suggestions' in result:
                    print(f"💡 Try: {', '.join(result['suggestions'])}")
            else:
                print(f"📊 Found {result['verses_found']} verses about '{result['concept']}'")
                print("="*70)
                print(result['answer'])
            
            print("="*70)
            
        except KeyboardInterrupt:
            print("\n\nمع السلامة / Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main function"""
    print("Simple Quran Q&A Engine (Fixed)")
    print("="*70)
    
    try:
        from unified_index import QuranUnifiedIndex
        from syntax_parser import QuranSyntaxParser
        
        # Load data
        print("Loading Quran data...")
        index = QuranUnifiedIndex(".")
        index.load_all_data()
        
        # Initialize parser
        print("Initializing syntax parser...")
        parser = QuranSyntaxParser(index)
        
        # Create Q&A engine
        print("Initializing Q&A engine...")
        engine = QuranQAFixed(index, parser)
        
        print("\n✅ System ready!")
        
        # Run tests
        run_test = input("\nRun tests first? (y/n): ").strip().lower()
        if run_test == 'y':
            run_simple_tests(engine)
        
        # Start interactive Q&A
        interactive_qa_simple(engine)
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()