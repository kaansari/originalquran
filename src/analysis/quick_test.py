#!/usr/bin/env python3
"""
Quick test of the unified index
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_index import QuranUnifiedIndex

def quick_test():
    """Quick test with minimal output"""
    print("Quick test of Quran Unified Index")
    print("-" * 40)
    
    try:
        # Try to load data
        index = QuranUnifiedIndex(".")
        index.load_all_data()
        
        # Test a few things
        print("\nQuick tests:")
        
        # Test 1: Word 1
        word1 = index.get_word_info(1)
        print(f"1. Word 1: {word1['arabic'] if word1 else 'NOT FOUND'}")
        
        # Test 2: Verse 1
        verse1_words = index.get_verse_words(1)
        print(f"2. Verse 1 has {len(verse1_words)} words")
        
        # Test 3: Surah 1:1
        verse = index.get_sura_verse(1, 1)
        print(f"3. Surah 1:1: {verse['arabic'][:50] if verse else 'NOT FOUND'}...")
        
        print("\n✅ Quick test completed successfully!")
        
        # Show memory usage
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"\n📊 Memory usage: {memory_mb:.1f} MB")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()