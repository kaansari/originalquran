#!/usr/bin/env python3
"""
Debug script for الصلاة search
"""

import json

def debug_salah():
    print("Debugging الصلاة Search")
    print("="*60)
    
    # Load words
    with open('quran_words.json', 'r', encoding='utf-8') as f:
        words = json.load(f)
    
    # Search for الصلاة
    search_terms = ['الصلاة', 'صلاة', 'صلوات', 'صلوه']
    
    for term in search_terms:
        print(f"\nSearching for '{term}':")
        found = []
        
        for word_id, arabic_word in words.items():
            if term == arabic_word:
                found.append((word_id, arabic_word))
        
        print(f"  Exact matches: {len(found)}")
        
        if found:
            for word_id, arabic_word in found[:5]:
                print(f"    {word_id}: {arabic_word}")
        
        # Try partial search
        partial_found = []
        for word_id, arabic_word in list(words.items())[:500]:  # First 500
            if term in arabic_word:
                partial_found.append((word_id, arabic_word))
        
        print(f"  Partial matches (in first 500): {len(partial_found)}")
        if partial_found:
            for word_id, arabic_word in partial_found[:3]:
                print(f"    {word_id}: {arabic_word}")
    
    print("\n" + "="*60)
    print("Checking specific word IDs around prayer concepts")
    print("="*60)
    
    # Check some specific word IDs that might contain prayer
    check_ids = ['5', '6', '7', '8', '100', '200', '300', '400', '500']
    
    for word_id in check_ids:
        if word_id in words:
            print(f"Word {word_id}: '{words[word_id]}'")
    
    print("\n" + "="*60)
    print("Searching for root letters ص ل و")
    print("="*60)
    
    # Search for words containing ص ل و letters
    words_with_sad = []
    for word_id, arabic_word in list(words.items())[:1000]:
        if 'ص' in arabic_word:
            words_with_sad.append((word_id, arabic_word))
    
    print(f"Words with 'ص' in first 1000: {len(words_with_sad)}")
    for word_id, arabic_word in words_with_sad[:10]:
        print(f"  {word_id}: {arabic_word}")

if __name__ == "__main__":
    debug_salah()