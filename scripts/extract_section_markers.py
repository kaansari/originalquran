#!/usr/bin/env python3
"""Extract Qudratullah section annotations from the already-imported Indian text.

Reads local files only. Never rewrites Quran word files. The four recurring
positions within each Juz identify quarter/half/three-quarter/end signs; unknown
glyphs (including pause, recitation and verse-number signs) are not copied.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLYPHS = {'\uf64c': 'quarter', '\uf64d': 'half', '\uf64e': 'three_quarters',
          '\uf64f': 'three_quarters', '\uf650': 'juz_end'}
PHASES = ['quarter', 'half', 'three_quarters', 'juz_end']
SYMBOLS = {'quarter': '¼', 'half': '½', 'three_quarters': '¾', 'juz_end': 'Juz'}


def extract(layout, suras, combined, expected_juz=30):
    result, issues, starts = [], [], [{'juz': 1, 'beforeWordId': 1}]
    juz, phases, previous_word = 1, [], 0
    for page, lines in sorted(layout['pages'].items(), key=lambda item: int(item[0])):
        for line in sorted(lines, key=lambda item: item['number']):
            for token in line.get('tokens', []):
                signs = [character for character in token['text'] if character in GLYPHS]
                if not signs:
                    continue
                sura, verse = map(int, token['ref'].split(':'))
                if str(sura) not in suras or not 1 <= verse <= suras[str(sura)]['nAyah']:
                    raise ValueError('Invalid source verse: ' + token['ref'])
                meta = combined[str(suras[str(sura)]['start'] + verse - 1)]
                anchor = token.get('wordId', meta['end_word'])
                if not meta['start_word'] <= anchor <= meta['end_word'] or anchor < previous_word:
                    raise ValueError('Invalid or unordered shared word anchor')
                for character in signs:
                    kind = GLYPHS[character]
                    phase = PHASES.index(kind)
                    if phase in phases or (phases and phase < phases[-1]):
                        raise ValueError('Repeated or out-of-order section sign in Juz {}'.format(juz))
                    phases.append(phase)
                    result.append({'juz': juz, 'kind': kind, 'symbol': SYMBOLS[kind],
                                   'verse': token['ref'], 'afterWordId': anchor,
                                   'placement': 'after_word' if token.get('wordId') else 'after_verse',
                                   'codePoint': 'U+{:04X}'.format(ord(character)),
                                   'sourcePage': int(page), 'sourceLine': line['number']})
                    previous_word = anchor
                    if kind == 'juz_end':
                        for missing in sorted(set(range(3)) - set(phases)):
                            issues.append({'juz': juz, 'kind': PHASES[missing],
                                           'message': 'No explicit sign found in the local Indian source; not inferred or inserted.'})
                        if juz < expected_juz:
                            starts.append({'juz': juz + 1, 'beforeWordId': anchor + 1})
                        juz += 1
                        phases = []
    if juz - 1 != expected_juz or phases:
        raise ValueError('Expected {} complete Juz-ending signs'.format(expected_juz))
    counts = collections.Counter(marker['kind'] for marker in result)
    return {'convention': 'Indian / Qudratullah',
            'interpretation': 'Quarter/half/three-quarter/end meanings follow the repeated four-phase sequence of the embedded Indian signs.',
            'counts': dict(counts), 'markers': result, 'juzStarts': starts, 'issues': issues}


def report(data):
    lines = ['# Extracted Indian Quran section markers', '',
             'Extracted locally from the existing Indian layout; all Quran word files remain unchanged.', '',
             'The sign meanings are identified from their repeating quarter / half / three-quarter / Juz-end sequence.',
             'These are the Indian/Qudratullah boundaries, not a claim that every printed edition uses identical divisions.', '',
             '| Kind | Source glyph | Count |', '|---|---|---:|']
    for kind in PHASES:
        codes = ', '.join('U+{:04X}'.format(ord(c)) for c, mapped in GLYPHS.items() if mapped == kind)
        lines.append('| {} | {} | {} |'.format(kind, codes, data['counts'].get(kind, 0)))
    lines += ['', '## Source gaps', '']
    lines += ['- Juz {}: {} — {}'.format(item['juz'], item['kind'], item['message']) for item in data['issues']]
    lines += ['', '## Exact extracted positions', '',
              '| Juz | Kind | Verse | After shared word | Placement | Indian page/line |',
              '|---:|---|---|---:|---|---|']
    for item in data['markers']:
        lines.append('| {juz} | {kind} | {verse} | {afterWordId} | {placement} | {sourcePage}/{sourceLine} |'.format(**item))
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'src/json/section_markers.json')
    parser.add_argument('--report', type=Path, default=ROOT / 'docs/section-markers.md')
    args = parser.parse_args()
    source = ROOT / 'src/json/indian/lines.json'
    load = lambda name: json.loads((ROOT / 'src/json' / name).read_text(encoding='utf-8'))
    data = extract(load('indian/lines.json'), load('sura.json'), load('combined_quran.json'))
    data['source'] = {'file': 'json/indian/lines.json', 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    for path, text in [(args.output, json.dumps(data, ensure_ascii=False, indent=2) + '\n'), (args.report, report(data))]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    print('Extracted {} section markers; {} source gaps recorded.'.format(len(data['markers']), len(data['issues'])))


if __name__ == '__main__':
    main()
