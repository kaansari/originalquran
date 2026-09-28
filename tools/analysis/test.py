#!/usr/bin/env python3
"""
Create minimal test data for the ID mapper
"""

import json
import os

def create_test_files():
    """Create minimal versions of required files for testing"""
    
    # Create minimal sura.json (first 3 surahs)
    sura_data = {
        "1": {
            "name": "الفاتحة",
            "nAyah": 7,
            "revelationOrder": 5,
            "type": "meccan",
            "start": 1,
            "end": 7
        },
        "2": {
            "name": "البقرة",
            "nAyah": 286,
            "revelationOrder": 87,
            "type": "medinan",
            "start": 8,
            "end": 293
        },
        "74": {
            "name": "المدثر",
            "nAyah": 56,
            "revelationOrder": 4,
            "type": "meccan",
            "start": 5556,
            "end": 5611
        }
    }
    
    # Create minimal verses.json (first 10 verses + surah 74:51)
    verses_data = {}
    
    # First 7 verses (Surah 1)
    for i in range(1, 8):
        verses_data[str(i)] = {
            "arabic": f"Verse {i} Arabic",
            "en": f"Verse {i} English",
            "start_word": (i-1)*4 + 1,
            "end_word": i*4
        }
    
    # Verse 5606 (Surah 74:51)
    verses_data["5606"] = {
        "arabic": "Verse 74:51 Arabic",
        "en": "Verse 74:51 English",
        "start_word": 74621,  # Made up for testing
        "end_word": 74625     # Made up for testing
    }
    
    # Save files
    os.makedirs("test_data", exist_ok=True)
    
    with open("test_data/sura.json", "w", encoding="utf-8") as f:
        json.dump(sura_data, f, indent=2, ensure_ascii=False)
    
    with open("test_data/verses.json", "w", encoding="utf-8") as f:
        json.dump(verses_data, f, indent=2, ensure_ascii=False)
    
    print("Test files created in 'test_data/' directory")
    print("To test: python id_mapper.py (from test_data directory)")

if __name__ == "__main__":
    create_test_files()