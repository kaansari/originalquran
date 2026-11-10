#!/usr/bin/env python3
"""Build the standalone Maqayis dictionary browser from a read-only download snapshot."""
import argparse
import json
import os
from html import escape
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]


def collect(source):
    source = Path(source)
    manifest = json.loads((source / 'index.json').read_text(encoding='utf-8'))
    entries = []
    for item in manifest['entries']:
        entry_id = item['id']
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', entry_id):
            raise ValueError('Invalid entry ID: ' + entry_id)
        entry = {key: item.get(key, '') for key in ('id', 'heading', 'url', 'text')}
        markdown = source / 'entries' / (entry_id + '.md')
        if markdown.is_file():
            content = markdown.read_text(encoding='utf-8')
            match = re.search(r'^Source:\s*(\S+)[ \t]*\n\s*\n([\s\S]*)', content, re.MULTILINE)
            if not match or not match.group(2).strip():
                raise ValueError('Missing source or definition in ' + str(markdown))
            entry['url'], entry['text'] = match.group(1), match.group(2).strip()
        if not isinstance(entry['text'], str):
            entry['text'] = ''
        url = urlsplit(entry['url'])
        if url.scheme not in ('http', 'https') or url.netloc != 'arabiclexicon.hawramani.com':
            entry['url'] = ''
        entries.append(entry)
    if not entries:
        raise ValueError('The dictionary index has no entries.')
    return {'entries': entries, 'available': sum(bool(e['text']) for e in entries),
            'total': len(entries), 'built': datetime.now(timezone.utc).isoformat(timespec='seconds')}


def render(template, data, core, root_url="../root.html"):
    tokens = ('__DICTIONARY_DATA__', '__DICTIONARY_CORE__')
    if any(template.count(token) != 1 for token in tokens):
        raise ValueError('Template must contain each dictionary placeholder exactly once.')
    serialized = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    serialized = serialized.replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    site_base = root_url.rsplit('/', 1)[0] + '/' if '/' in root_url else ''
    template = template.replace('__SITE_BASE__', escape(site_base, quote=True))
    return template.replace('href="__ROOT_URL__"', 'href="' + escape(root_url, quote=True) + '"').replace(tokens[1], core).replace(tokens[0], serialized)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=PROJECT / 'src/json/maqayis')
    parser.add_argument('--output', type=Path, default=PROJECT / 'src/maqayis.html')
    args = parser.parse_args()
    data = collect(args.source)
    page = render((HERE / 'maqayis.template.html').read_text(encoding='utf-8'), data,
                  (HERE / 'browser_core.js').read_text(encoding='utf-8'),
                  root_url=Path(os.path.relpath(PROJECT / 'src/root.html', args.output.resolve().parent)).as_posix())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + '.tmp')
    temporary.write_text(page, encoding='utf-8')
    temporary.replace(args.output)
    print(f'Built {args.output}: {data["available"]:,} definitions / {data["total"]:,} indexed headings.')


if __name__ == '__main__':
    main()
