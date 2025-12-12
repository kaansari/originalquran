#!/usr/bin/env python3
"""
Quran Syntax Parser
Analyzes morphology data to understand grammatical structure
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

class SyntaxRole(Enum):
    """Arabic grammatical roles"""
    SUBJECT = "subject"          # فاعل / مبتدأ
    PREDICATE = "predicate"      # خبر
    OBJECT = "object"            # مفعول به
    PREPOSITION = "preposition"  # حرف جر
    NOUN_GENITIVE = "noun_genitive"    # اسم مجرور
    NOUN_NOMINATIVE = "noun_nominative" # اسم مرفوع
    NOUN_ACCUSATIVE = "noun_accusative" # اسم منصوب
    ADJECTIVE = "adjective"      # صفة
    VERB = "verb"                # فعل
    PARTICLE = "particle"        # حرف
    UNKNOWN = "unknown"

class Case(Enum):
    """Arabic grammatical cases"""
    NOMINATIVE = "nominative"    # مرفوع
    ACCUSATIVE = "accusative"    # منصوب
    GENITIVE = "genitive"        # مجرور
    UNKNOWN = "unknown"

class Number(Enum):
    """Arabic grammatical numbers"""
    SINGULAR = "singular"        # مفرد
    DUAL = "dual"                # مثنى
    PLURAL = "plural"            # جمع
    UNKNOWN = "unknown"

class Gender(Enum):
    """Arabic grammatical genders"""
    MASCULINE = "masculine"      # مذكر
    FEMININE = "feminine"        # مؤنث
    UNKNOWN = "unknown"

class QuranSyntaxParser:
    """Parses Quranic Arabic syntax from morphology data"""
    
    def __init__(self, unified_index):
        self.index = unified_index
        
        # Morphology tag mappings
        self.case_markers = {
            'NOM': Case.NOMINATIVE,
            'ACC': Case.ACCUSATIVE,
            'GEN': Case.GENITIVE,
        }
        
        self.number_markers = {
            'S': Number.SINGULAR,
            'D': Number.DUAL,
            'P': Number.PLURAL,
            'MS': Number.SINGULAR,  # Masculine Singular
            'FS': Number.SINGULAR,  # Feminine Singular
            'MD': Number.DUAL,      # Masculine Dual
            'FD': Number.DUAL,      # Feminine Dual
            'MP': Number.PLURAL,    # Masculine Plural
            'FP': Number.PLURAL,    # Feminine Plural
        }
        
        self.gender_markers = {
            'M': Gender.MASCULINE,
            'F': Gender.FEMININE,
            'MS': Gender.MASCULINE,
            'FS': Gender.FEMININE,
            'MD': Gender.MASCULINE,
            'FD': Gender.FEMININE,
            'MP': Gender.MASCULINE,
            'FP': Gender.FEMININE,
        }
    
    def parse_morphology_tag(self, morph_tag: str) -> Dict[str, Any]:
        """Parse morphology tag into grammatical features"""
        if not morph_tag:
            return {}
        
        parts = morph_tag.split('|')
        features = {
            'raw': morph_tag,
            'parts': parts,
            'case': Case.UNKNOWN,
            'number': Number.UNKNOWN,
            'gender': Gender.UNKNOWN,
            'is_adjective': False,
            'is_particle': False,
            'is_verb': False,
            'is_noun': False,
            'is_preposition': False,
            'is_determiner': False,
            'is_proper_noun': False,
            'is_participle': False,
        }
        
        for part in parts:
            # Check for case
            for marker, case_enum in self.case_markers.items():
                if marker in part:
                    features['case'] = case_enum
            
            # Check for number
            for marker, number_enum in self.number_markers.items():
                if marker == part or (len(part) > 1 and marker in part):
                    features['number'] = number_enum
            
            # Check for gender
            for marker, gender_enum in self.gender_markers.items():
                if marker == part or (len(part) > 1 and marker in part):
                    features['gender'] = gender_enum
            
            # Check for word type indicators
            if 'ADJ' in part:
                features['is_adjective'] = True
                features['is_noun'] = True
            elif 'PN' in part:
                features['is_proper_noun'] = True
                features['is_noun'] = True
            elif 'PREF' in part or 'PRT' in part:
                features['is_particle'] = True
            elif 'DET' in part:
                features['is_determiner'] = True
            elif 'P' in part and len(part) == 1:
                features['is_particle'] = True
            elif 'V' in part:
                features['is_verb'] = True
            elif 'N' in part and len(part) == 1:
                features['is_noun'] = True
            elif 'ACT_PCPL' in part or 'PASS_PCPL' in part:
                features['is_participle'] = True
                features['is_noun'] = True
            elif 'IMPF' in part or 'PERF' in part:
                features['is_verb'] = True
        
        return features
    
    def infer_syntax_role(self, word_data: Dict, context: List[Dict] = None) -> SyntaxRole:
        """Infer syntax role from morphology and context"""
        morph = word_data.get('morphology', {})
        if not morph or 'words' not in morph:
            return SyntaxRole.UNKNOWN
        
        # Get first subtoken (most representative)
        first_subtoken = next(iter(morph['words'].values()))
        morph_tag = first_subtoken.get('morphology', '')
        pos = first_subtoken.get('pos', '')
        
        # Parse morphology tag
        features = self.parse_morphology_tag(morph_tag)
        
        # Determine syntax role based on features
        if features.get('is_particle'):
            if 'PREF' in morph_tag:
                return SyntaxRole.PREPOSITION
            return SyntaxRole.PARTICLE
        
        elif features.get('is_verb'):
            return SyntaxRole.VERB
        
        elif features.get('is_noun'):
            case = features.get('case')
            
            if case == Case.NOMINATIVE:
                # Check if this could be subject or predicate
                if context:
                    # Simple heuristic: first nominal in sentence is often subject
                    position = context.index(word_data) if word_data in context else 0
                    if position == 0:
                        return SyntaxRole.SUBJECT
                    else:
                        return SyntaxRole.PREDICATE
                return SyntaxRole.SUBJECT
            
            elif case == Case.ACCUSATIVE:
                return SyntaxRole.OBJECT
            
            elif case == Case.GENITIVE:
                if features.get('is_adjective'):
                    return SyntaxRole.ADJECTIVE
                elif features.get('is_proper_noun'):
                    return SyntaxRole.NOUN_GENITIVE
                else:
                    return SyntaxRole.NOUN_GENITIVE
            
            else:
                # Default noun roles
                if features.get('is_adjective'):
                    return SyntaxRole.ADJECTIVE
                else:
                    return SyntaxRole.NOUN_NOMINATIVE
        
        return SyntaxRole.UNKNOWN
    
    def analyze_verse_syntax(self, verse_id: int) -> Dict:
        """Complete syntax analysis of a verse"""
        # Get all words in verse
        words_info = self.index.get_verse_words(verse_id)
        if not words_info:
            return {'verse_id': verse_id, 'error': 'Verse not found'}
        
        # First pass: basic syntax roles
        syntax_analysis = []
        for word_info in words_info:
            role = self.infer_syntax_role(word_info, words_info)
            
            # Get additional grammatical features
            morph = word_info.get('morphology', {})
            gram_features = {}
            if morph and 'words' in morph:
                first_subtoken = next(iter(morph['words'].values()))
                gram_features = self.parse_morphology_tag(
                    first_subtoken.get('morphology', '')
                )
            
            syntax_analysis.append({
                'word_id': word_info['word_id'],
                'arabic': word_info['arabic'],
                'translation': word_info.get('translation'),
                'syntax_role': role.value,
                'grammatical_features': {
                    'case': gram_features.get('case', Case.UNKNOWN).value,
                    'number': gram_features.get('number', Number.UNKNOWN).value,
                    'gender': gram_features.get('gender', Gender.UNKNOWN).value,
                    'is_adjective': gram_features.get('is_adjective', False),
                    'is_proper_noun': gram_features.get('is_proper_noun', False),
                    'is_verb': gram_features.get('is_verb', False),
                    'is_particle': gram_features.get('is_particle', False),
                },
                'morphology': word_info.get('morphology', {}).get('id', ''),
                'roots': word_info.get('roots', [])
            })
        
        # Second pass: identify relationships
        relationships = self._identify_relationships(syntax_analysis)
        
        # Third pass: identify sentence structure
        sentence_structure = self._identify_sentence_structure(syntax_analysis)
        
        return {
            'verse_id': verse_id,
            'verse_text': self.index.verses.get(verse_id, {}).get('arabic', ''),
            'translation': self.index.verses.get(verse_id, {}).get('en', ''),
            'word_count': len(syntax_analysis),
            'syntax_analysis': syntax_analysis,
            'relationships': relationships,
            'sentence_structure': sentence_structure,
            'summary': self._generate_summary(syntax_analysis, relationships)
        }
    
    def _identify_relationships(self, syntax_analysis: List[Dict]) -> List[Dict]:
        """Identify grammatical relationships between words"""
        relationships = []
        
        for i, word in enumerate(syntax_analysis):
            role = word['syntax_role']
            
            # Look for construct state (إضافة)
            if role == 'noun_genitive' and i > 0:
                prev_word = syntax_analysis[i - 1]
                if prev_word['syntax_role'] in ['noun_nominative', 'noun_genitive', 'subject']:
                    relationships.append({
                        'type': 'construct_state',
                        'head': prev_word['word_id'],
                        'dependent': word['word_id'],
                        'description': f"{prev_word['arabic']} مضاف إلى {word['arabic']}"
                    })
            
            # Look for adjectives (صفة)
            if role == 'adjective' and i > 0:
                prev_word = syntax_analysis[i - 1]
                if prev_word['syntax_role'] in ['noun_nominative', 'noun_genitive', 'subject', 'object']:
                    relationships.append({
                        'type': 'adjective_modification',
                        'head': prev_word['word_id'],
                        'dependent': word['word_id'],
                        'description': f"{word['arabic']} صفة لـ {prev_word['arabic']}"
                    })
            
            # Look for prepositional phrases
            if role == 'preposition' and i < len(syntax_analysis) - 1:
                next_word = syntax_analysis[i + 1]
                if next_word['syntax_role'] == 'noun_genitive':
                    relationships.append({
                        'type': 'prepositional_phrase',
                        'preposition': word['word_id'],
                        'object': next_word['word_id'],
                        'description': f"{word['arabic']} {next_word['arabic']} (جار ومجرور)"
                    })
        
        return relationships
    
    def _identify_sentence_structure(self, syntax_analysis: List[Dict]) -> Dict:
        """Identify the overall sentence structure"""
        structure = {
            'type': 'unknown',
            'has_verb': False,
            'has_subject': False,
            'has_predicate': False,
            'has_object': False,
            'nominal_sentence': False,
            'verbal_sentence': False
        }
        
        roles = [word['syntax_role'] for word in syntax_analysis]
        
        # Check for verbal sentence (جملة فعلية)
        if 'verb' in roles:
            structure['has_verb'] = True
            structure['verbal_sentence'] = True
            structure['type'] = 'verbal_sentence'
            
            # Look for subject after verb
            verb_index = roles.index('verb') if 'verb' in roles else -1
            if verb_index >= 0 and verb_index < len(roles) - 1:
                if roles[verb_index + 1] == 'subject':
                    structure['has_subject'] = True
        
        # Check for nominal sentence (جملة اسمية)
        elif 'subject' in roles and 'predicate' in roles:
            structure['has_subject'] = True
            structure['has_predicate'] = True
            structure['nominal_sentence'] = True
            structure['type'] = 'nominal_sentence'
        
        # Check for object
        if 'object' in roles:
            structure['has_object'] = True
        
        return structure
    
    def _generate_summary(self, syntax_analysis: List[Dict], relationships: List[Dict]) -> str:
        """Generate a human-readable summary of the syntax analysis"""
        summary_parts = []
        
        # Count roles
        role_counts = {}
        for word in syntax_analysis:
            role = word['syntax_role']
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Add role summary
        if role_counts:
            summary_parts.append("Roles: " + ", ".join([
                f"{count} {role}" for role, count in role_counts.items()
            ]))
        
        # Add relationship summary
        if relationships:
            rel_types = {}
            for rel in relationships:
                rel_type = rel['type']
                rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
            
            summary_parts.append("Relationships: " + ", ".join([
                f"{count} {rel_type}" for rel_type, count in rel_types.items()
            ]))
        
        # Identify key patterns
        has_construct = any(r['type'] == 'construct_state' for r in relationships)
        has_adjective = any(r['type'] == 'adjective_modification' for r in relationships)
        has_preposition = any(r['type'] == 'prepositional_phrase' for r in relationships)
        
        pattern_parts = []
        if has_construct:
            pattern_parts.append("إضافة (construct state)")
        if has_adjective:
            pattern_parts.append("صفة (adjective modification)")
        if has_preposition:
            pattern_parts.append("جار ومجرور (prepositional phrase)")
        
        if pattern_parts:
            summary_parts.append("Patterns: " + ", ".join(pattern_parts))
        
        return "; ".join(summary_parts)
    
    def find_by_syntax_pattern(self, pattern: Dict) -> List[Dict]:
        """Find verses matching specific syntax patterns"""
        results = []
        
        # Simple pattern matching for now
        # Example pattern: {'roles': ['preposition', 'noun_genitive']}
        
        for verse_id in range(1, min(100, self.index.stats['total_verses']) + 1):  # Limit to first 100
            analysis = self.analyze_verse_syntax(verse_id)
            
            if 'error' in analysis:
                continue
            
            roles = [word['syntax_role'] for word in analysis['syntax_analysis']]
            
            # Check if pattern matches
            if 'roles' in pattern:
                pattern_roles = pattern['roles']
                # Simple subsequence matching
                for i in range(len(roles) - len(pattern_roles) + 1):
                    if roles[i:i+len(pattern_roles)] == pattern_roles:
                        results.append({
                            'verse_id': verse_id,
                            'verse_text': analysis['verse_text'],
                            'matched_pattern': pattern,
                            'matched_position': i,
                            'analysis': analysis
                        })
                        break
        
        return results
    
    def get_concept_usage(self, root: str) -> Dict:
        """Analyze how a concept (root) is used syntactically"""
        words = self.index.find_words_by_root(root)
        if not words:
            return {'root': root, 'error': 'No words found'}
        
        syntax_roles = {}
        grammatical_features = {
            'cases': {},
            'numbers': {},
            'genders': {},
            'is_adjective': 0,
            'is_proper_noun': 0,
            'is_verb': 0
        }
        
        for word in words:
            # Get syntax role
            role = self.infer_syntax_role(word)
            syntax_roles[role.value] = syntax_roles.get(role.value, 0) + 1
            
            # Get grammatical features
            morph = word.get('morphology', {})
            if morph and 'words' in morph:
                first_subtoken = next(iter(morph['words'].values()))
                features = self.parse_morphology_tag(
                    first_subtoken.get('morphology', '')
                )
                
                # Count cases
                case = features.get('case', Case.UNKNOWN).value
                grammatical_features['cases'][case] = grammatical_features['cases'].get(case, 0) + 1
                
                # Count numbers
                number = features.get('number', Number.UNKNOWN).value
                grammatical_features['numbers'][number] = grammatical_features['numbers'].get(number, 0) + 1
                
                # Count genders
                gender = features.get('gender', Gender.UNKNOWN).value
                grammatical_features['genders'][gender] = grammatical_features['genders'].get(gender, 0) + 1
                
                # Count types
                if features.get('is_adjective'):
                    grammatical_features['is_adjective'] += 1
                if features.get('is_proper_noun'):
                    grammatical_features['is_proper_noun'] += 1
                if features.get('is_verb'):
                    grammatical_features['is_verb'] += 1
        
        return {
            'root': root,
            'total_occurrences': len(words),
            'syntax_roles': syntax_roles,
            'grammatical_features': grammatical_features,
            'most_common_role': max(syntax_roles.items(), key=lambda x: x[1])[0] if syntax_roles else 'unknown',
            'sample_verses': [{'verse_id': w['verse_id'], 'word': w['arabic']} for w in words[:5]]
        }

def interactive_syntax_test(parser: QuranSyntaxParser):
    """Interactive testing of syntax parser"""
    print("\n" + "="*60)
    print("SYNTAX PARSER INTERACTIVE TEST")
    print("="*60)
    print("\nCommands:")
    print("  verse [id]      - Analyze verse syntax")
    print("  root [root]     - Analyze concept usage")
    print("  pattern [roles] - Find verses by syntax pattern")
    print("  word [id]       - Analyze single word")
    print("  test            - Run automated tests")
    print("  quit            - Exit")
    print("\nPattern example: preposition,noun_genitive")
    print("-" * 60)
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'quit' or cmd == 'exit':
                break
            
            elif cmd == 'test':
                run_syntax_tests(parser)
            
            elif cmd.startswith('verse '):
                try:
                    verse_id = int(cmd[6:])
                    analysis = parser.analyze_verse_syntax(verse_id)
                    
                    if 'error' in analysis:
                        print(f"Error: {analysis['error']}")
                        continue
                    
                    print(f"\nVerse {verse_id}: {analysis['verse_text']}")
                    print(f"Translation: {analysis['translation']}")
                    print(f"\nSyntax Analysis ({analysis['word_count']} words):")
                    print("-" * 60)
                    
                    for i, word in enumerate(analysis['syntax_analysis'], 1):
                        role = word['syntax_role']
                        arabic = word['arabic']
                        trans = word.get('translation', '')
                        case = word['grammatical_features']['case']
                        
                        print(f"{i:2d}. {arabic:15} → {role:20} ({case})")
                        if trans:
                            print(f"    {'':15}   {trans}")
                    
                    print(f"\nStructure: {analysis['sentence_structure']['type']}")
                    print(f"Summary: {analysis['summary']}")
                    
                    if analysis['relationships']:
                        print(f"\nRelationships:")
                        for rel in analysis['relationships']:
                            print(f"  • {rel['description']}")
                
                except ValueError:
                    print("Invalid verse ID")
            
            elif cmd.startswith('root '):
                root = cmd[5:].strip()
                usage = parser.get_concept_usage(root)
                
                if 'error' in usage:
                    print(f"Error: {usage['error']}")
                    continue
                
                print(f"\nConcept Analysis: Root '{root}'")
                print(f"Total occurrences: {usage['total_occurrences']}")
                print(f"Most common role: {usage['most_common_role']}")
                
                print(f"\nSyntax Roles:")
                for role, count in usage['syntax_roles'].items():
                    percentage = count / usage['total_occurrences'] * 100
                    print(f"  {role:20} : {count:4d} ({percentage:5.1f}%)")
                
                print(f"\nGrammatical Features:")
                if usage['grammatical_features']['cases']:
                    print("  Cases:", ", ".join([
                        f"{case}: {count}" 
                        for case, count in usage['grammatical_features']['cases'].items()
                        if case != 'unknown'
                    ]))
                
                if usage['grammatical_features']['is_adjective']:
                    adj_pct = usage['grammatical_features']['is_adjective'] / usage['total_occurrences'] * 100
                    print(f"  Used as adjective: {adj_pct:.1f}%")
                
                if usage['grammatical_features']['is_verb']:
                    verb_pct = usage['grammatical_features']['is_verb'] / usage['total_occurrences'] * 100
                    print(f"  Used as verb: {verb_pct:.1f}%")
                
                print(f"\nSample verses:")
                for sample in usage['sample_verses'][:3]:
                    verse_data = parser.index.verses.get(sample['verse_id'], {})
                    print(f"  Verse {sample['verse_id']}: {verse_data.get('arabic', '')[:50]}...")
            
            elif cmd.startswith('pattern '):
                pattern_str = cmd[8:].strip()
                roles = [r.strip() for r in pattern_str.split(',')]
                
                pattern = {'roles': roles}
                results = parser.find_by_syntax_pattern(pattern)
                
                if results:
                    print(f"\nFound {len(results)} verses with pattern: {pattern_str}")
                    for result in results[:5]:  # Show first 5
                        print(f"\nVerse {result['verse_id']}:")
                        print(f"  {result['verse_text']}")
                        print(f"  Matched at position: {result['matched_position']}")
                    if len(results) > 5:
                        print(f"\n... and {len(results) - 5} more")
                else:
                    print(f"No verses found with pattern: {pattern_str}")
            
            elif cmd.startswith('word '):
                try:
                    word_id = int(cmd[5:])
                    word_info = parser.index.get_word_info(word_id)
                    
                    if not word_info:
                        print(f"Word ID {word_id} not found")
                        continue
                    
                    role = parser.infer_syntax_role(word_info)
                    morph = word_info.get('morphology', {})
                    
                    print(f"\nWord {word_id}: {word_info['arabic']}")
                    print(f"Translation: {word_info.get('translation', 'N/A')}")
                    print(f"Syntax Role: {role.value}")
                    
                    if morph and 'words' in morph:
                        print(f"\nMorphological Analysis:")
                        for subtoken_id, subtoken in morph['words'].items():
                            print(f"  {subtoken['word']}: {subtoken['morphology']}")
                        
                        # Parse features
                        first_subtoken = next(iter(morph['words'].values()))
                        features = parser.parse_morphology_tag(
                            first_subtoken.get('morphology', '')
                        )
                        
                        print(f"\nGrammatical Features:")
                        print(f"  Case: {features.get('case', 'unknown')}")
                        print(f"  Number: {features.get('number', 'unknown')}")
                        print(f"  Gender: {features.get('gender', 'unknown')}")
                        print(f"  Type: ", end="")
                        types = []
                        if features.get('is_noun'):
                            types.append("noun")
                        if features.get('is_verb'):
                            types.append("verb")
                        if features.get('is_adjective'):
                            types.append("adjective")
                        if features.get('is_particle'):
                            types.append("particle")
                        if features.get('is_proper_noun'):
                            types.append("proper noun")
                        print(", ".join(types) if types else "unknown")
                
                except ValueError:
                    print("Invalid word ID")
            
            elif cmd:
                print("Unknown command. Type 'help' for commands list.")
        
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

def run_syntax_tests(parser: QuranSyntaxParser):
    """Run automated syntax tests"""
    print("\n" + "="*60)
    print("RUNNING SYNTAX TESTS")
    print("="*60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Verse 1 syntax analysis
    print("\n1. Testing verse 1 syntax...")
    analysis = parser.analyze_verse_syntax(1)
    if 'error' not in analysis and analysis['word_count'] == 4:
        print(f"   ✓ Verse 1 analyzed with {analysis['word_count']} words")
        tests_passed += 1
    else:
        print(f"   ✗ Verse 1 analysis failed")
        tests_failed += 1
    
    # Test 2: Root 'رحم' concept analysis
    print("\n2. Testing concept analysis...")
    usage = parser.get_concept_usage('رحم')
    if 'error' not in usage and usage['total_occurrences'] > 0:
        print(f"   ✓ Root 'رحم' has {usage['total_occurrences']} occurrences")
        tests_passed += 1
    else:
        print(f"   ✗ Root 'رحم' analysis failed")
        tests_failed += 1
    
    # Test 3: Syntax pattern search
    print("\n3. Testing syntax pattern search...")
    pattern = {'roles': ['preposition', 'noun_genitive']}
    results = parser.find_by_syntax_pattern(pattern)
    if results:
        print(f"   ✓ Found {len(results)} verses with preposition + noun pattern")
        tests_passed += 1
    else:
        print(f"   ✗ No verses found with pattern")
        tests_failed += 1
    
    # Test 4: Word syntax inference
    print("\n4. Testing word syntax inference...")
    word_info = parser.index.get_word_info(1)
    if word_info:
        role = parser.infer_syntax_role(word_info)
        print(f"   ✓ Word 1 role: {role.value}")
        tests_passed += 1
    else:
        print(f"   ✗ Word 1 inference failed")
        tests_failed += 1
    
    print("\n" + "="*60)
    print(f"SYNTAX TESTS COMPLETE: {tests_passed} passed, {tests_failed} failed")
    print("="*60)

def main():
    """Main function"""
    print("Quran Syntax Parser")
    print("="*60)
    
    # Import and initialize unified index
    try:
        from unified_index import QuranUnifiedIndex
        
        # Load data
        print("Loading unified index...")
        index = QuranUnifiedIndex(".")
        index.load_all_data()
        
        # Create syntax parser
        parser = QuranSyntaxParser(index)
        print("Syntax parser initialized successfully!")
        
        # Run interactive test
        interactive_syntax_test(parser)
        
    except ImportError as e:
        print(f"Error: {e}")
        print("\nMake sure unified_index.py is in the same directory")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()