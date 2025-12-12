#!/usr/bin/env python3
"""
Quran Unified Index System
Connects all data files using global word IDs
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

class QuranUnifiedIndex:
    """Unified index connecting all Quran data files"""


      # Add this method to the QuranUnifiedIndex class:

def _load_root_csv(self, csv_file: str = "root_words.txt"):
    """Load root words from CSV file"""
    print(f"   Loading root CSV: {csv_file}")
    
    import csv
    
    root_word_map = {}  # root → [words]
    word_root_map = {}  # word → [roots]
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Skip header if exists
            if f.read(5) == "Root,":
                f.seek(0)
                next(f)  # Skip header
        
            f.seek(0)
            reader = csv.reader(f)
            
            for row in reader:
                if len(row) < 3:
                    continue
                
                root = row[0].strip()
                word = row[1].strip()
                # count = row[2]  # We don't need count for indexing
                
                if not root or not word:
                    continue
                
                # Add to root → words map
                if root not in root_word_map:
                    root_word_map[root] = []
                if word not in root_word_map[root]:
                    root_word_map[root].append(word)
                
                # Add to word → roots map
                if word not in word_root_map:
                    word_root_map[word] = []
                if root not in word_root_map[word]:
                    word_root_map[word].append(root)
        
        print(f"   Loaded {len(root_word_map)} roots, {len(word_root_map)} unique words")
        
        # Update the existing root_index
        for root, words in root_word_map.items():
            # For each word, find its word_id(s) and add to root_index
            for word in words:
                # Search for this word in our words dictionary
                for word_id_str, arabic_word in self.words.items():
                    if word == arabic_word:
                        try:
                            word_id = int(word_id_str)
                            self.root_index[root].append(word_id)
                            self.stats['words_with_root'] += 1
                        except ValueError:
                            continue
        
        self.stats['unique_roots'] = len(root_word_map)
        
        # Store the maps for later use
        self.root_word_map = root_word_map
        self.word_root_map = word_root_map
        
    except FileNotFoundError:
        print(f"   Warning: CSV file {csv_file} not found")
    except Exception as e:
        print(f"   Error loading CSV: {e}")
    
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        
        # Core indices
        self.words = {}               # word_id → arabic_text
        self.word_translations = {}   # word_id → english_translation
        self.morphology = {}          # word_id → morphology_data
        self.verses = {}              # verse_id → verse_data
        self.suras = {}               # sura_id → sura_data
        
        # Derived indices
        self.word_to_verse = {}       # word_id → verse_id
        self.verse_to_words = {}      # verse_id → [word_ids]
        self.root_index = defaultdict(list)  # root → [word_ids]
        self.sura_verse_index = {}    # (sura, ayah) → verse_id
        
        # Statistics
        self.stats = {
            'total_words': 0,
            'total_verses': 0,
            'total_suras': 0,
            'words_with_morphology': 0,
            'words_with_translation': 0,
            'words_with_root': 0,
            'unique_roots': 0
        }
    
    def load_all_data(self):
        """Load all data files and build indices"""
        print("="*60)
        print("Loading Quran Data Files")
        print("="*60)
        
        try:
            # 1. Load quran_words.json
            print("1. Loading words...")
            with open(os.path.join(self.data_dir, 'quran_words.json'), 'r', encoding='utf-8') as f:
                self.words = json.load(f)
            self.stats['total_words'] = len(self.words)
            print(f"   Loaded {self.stats['total_words']} words")
            
            # 2. Load word translations
            print("2. Loading word translations...")
            word_trans_file = os.path.join(self.data_dir, 'word_translations.json')
            if os.path.exists(word_trans_file):
                with open(word_trans_file, 'r', encoding='utf-8') as f:
                    self.word_translations = json.load(f)
                self.stats['words_with_translation'] = len(self.word_translations)
                print(f"   Loaded {self.stats['words_with_translation']} word translations")
            else:
                print("   Word translations file not found, skipping")
            
            # 3. Load morphology
            print("3. Loading morphology...")
            with open(os.path.join(self.data_dir, 'morphology.json'), 'r', encoding='utf-8') as f:
                morph_data = json.load(f)
                
                # Convert keys to integers and store
                for key_str, value in morph_data.items():
                    try:
                        word_id = int(key_str)
                        self.morphology[word_id] = value
                    except ValueError:
                        print(f"   Warning: Non-integer key in morphology: {key_str}")
                        continue
                
                self.stats['words_with_morphology'] = len(self.morphology)
                print(f"   Loaded {self.stats['words_with_morphology']} morphology entries")
            
            # 4. Load verses
            print("4. Loading verses...")
            with open(os.path.join(self.data_dir, 'verses.json'), 'r', encoding='utf-8') as f:
                verses_data = json.load(f)
                
                for key_str, value in verses_data.items():
                    try:
                        verse_id = int(key_str)
                        self.verses[verse_id] = value
                    except ValueError:
                        print(f"   Warning: Non-integer key in verses: {key_str}")
                        continue
                
                self.stats['total_verses'] = len(self.verses)
                print(f"   Loaded {self.stats['total_verses']} verses")
            
            # 5. Load suras
            print("5. Loading suras...")
            with open(os.path.join(self.data_dir, 'sura.json'), 'r', encoding='utf-8') as f:
                sura_data = json.load(f)
                
                for key_str, value in sura_data.items():
                    try:
                        sura_id = int(key_str)
                        self.suras[sura_id] = value
                    except ValueError:
                        print(f"   Warning: Non-integer key in suras: {key_str}")
                        continue
                
                self.stats['total_suras'] = len(self.suras)
                print(f"   Loaded {self.stats['total_suras']} suras")
            
            # 6. Load root words (optional)
            print("6. Loading root words...")
            root_file = os.path.join(self.data_dir, 'root_words.json')
            if os.path.exists(root_file):
                with open(root_file, 'r', encoding='utf-8') as f:
                    root_data = json.load(f)
                self._build_root_index(root_data)
                print(f"   Loaded {self.stats['unique_roots']} unique roots")
                print(f"   Found {self.stats['words_with_root']} word-root mappings")
            else:
                print("   Root words file not found, skipping")

    # With this:
            print("6. Loading root words from CSV...")
            csv_file = os.path.join(self.data_dir, 'root_words.txt')
            self._load_root_csv(csv_file)
            
            # 8. Build derived indices
            print("7. Building derived indices...")
            self._build_derived_indices()
            
            print("\n" + "="*60)
            print("DATA LOADING COMPLETE")
            print("="*60)
            self.print_stats()
            
        except FileNotFoundError as e:
            print(f"\n❌ ERROR: File not found: {e}")
            print("\nRequired files in {data_dir}:")
            print("  - quran_words.json")
            print("  - morphology.json")
            print("  - verses.json")
            print("  - sura.json")
            print("\nOptional files:")
            print("  - word_translations.json")
            print("  - root_words.json")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"\n❌ ERROR: Invalid JSON: {e}")
            sys.exit(1)
    
    def _build_root_index(self, root_data: Dict):
        """Build index from root_words.json"""
        roots_found = set()
        words_with_root = 0
        
        for root, root_info in root_data.items():
            if 'Word' not in root_info:
                continue
                
            for derived_word, word_info in root_info['Word'].items():
                if 'Verses' not in word_info:
                    continue
                    
                for verse_ref in word_info['Verses']:
                    if 'Key' not in verse_ref:
                        continue
                    
                    try:
                        word_id = int(verse_ref['Key'])
                        # Add to root index
                        self.root_index[root].append(word_id)
                        roots_found.add(root)
                        words_with_root += 1
                    except ValueError:
                        # Skip non-integer keys
                        continue
        
        self.stats['unique_roots'] = len(roots_found)
        self.stats['words_with_root'] = words_with_root
    
    def _build_derived_indices(self):
        """Build derived lookup indices"""
        print("   Building word-to-verse mapping...")
        for verse_id, verse_data in self.verses.items():
            start = verse_data.get('start_word')
            end = verse_data.get('end_word')
            
            if start is None or end is None:
                continue
            
            # Ensure start and end are integers
            try:
                start_int = int(start)
                end_int = int(end)
            except (ValueError, TypeError):
                continue
            
            # Build verse_to_words
            word_ids = list(range(start_int, end_int + 1))
            self.verse_to_words[verse_id] = word_ids
            
            # Build word_to_verse
            for word_id in word_ids:
                self.word_to_verse[word_id] = verse_id
        
        print("   Building sura-verse index...")
        # Build (sura, ayah) → verse_id mapping
        for sura_id, sura_info in self.suras.items():
            start_verse = sura_info.get('start')
            end_verse = sura_info.get('end')
            n_ayah = sura_info.get('nAyah', 0)
            
            if start_verse and end_verse and n_ayah > 0:
                for ayah in range(1, n_ayah + 1):
                    verse_id = start_verse + ayah - 1
                    self.sura_verse_index[(sura_id, ayah)] = verse_id
        
        print("   Derived indices built successfully")
    
    def print_stats(self):
        """Print loading statistics"""
        print(f"\n📊 STATISTICS:")
        print(f"   Words: {self.stats['total_words']:,}")
        print(f"   Verses: {self.stats['total_verses']:,}")
        print(f"   Suras: {self.stats['total_suras']:,}")
        print(f"   Words with morphology: {self.stats['words_with_morphology']:,} ({self.stats['words_with_morphology']/self.stats['total_words']*100:.1f}%)")
        
        if self.stats['words_with_translation'] > 0:
            print(f"   Words with translation: {self.stats['words_with_translation']:,} ({self.stats['words_with_translation']/self.stats['total_words']*100:.1f}%)")
        
        if self.stats['unique_roots'] > 0:
            print(f"   Unique roots: {self.stats['unique_roots']:,}")
            print(f"   Word-root mappings: {self.stats['words_with_root']:,}")
        
        # Check for data integrity
        print(f"\n🔍 DATA INTEGRITY:")
        
        # Check word ranges - FIXED: Convert keys to integers
        word_keys = self.words.keys()
        if word_keys:
            # Convert all keys to integers and find max
            int_keys = []
            for key in word_keys:
                try:
                    int_keys.append(int(key))
                except (ValueError, TypeError):
                    continue
            
            if int_keys:
                max_word_id = max(int_keys)
                words_in_verses = sum(len(words) for words in self.verse_to_words.values())
                print(f"   Max word ID: {max_word_id}")
                print(f"   Words accounted in verses: {words_in_verses:,}")
                
                coverage = words_in_verses / max_word_id * 100
                print(f"   Coverage: {coverage:.1f}%")
            else:
                print(f"   No valid integer word IDs found")
        else:
            print(f"   No words loaded")
        
        # Check morphology coverage
        missing_morphology = []
        # Get max word ID safely
        max_id_to_check = 0
        if word_keys:
            try:
                # Get first 100 valid integer IDs
                int_keys = []
                for key in word_keys:
                    try:
                        int_keys.append(int(key))
                    except (ValueError, TypeError):
                        continue
                
                if int_keys:
                    max_id_to_check = min(100, max(int_keys))
                
                for word_id in range(1, max_id_to_check + 1):
                    if word_id not in self.morphology:
                        missing_morphology.append(word_id)
            except:
                pass
        
        if missing_morphology:
            print(f"   Missing morphology for words: {missing_morphology[:10]}{'...' if len(missing_morphology) > 10 else ''}")   
    # ===== QUERY METHODS =====
    def get_word_info(self, word_id: int) -> Optional[Dict]:
        """Get complete information for a word"""
        # Convert word_id to string for dictionary lookup
        word_id_str = str(word_id)
        
        if word_id_str not in self.words:
            return None
        
        info = {
            'word_id': word_id,
            'arabic': self.words.get(word_id_str),
            'translation': self.word_translations.get(word_id_str),  # Use string key
            'morphology': self.morphology.get(word_id),  # morphology uses int keys
            'verse_id': self.word_to_verse.get(word_id)  # word_to_verse uses int keys
        }
        
        # Add verse context if available
        if info['verse_id']:
            verse_data = self.verses.get(info['verse_id'], {})
            info['verse_arabic'] = verse_data.get('arabic')
            info['verse_translation'] = verse_data.get('en')
        
        # Add root information if available
        info['roots'] = []
        for root, word_ids in self.root_index.items():
            if word_id in word_ids:
                info['roots'].append(root)
        
        return info
    
    def get_verse_words(self, verse_id: int) -> List[Dict]:
        """Get all words in a verse with their information"""
        if verse_id not in self.verse_to_words:
            return []
        
        words_info = []
        for word_id in self.verse_to_words[verse_id]:
            word_info = self.get_word_info(word_id)
            if word_info:
                words_info.append(word_info)
        
        return words_info
    
    def find_words_by_root(self, root: str) -> List[Dict]:
        """Find all words derived from a root"""
        if root not in self.root_index:
            return []
        
        results = []
        for word_id in self.root_index[root]:
            word_info = self.get_word_info(word_id)
            if word_info:
                results.append(word_info)
        
        return results
    
    def search_by_arabic(self, arabic_text: str, exact: bool = False) -> List[Dict]:
        """Search for words by Arabic text"""
        results = []
        arabic_lower = arabic_text.strip()
        
        for word_id_str, text in self.words.items():
            # Convert string key to integer for get_word_info
            try:
                word_id = int(word_id_str)
            except ValueError:
                continue
            
            if exact:
                if text == arabic_lower:
                    word_info = self.get_word_info(word_id)
                    if word_info:
                        results.append(word_info)
            else:
                if arabic_lower in text:
                    word_info = self.get_word_info(word_id)
                    if word_info:
                        results.append(word_info)
        
        return results
    
    
   
    
    
    
    def analyze_verse_syntax(self, verse_id: int) -> List[Dict]:
        """Analyze syntactic structure of a verse"""
        words = self.get_verse_words(verse_id)
        
        for word_info in words:
            # Infer syntax role from morphology
            morph = word_info.get('morphology', {})
            if morph and 'words' in morph:
                # Get first subtoken's morphology (simplified)
                first_subtoken = next(iter(morph['words'].values()))
                word_info['syntax_role'] = self._infer_syntax_role(first_subtoken)
            else:
                word_info['syntax_role'] = 'unknown'
        
        return words
    
    def _infer_syntax_role(self, morph_data: Dict) -> str:
        """Infer syntax role from morphology data"""
        morph_str = morph_data.get('morphology', '')
        pos = morph_data.get('pos', '')
        
        # Simple inference rules
        if 'PREF' in morph_str:
            return 'preposition'
        elif 'GEN' in morph_str:
            if 'ADJ' in morph_str:
                return 'adjective'
            elif 'PN' in morph_str:
                return 'proper_noun'
            else:
                return 'noun_genitive'
        elif 'NOM' in morph_str:
            return 'noun_nominative'
        elif 'ACC' in morph_str:
            return 'noun_accusative'
        elif pos == 'V':
            return 'verb'
        elif pos == 'N':
            return 'noun'
        elif pos == 'P':
            return 'particle'
        
        return 'unknown'
    
   
    
    def get_sura_verse(self, sura: int, ayah: int) -> Optional[Dict]:
        """Get verse by sura and ayah number"""
        verse_id = self.sura_verse_index.get((sura, ayah))
        if not verse_id:
            return None
        
        verse_data = self.verses.get(verse_id, {}).copy()
        verse_data['verse_id'] = verse_id
        verse_data['sura'] = sura
        verse_data['ayah'] = ayah
        verse_data['words'] = self.get_verse_words(verse_id)
        
        return verse_data

def interactive_test(index: QuranUnifiedIndex):
    """Interactive testing of the index"""
    print("\n" + "="*60)
    print("INTERACTIVE TEST MODE")
    print("="*60)
    print("\nCommands:")
    print("  word [id]       - Show word information")
    print("  verse [id]      - Show verse with syntax analysis")
    print("  root [root]     - Find words by root")
    print("  search [text]   - Search Arabic text")
    print("  sura [s:aya]    - Get verse by sura:ayah")
    print("  stats           - Show statistics")
    print("  test            - Run automated tests")
    print("  quit            - Exit")
    print("-" * 60)
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'quit' or cmd == 'exit':
                break
            
            elif cmd == 'stats':
                index.print_stats()
            
            elif cmd == 'test':
                run_automated_tests(index)
            
            elif cmd.startswith('word '):
                try:
                    word_id = int(cmd[5:])
                    info = index.get_word_info(word_id)
                    if info:
                        print(f"\nWord ID: {word_id}")
                        print(f"Arabic: {info['arabic']}")
                        if info.get('translation'):
                            print(f"Translation: {info['translation']}")
                        if info.get('verse_id'):
                            print(f"Verse: {info['verse_id']}")
                            if info.get('verse_arabic'):
                                print(f"Verse text: {info['verse_arabic']}")
                        if info.get('roots'):
                            print(f"Roots: {', '.join(info['roots'])}")
                        if info.get('morphology'):
                            print(f"Morphology: {info['morphology'].get('id', 'N/A')}")
                    else:
                        print(f"Word ID {word_id} not found")
                except ValueError:
                    print("Invalid word ID")
            
            elif cmd.startswith('verse '):
                try:
                    verse_id = int(cmd[6:])
                    words = index.analyze_verse_syntax(verse_id)
                    if words:
                        verse_data = index.verses.get(verse_id, {})
                        print(f"\nVerse {verse_id}: {verse_data.get('arabic', 'N/A')}")
                        print(f"Translation: {verse_data.get('en', 'N/A')}")
                        print("\nSyntax Analysis:")
                        for word in words:
                            role = word.get('syntax_role', 'unknown')
                            print(f"  {word['arabic']} ({role})")
                    else:
                        print(f"Verse ID {verse_id} not found")
                except ValueError:
                    print("Invalid verse ID")
            
            elif cmd.startswith('root '):
                root = cmd[5:].strip()
                words = index.find_words_by_root(root)
                if words:
                    print(f"\nFound {len(words)} words with root '{root}':")
                    for word in words[:10]:  # Show first 10
                        print(f"  {word['word_id']}: {word['arabic']} (Verse {word['verse_id']})")
                    if len(words) > 10:
                        print(f"  ... and {len(words) - 10} more")
                else:
                    print(f"No words found with root '{root}'")
            
            elif cmd.startswith('search '):
                text = cmd[7:].strip()
                words = index.search_by_arabic(text)
                if words:
                    print(f"\nFound {len(words)} words containing '{text}':")
                    for word in words[:10]:  # Show first 10
                        print(f"  {word['word_id']}: {word['arabic']} (Verse {word['verse_id']})")
                    if len(words) > 10:
                        print(f"  ... and {len(words) - 10} more")
                else:
                    print(f"No words found containing '{text}'")
            
            elif cmd.startswith('sura '):
                try:
                    parts = cmd[5:].split(':')
                    if len(parts) != 2:
                        print("Format: sura s:aya (e.g., 'sura 1:1')")
                        continue
                    
                    sura = int(parts[0])
                    ayah = int(parts[1])
                    verse = index.get_sura_verse(sura, ayah)
                    
                    if verse:
                        print(f"\nSurah {sura}:{ayah} ({verse['verse_id']})")
                        print(f"Arabic: {verse.get('arabic', 'N/A')}")
                        print(f"Translation: {verse.get('en', 'N/A')}")
                    else:
                        print(f"Surah {sura}:{ayah} not found")
                except ValueError:
                    print("Invalid sura:ayah format")
            
            elif cmd:
                print("Unknown command. Type 'help' for commands list.")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

def run_automated_tests(index: QuranUnifiedIndex):
    """Run automated tests on the index"""
    print("\n" + "="*60)
    print("RUNNING AUTOMATED TESTS")
    print("="*60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Basic word lookup
    print("\n1. Testing word lookup...")
    word_info = index.get_word_info(1)
    if word_info and word_info['arabic'] == 'بسم':
        print("   ✓ Word 1 is 'بسم'")
        tests_passed += 1
    else:
        print("   ✗ Word 1 lookup failed")
        tests_failed += 1
    
    # Test 2: Verse words
    print("\n2. Testing verse words...")
    verse_words = index.get_verse_words(1)
    if len(verse_words) >= 4:
        print(f"   ✓ Verse 1 has {len(verse_words)} words")
        tests_passed += 1
    else:
        print(f"   ✗ Verse 1 has only {len(verse_words)} words")
        tests_failed += 1
    
    # Test 3: Root search (if roots loaded)
    if index.stats['unique_roots'] > 0:
        print("\n3. Testing root search...")
        # Try a common root like 'رحم'
        rahm_words = index.find_words_by_root('رحم')
        if rahm_words:
            print(f"   ✓ Found {len(rahm_words)} words with root 'رحم'")
            tests_passed += 1
        else:
            print("   ✗ No words found for root 'رحم'")
            tests_failed += 1
    
    # Test 4: Sura:ayah lookup
    print("\n4. Testing sura:ayah lookup...")
    verse = index.get_sura_verse(1, 1)
    if verse:
        print(f"   ✓ Surah 1:1 found as verse {verse['verse_id']}")
        tests_passed += 1
    else:
        print("   ✗ Surah 1:1 not found")
        tests_failed += 1
    
    # Test 5: Arabic search
    print("\n5. Testing Arabic search...")
    results = index.search_by_arabic('الله')
    if results:
        print(f"   ✓ Found {len(results)} occurrences of 'الله'")
        tests_passed += 1
    else:
        print("   ✗ No occurrences of 'الله' found")
        tests_failed += 1
    
    print("\n" + "="*60)
    print(f"TESTS COMPLETE: {tests_passed} passed, {tests_failed} failed")
    print("="*60)

def main():
    """Main function"""
    print("Quran Unified Index System")
    print("="*60)
    
    # Get data directory
    data_dir = input("Enter data directory path [default: current]: ").strip()
    if not data_dir:
        data_dir = "."
    
    # Build index
    index = QuranUnifiedIndex(data_dir)
    index.load_all_data()
    
    # Run interactive test
    interactive_test(index)
    
    print("\n" + "="*60)
    print("Thank you for using Quran Unified Index System")
    print("="*60)

if __name__ == "__main__":
    main()