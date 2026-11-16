#!/usr/bin/env python3
"""Build an offline, merge-friendly chapter/Juz/marker reference JSON.

No HTML, JavaScript, Quran word, pagination or surah files are modified.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(source, suras, combined):
    locations = {}
    chapters = {}
    for key, sura in sorted(suras.items(), key=lambda item: int(item[0])):
        record = copy.deepcopy(sura)
        record['start_word'] = combined[str(sura['start'])]['start_word']
        record['end_word'] = combined[str(sura['end'])]['end_word']
        chapters[key] = record
        for verse in range(1, sura['nAyah'] + 1):
            verse_id = sura['start'] + verse - 1
            words = combined[str(verse_id)]
            for word_id in range(words['start_word'], words['end_word'] + 1):
                if word_id in locations:
                    raise ValueError('Duplicate shared word ID')
                locations[word_id] = {'sura': int(key), 'verse': verse,
                                      'verseKey': '{}:{}'.format(key, verse),
                                      'verseId': verse_id, 'word': word_id - words['start_word'] + 1}
    if sorted(locations) != list(range(1, len(locations) + 1)):
        raise ValueError('Shared word IDs must be contiguous and one-based')

    markers = []
    ends = {}
    for original in source['markers']:
        word_id = original['afterWordId']
        if word_id not in locations:
            raise ValueError('Marker refers to a missing word')
        location = locations[word_id]
        if location['verseKey'] != original['verse']:
            raise ValueError('Marker verse and word reference disagree')
        if original['placement'] == 'after_verse' and word_id != combined[str(location['verseId'])]['end_word']:
            raise ValueError('Verse-ending marker is not at the last word')
        record = {key: copy.deepcopy(value) for key, value in original.items()
                  if key not in ('verse', 'afterWordId')}
        record.update(location)
        record['wordId'] = word_id
        markers.append(record)
        if record['kind'] == 'juz_end':
            if record['juz'] in ends:
                raise ValueError('Duplicate Juz ending')
            ends[record['juz']] = word_id

    juz = {}
    previous = 0
    if sorted(ends) != list(range(1, 31)):
        raise ValueError('Expected 30 Juz endings')
    for number in range(1, 31):
        start, end = previous + 1, ends[number]
        if start > end:
            raise ValueError('Juz ranges must be ordered and nonempty')
        juz[str(number)] = {'from': locations[start]['verseKey'], 'to': locations[end]['verseKey'],
                            'start_word': start, 'end_word': end,
                            'fromWord': locations[start]['word'], 'toWord': locations[end]['word']}
        previous = end
    if previous != max(locations):
        raise ValueError('Juz ranges must cover the complete Quran')
    for record in chapters.values():
        record['juz'] = [int(key) for key, part in juz.items()
                         if part['start_word'] <= record['end_word'] and part['end_word'] >= record['start_word']]
    return {'schemaVersion': 1, 'convention': source['convention'],
            'interpretation': source['interpretation'],
            'indexing': {'wordId': 'One-based shared Quran word index; markers occur after this word.',
                         'verseId': 'One-based global verse index used by combined_quran.json.',
                         'word': 'One-based word position within the verse.',
                         'chapters': 'String keys match sura.json; start/end are global verse IDs.',
                         'juz': 'String keys 1–30; from/to match pagination-style sura:verse references.'},
            'chapters': chapters, 'juz': juz, 'markers': markers, 'issues': copy.deepcopy(source['issues'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'src/json/quran_sections.json')
    args = parser.parse_args()
    load = lambda name: json.loads((ROOT / 'src/json' / name).read_text(encoding='utf-8'))
    data = build(load('section_markers.json'), load('sura.json'), load('combined_quran.json'))
    data['sources'] = {name: hashlib.sha256((ROOT / 'src/json' / name).read_bytes()).hexdigest()
                       for name in ('section_markers.json', 'sura.json', 'combined_quran.json')}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Wrote {}: {} chapters, {} Juz ranges, {} markers; {} source gaps retained.'.format(
        args.output, len(data['chapters']), len(data['juz']), len(data['markers']), len(data['issues'])))


if __name__ == '__main__':
    main()
