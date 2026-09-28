#!/usr/bin/env python3
"""
Quran ID Mapping System
Handles conversion between different ID formats across files
"""

import json
from functools import lru_cache
from typing import Dict, Tuple, Optional
import os

class QuranIDMapper:
    """Maps between different Quran ID systems"""
    
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.sura_data = None
        self.verse_ranges = None  # verse_id -> (start_word, end_word)
        self._load_data()
    
    def _load_data(self):
        """Load necessary data files"""
        print("Loading data files...")
        
        # Load sura.json
        with open(os.path.join(self.data_dir, 'sura.json'), 'r', encoding='utf-8') as f:
            self.sura_data = json.load(f)
        
        # Load verses.json to build word ranges
        with open(os.path.join(self.data_dir, 'verses.json'), 'r', encoding='utf-8') as f:
            verses = json.load(f)
        
        # Build verse ranges lookup
        self.verse_ranges = {}
        for verse_id_str, verse_data in verses.items():
            verse_id = int(verse_id_str)
            self.verse_ranges[verse_id] = (
                verse_data['start_word'],
                verse_data['end_word']
            )
        
        print(f"Loaded {len(self.sura_data)} surahs, {len(self.verse_ranges)} verses")
    
    @lru_cache(maxsize=10000)
    def surah_ayah_to_verse_id(self, surah: int, ayah: int) -> Optional[int]:
        """Convert surah:ayah to sequential verse ID"""
        surah_key = str(surah)
        if surah_key not in self.sura_data:
            return None
        
        surah_info = self.sura_data[surah_key]
        start_verse = surah_info['start']
        end_verse = surah_info['end']
        
        # Validate ayah number
        if ayah < 1 or ayah > (end_verse - start_verse + 1):
            return None
        
        verse_id = start_verse + ayah - 1
        return verse_id
    
    @lru_cache(maxsize=10000)
    def verse_id_to_surah_ayah(self, verse_id: int) -> Optional[Tuple[int, int]]:
        """Convert sequential verse ID to surah:ayah"""
        # Find which surah contains this verse
        for surah_key, surah_info in self.sura_data.items():
            if surah_info['start'] <= verse_id <= surah_info['end']:
                surah = int(surah_key)
                ayah = verse_id - surah_info['start'] + 1
                return surah, ayah
        return None
    
    def parse_root_id(self, root_id: str) -> Optional[Tuple[int, int, int]]:
        """
        Parse root_words.json ID format "surah:ayah:word_position"
        Returns: (surah, ayah, word_position) or None
        """
        try:
            parts = root_id.split(':')
            if len(parts) != 3:
                return None
            
            surah = int(parts[0])
            ayah = int(parts[1])
            word_pos = int(parts[2])
            
            return surah, ayah, word_pos
        except (ValueError, IndexError):
            return None
    
    def root_id_to_global_word_id(self, root_id: str) -> Optional[int]:
        """
        Convert "surah:ayah:word_position" to global word ID
        """
        parsed = self.parse_root_id(root_id)
        if not parsed:
            return None
        
        surah, ayah, word_pos = parsed
        
        # Get verse ID
        verse_id = self.surah_ayah_to_verse_id(surah, ayah)
        if not verse_id:
            return None
        
        # Get word range for this verse
        if verse_id not in self.verse_ranges:
            return None
        
        start_word, end_word = self.verse_ranges[verse_id]
        
        # Calculate global word ID
        if word_pos < 1:
            return None
        
        global_word_id = start_word + word_pos - 1
        
        # Validate
        if global_word_id > end_word:
            return None
        
        return global_word_id
    
    def global_word_id_to_root_id(self, global_word_id: int) -> Optional[str]:
        """
        Convert global word ID to "surah:ayah:word_position"
        """
        # Find which verse contains this word
        verse_id = None
        word_pos_in_verse = None
        
        for v_id, (start, end) in self.verse_ranges.items():
            if start <= global_word_id <= end:
                verse_id = v_id
                word_pos_in_verse = global_word_id - start + 1
                break
        
        if not verse_id:
            return None
        
        # Convert verse_id to surah:ayah
        surah_ayah = self.verse_id_to_surah_ayah(verse_id)
        if not surah_ayah:
            return None
        
        surah, ayah = surah_ayah
        return f"{surah}:{ayah}:{word_pos_in_verse}"
    
    def test_mappings(self):
        """Test the ID mapping system with sample data"""
        print("\n" + "="*60)
        print("Testing ID Mappings")
        print("="*60)
        
        # Test cases
        test_cases = [
            ("74:51:3", "Known verse from root_words.json"),
            ("1:1:1", "First word of Quran"),
            ("114:6:3", "Last surah"),
        ]
        
        for root_id, description in test_cases:
            print(f"\nTest: {description}")
            print(f"  Root ID: {root_id}")
            
            # Parse
            parsed = self.parse_root_id(root_id)
            if parsed:
                surah, ayah, word_pos = parsed
                print(f"  Parsed: surah={surah}, ayah={ayah}, word_pos={word_pos}")
                
                # Convert to verse ID
                verse_id = self.surah_ayah_to_verse_id(surah, ayah)
                print(f"  Verse ID: {verse_id}")
                
                # Convert to global word ID
                word_id = self.root_id_to_global_word_id(root_id)
                print(f"  Global Word ID: {word_id}")
                
                # Round-trip test
                if word_id:
                    round_trip = self.global_word_id_to_root_id(word_id)
                    print(f"  Round-trip: {round_trip}")
                    if round_trip == root_id:
                        print("  ✓ Round-trip successful")
                    else:
                        print(f"  ✗ Round-trip mismatch: {round_trip}")
            else:
                print(f"  ✗ Failed to parse: {root_id}")
        
        print("\n" + "="*60)
        print("Quick performance test...")
        
        # Test cache performance
        import time
        start = time.time()
        
        # Repeated calls should be fast due to caching
        for _ in range(1000):
            self.root_id_to_global_word_id("74:51:3")
        
        elapsed = time.time() - start
        print(f"1000 lookups: {elapsed:.3f} seconds ({elapsed*1000:.1f} ms per call)")

def main():
    """Main function to test the ID mapper"""
    print("Quran ID Mapping System")
    print("="*60)
    
    try:
        mapper = QuranIDMapper()
        mapper.test_mappings()
        
        # Interactive mode
        print("\n" + "="*60)
        print("Interactive Mode (Ctrl+C to exit)")
        print("="*60)
        
        while True:
            try:
                user_input = input("\nEnter ID (format: surah:ayah:word or 'test'): ").strip()
                
                if user_input.lower() == 'quit':
                    break
                
                if user_input.lower() == 'test':
                    mapper.test_mappings()
                    continue
                
                if ':' in user_input:
                    # Try as root ID
                    word_id = mapper.root_id_to_global_word_id(user_input)
                    if word_id:
                        print(f"Global Word ID: {word_id}")
                        
                        # Show round-trip
                        round_trip = mapper.global_word_id_to_root_id(word_id)
                        print(f"Round-trip: {round_trip}")
                    else:
                        print("Invalid ID format or out of range")
                else:
                    # Try as global word ID
                    try:
                        word_id = int(user_input)
                        root_id = mapper.global_word_id_to_root_id(word_id)
                        if root_id:
                            print(f"Root ID: {root_id}")
                        else:
                            print(f"Word ID {word_id} out of range (1-77430)")
                    except ValueError:
                        print("Enter either 'surah:ayah:word' or numeric word ID")
                        
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
                
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure all data files are in the current directory:")
        print("  - sura.json")
        print("  - verses.json")
        print("Place them in the same directory as this script or update data_dir.")

if __name__ == "__main__":
    main()