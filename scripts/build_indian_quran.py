#!/usr/bin/env python3
"""Import matching QUL resource 12 layout and resource 59 word exports.

Accepts QUL ZIP, JSON or SQLite. Run with --help for the required source paths.
Source text uses the three user-requested بَعْدَمَا joins and the token split
at 37:130; no inferred printed line breaks. Original archives remain unchanged.
"""
import argparse
import hashlib
import json
import sqlite3
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_rows(path, table):
    path = Path(path)
    if path.suffix == '.zip':
        with zipfile.ZipFile(path) as archive:
            documents = [json.loads(archive.read(name)) for name in archive.namelist()
                         if name.endswith('.json') and Path(name).name != 'info.json']
        if table == 'pages':
            return [dict(line, page_number=document['page'], line_number=int(number),
                         line_type=line['type'], is_centered=line['alignment'] == 'centered')
                    for document in documents for number, line in document['lines'].items()]
        if len(documents) != 1:
            raise ValueError('Expected one word export in ZIP')
        data = documents[0]
    else:
        data = None
    if path.suffix in ('.db', '.sqlite', '.sqlite3'):
        with sqlite3.connect('file:{}?mode=ro'.format(path.resolve()), uri=True) as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute('SELECT * FROM ' + table)]
    if data is None:
        data = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data, dict) and table in data:
        data = data[table]
    if isinstance(data, dict):
        data = list(data.values())
    if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
        raise ValueError('Expected {} rows in {}'.format(table, path))
    return data


def integer(row, *fields):
    for field in fields:
        if row.get(field) is not None and row[field] != '':
            return int(row[field])
    raise ValueError('Missing {}'.format('/'.join(fields)))


def convert(lines, source_words, suras, combined, expected_pages=610):
    # QUL word IDs include verse markers; our morphology IDs do not.
    by_verse, source = {}, {}
    for row in source_words:
        wid = integer(row, 'id', 'word_index')
        if wid in source:
            raise ValueError('Duplicate source word {}'.format(wid))
        sura = integer(row, 'surah', 'surah_number', 'sura')
        verse = integer(row, 'ayah', 'ayah_number', 'verse')
        position = integer(row, 'word', 'position', 'word_position')
        if str(sura) not in suras or not 1 <= verse <= suras[str(sura)]['nAyah']:
            raise ValueError('Invalid verse')
        text = row.get('text')
        if not isinstance(text, str) or not text.strip():
            raise ValueError('Missing source text')
        token = {'text': text, 'ref': '{}:{}'.format(sura, verse)}
        source[wid] = token
        by_verse.setdefault((sura, verse), []).append((position, wid))

    words = {}
    for sura_key, sura in suras.items():
        for verse in range(1, sura['nAyah'] + 1):
            rows = sorted(by_verse.get((int(sura_key), verse), []))
            meta = combined[str(sura['start'] + verse - 1)]
            count = meta['end_word'] - meta['start_word'] + 1
            # Exactly one final token must be the source's ayah marker.
            ref = '{}:{}'.format(sura_key, verse)
            split_at = {'2:181': 3, '8:6': 4, '13:37': 8}.get(ref)
            merged_at = 3 if ref == '37:130' else None
            expected = count + 1 + (1 if split_at else -1 if merged_at else 0)
            if len(rows) != expected or [r[0] for r in rows] != list(range(1, expected + 1)):
                raise ValueError('Word alignment mismatch at {}:{}'.format(sura_key, verse))
            for offset, (_, wid) in enumerate(rows[:-1]):
                position = offset + 1
                canonical_offset = offset - (1 if split_at and position > split_at else 0)
                if merged_at and position > merged_at:
                    canonical_offset += 1
                word_id = meta['start_word'] + canonical_offset
                token = source[wid]
                if merged_at and position == merged_at:
                    # The source prints اِِلْ یَاسِیْنَ as one token; morphology has two.
                    parts = token['text'].split(' ')
                    if len(parts) != 2:
                        raise ValueError('Unexpected merged token at ' + ref)
                    token['parts'] = [{'text': part, 'wordId': word_id + i} for i, part in enumerate(parts)]
                    for part in token['parts']:
                        words[str(part['wordId'])] = part['text']
                else:
                    token['wordId'] = word_id
                    previous = words.get(str(word_id))
                    words[str(word_id)] = previous + token['text'] if previous else token['text']

    pages, seen, layout, text_differences = [], [], {}, []
    for row in sorted(lines, key=lambda r: (integer(r, 'page_number'), integer(r, 'line_number'))):
        page, number = integer(row, 'page_number'), integer(row, 'line_number')
        if not 1 <= page <= expected_pages or not 1 <= number <= 15:
            raise ValueError('Invalid page or line number')
        page_lines = layout.setdefault(str(page), [])
        if page_lines and page_lines[-1]['number'] >= number:
            raise ValueError('Duplicate line')
        kind = row['line_type']
        if kind not in ('ayah', 'surah_name', 'basmallah'):
            raise ValueError('Unknown line type: ' + kind)
        line = {'number': number, 'type': kind,
                'centered': str(row.get('is_centered', False)).lower() in ('1', 'true')}
        if kind == 'ayah':
            first, last = integer(row, 'first_word_id'), integer(row, 'last_word_id')
            if last < first:
                raise ValueError('Reversed word range')
            ids = list(range(first, last + 1))
            if any(wid not in source for wid in ids):
                raise ValueError('Layout references missing source words')
            seen.extend(ids)
            line['tokens'] = [source[wid] for wid in ids]
            if 'data' in row:
                if len(row['data']) != len(ids):
                    raise ValueError('Layout text count differs from word range')
                # Layout exports carry a redundant cached text preview. Word IDs
                # define the layout; the matching word export is the text source.
                for wid, preview in zip(ids, row['data']):
                    if preview != source[wid]['text']:
                        text_differences.append({'page': page, 'line': number, 'word': wid,
                                                 'layoutPreview': preview, 'text': source[wid]['text']})
        elif kind == 'surah_name':
            line['sura'] = integer(row, 'surah_number')
            if str(line['sura']) not in suras:
                raise ValueError('Unknown surah heading')
        page_lines.append(line)
    if seen != sorted(source):
        raise ValueError('Layout must cover every source token exactly once in order')
    if sorted(map(int, layout)) != list(range(1, expected_pages + 1)):
        raise ValueError('Expected {} complete pages'.format(expected_pages))
    # Join only the three approved split words, after validating original source
    # coverage and layout previews. All three pairs occupy one printed line.
    joins = {'2:181': 3289, '8:6': 22614, '13:37': 32556}
    joined = set()
    for page_lines in layout.values():
        for line in page_lines:
            if line['type'] != 'ayah':
                continue
            tokens = []
            for token in line['tokens']:
                if token['ref'] == '37:130' and token.get('parts'):
                    tokens.extend(dict(part, ref=token['ref']) for part in token['parts'])
                    continue
                if (tokens and token['ref'] in joins and joins[token['ref']] == token.get('wordId')
                        and tokens[-1].get('wordId') == token.get('wordId')):
                    tokens[-1] = dict(tokens[-1], text=tokens[-1]['text'] + token['text'])
                    joined.add(token['ref'])
                else:
                    tokens.append(token)
            line['tokens'] = tokens
    expected_joins = set(joins).intersection(token['ref'] for token in source.values())
    if joined != expected_joins:
        raise ValueError('Approved joined word must appear on one printed line')
    lexical = [token for page_lines in layout.values() for line in page_lines
               for token in line.get('tokens', []) if token.get('wordId')]
    if [token['wordId'] for token in lexical] != sorted(map(int, words)):
        raise ValueError('Printed tokens must match the shared word index exactly once in order')
    if any(token['text'] != words[str(token['wordId'])] for token in lexical):
        raise ValueError('Printed token text must match the indexed word text')
    for page in range(1, expected_pages + 1):
        tokens = [t for line in layout[str(page)] for t in line.get('tokens', [])]
        if not tokens:
            raise ValueError('Page without Quran words')
        pages.append({'page': page, 'from': tokens[0]['ref'], 'to': tokens[-1]['ref']})
    basmallah = ' '.join(words[str(i)] for i in range(1, combined['1']['end_word'] + 1))
    return pages, words, {'pages': layout, 'basmallah': basmallah, 'textDifferences': text_differences}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--layout', type=Path, required=True, help='QUL resource 12 ZIP, JSON or SQLite')
    parser.add_argument('--words', type=Path, required=True, help='QUL resource 59 ZIP, JSON or SQLite')
    parser.add_argument('--output', type=Path, default=ROOT / 'src/json/indian')
    parser.add_argument('--words-output', type=Path, help='Word file; defaults to quranic_indian_words.json beside the edition folder')
    args = parser.parse_args()
    load = lambda name: json.loads((ROOT / 'src/json' / name).read_text(encoding='utf-8'))
    pages, words, layout = convert(read_rows(args.layout, 'pages'), read_rows(args.words, 'words'),
                                   load('sura.json'), load('combined_quran.json'))
    provenance = {
        'edition': 'Qudratullah IndoPak 15-line', 'pages': 610, 'linesPerPage': 15,
        'layoutSource': 'https://qul.tarteel.ai/resources/mushaf-layout/12',
        'textSource': 'https://qul.tarteel.ai/resources/quran-script/59',
        'fontSource': 'https://qul.tarteel.ai/resources/font/242',
        'credits': 'QUL / Tarteel; Qudratullah Company; Ayman Siddiqui and R. Siddiqua, QuranWBW.com and Quran.com',
        'tokenization': {'splitWords': ['2:181:3-4', '8:6:4-5', '13:37:8-9'], 'mergedWords': ['37:130:3']},
        'textAdjustments': {'joinedWithoutSpace': ['2:181:3-4', '8:6:4-5', '13:37:8-9'],
                            'splitIntoTwoTokens': ['37:130:3'],
                            'reason': 'User requested three بَعْدَمَا joins and splitting اِلْ یَاسِیْنَ at 37:130 to match the shared 77,430-word index.'},
        'layoutPreviewDifferences': layout['textDifferences'],
        'sourceSHA256': {name: hashlib.sha256(path.read_bytes()).hexdigest()
                         for name, path in [('layout', args.layout), ('words', args.words)]}}
    args.output.mkdir(parents=True, exist_ok=True)
    words_output = args.words_output or args.output.parent / 'quranic_indian_words.json'
    words_output.parent.mkdir(parents=True, exist_ok=True)
    words_output.write_text(json.dumps(words, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for name, data in [('pagination', pages), ('lines', layout), ('source', provenance)]:
        (args.output / (name + '.json')).write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print('Validated 610 pages and all 6,236 verses; wrote {}'.format(args.output))


if __name__ == '__main__':
    main()
