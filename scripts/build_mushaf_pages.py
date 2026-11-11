"""Build the 604-page Madinah Hafs verse map from Quran-Center page metadata."""
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

def build_pages(starts, surahs):
    ranges = sorted((int(key), value['start'], value['end']) for key, value in surahs.items())
    if len(starts) != 606 or starts[:2] != [0, 1] or starts[-1] != 6237:
        raise ValueError('Expected 604 Madinah pages with 0 and 6237 sentinels.')
    if any(a >= b for a, b in zip(starts, starts[1:])):
        raise ValueError('Page starts must be strictly increasing.')
    def reference(verse):
        for chapter, start, end in ranges:
            if start <= verse <= end:
                return f'{chapter}:{verse - start + 1}'
        raise ValueError(f'Unknown verse ID: {verse}')
    return [{'page': page, 'from': reference(starts[page]), 'to': reference(starts[page + 1] - 1)}
            for page in range(1, 605)]

if __name__ == '__main__':
    metadata = json.loads((PROJECT / 'data/mushaf-page-starts.json').read_text())
    surahs = json.loads((PROJECT / 'src/json/sura.json').read_text())
    pages = build_pages(metadata['starts'], surahs)
    destination = PROJECT / 'src/json/pagination_madinah.json'
    destination.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + '\n')
    print(f'Built {len(pages)} Madinah pages: {pages[0]} to {pages[-1]}')
