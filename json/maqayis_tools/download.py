#!/usr/bin/env python3
"""Download Maqayis entries, keeping cached source HTML and source attribution."""
import argparse
import hashlib
import json
import re
import ssl
import socket
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

BASE = 'https://arabiclexicon.hawramani.com/'
INDEX_URL = BASE + 'ibn-faris-maqayis-al-lugha/'
USER_AGENT = 'MaqayisArchive/1.0'


class Page(HTMLParser):
    """Collect visible text and links without third-party dependencies."""
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.links = []
        self.anchor = None
        self.hidden = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1
        if self.hidden:
            return
        if tag in ('p', 'div', 'br', 'li', 'h1', 'h2', 'h3', 'section', 'article'):
            self.parts.append('\n')
        if tag == 'a':
            self.anchor = [dict(attrs).get('href', ''), []]

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)
            return
        if self.hidden:
            return
        if tag == 'a' and self.anchor is not None:
            self.links.append((self.anchor[0], ''.join(self.anchor[1]).strip()))
            self.anchor = None
        if tag in ('p', 'div', 'li', 'h1', 'h2', 'h3', 'section', 'article'):
            self.parts.append('\n')

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)
            if self.anchor is not None:
                self.anchor[1].append(data)

    def text(self):
        return '\n'.join(' '.join(line.split()) for line in ''.join(self.parts).splitlines() if line.strip())


def parse_index(html):
    entries = {}
    for href, heading in Page(html).links:
        url = urlsplit(urljoin(INDEX_URL, href))
        if url.netloc != urlsplit(BASE).netloc or parse_qs(url.query).get('book') != ['9']:
            continue
        if not re.search('[\u0621-\u064a]', heading):
            continue
        path = quote(unquote(url.path), safe='/')
        canonical = urlunsplit(('https', url.netloc, path, url.query, ''))
        entries.setdefault(canonical, {
            'id': hashlib.sha256(canonical.encode()).hexdigest()[:20],
            'heading': heading.strip(), 'url': canonical,
        })
    if not entries:
        raise ValueError('No book=9 entry links found; index layout may have changed.')
    return list(entries.values())


class EntrySections(HTMLParser):
    """Extract credited definition blocks from the first article only."""
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.in_article = False
        self.finished = False
        self.div_depth = 0
        self.container_depth = None
        self.content_depth = None
        self.credited = False
        self.parts = []
        self.definitions = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if self.finished:
            return
        if tag == 'article':
            self.in_article = True
        if not self.in_article:
            return
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if tag == 'div':
            self.div_depth += 1
            if 'definition-container' in classes:
                self.container_depth = self.div_depth
                self.credited = False
                self.parts = []
            if self.container_depth is not None and 'definition' in classes:
                self.content_depth = self.div_depth
        if self.container_depth is not None and tag == 'a':
            href = urlsplit(urljoin(BASE, attrs.get('href', '')))
            if href.netloc == urlsplit(BASE).netloc and href.path.rstrip('/') == urlsplit(INDEX_URL).path.rstrip('/'):
                self.credited = True
        if self.content_depth is not None and tag in ('p', 'br', 'div', 'li'):
            self.parts.append('\n')

    def handle_endtag(self, tag):
        if not self.in_article or self.finished:
            return
        if tag == 'div':
            if self.div_depth == self.content_depth:
                self.content_depth = None
            if self.div_depth == self.container_depth:
                if self.credited:
                    text = '\n\n'.join(' '.join(line.split()) for line in ''.join(self.parts).splitlines() if line.strip())
                    if not re.search('[\u0621-\u064a]', text):
                        raise ValueError('Empty Ibn Faris definition block.')
                    self.definitions.append(text)
                self.container_depth = None
            self.div_depth -= 1
        if self.content_depth is not None and tag in ('p', 'div', 'li'):
            self.parts.append('\n')
        if tag == 'article':
            self.in_article = False
            self.finished = True

    def handle_data(self, data):
        if self.in_article and not self.finished and self.content_depth is not None:
            self.parts.append(data)


def parse_entry(html):
    structured = EntrySections(html)
    if structured.definitions:
        return '\n\n'.join(structured.definitions)
    text = Page(html).text()
    start = text.find('Entries on ')
    if start < 0:
        raise ValueError('Entry heading missing; refusing to save an error page.')
    text = text[start:]
    permalink = text.find('Permalink')
    if permalink < 0 or not re.search(r'Ibn F[āa]ris', text[:permalink]):
        raise ValueError('Ibn Faris section missing; refusing to save another dictionary.')
    text = text[permalink + len('Permalink'):]
    boundary = re.search(r'You are viewing The Arabic Lexicon|Similar and related entries:', text)
    if boundary is None:
        raise ValueError('Dictionary section boundary missing; inspect cached HTML before proceeding.')
    text = text[:boundary.start()]
    lines = text.splitlines()
    while lines and (not lines[0].strip() or lines[0].lstrip().startswith(('(الرابط', 'https://', 'http://'))):
        lines.pop(0)
    content = '\n\n'.join(line.strip() for line in lines if line.strip())
    if not re.search('[\u0621-\u064a]', content) or 'Permalink' in content:
        raise ValueError('Definition empty or contains multiple dictionary sections.')
    return content


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(text, encoding='utf-8')
    temporary.replace(path)


class Fetcher:
    def __init__(self, delay, offline, insecure=False, timeout=20, retries=0):
        self.delay = delay
        self.offline = offline
        self.timeout = timeout
        self.retries = retries
        self.last_request = 0
        self.policy = None
        self.ssl_context = ssl.create_default_context()
        if insecure:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

    def request(self, url):
        wait = self.delay - (time.monotonic() - self.last_request)
        if wait > 0:
            time.sleep(wait)
        self.last_request = time.monotonic()
        request = Request(url, headers={'User-Agent': USER_AGENT})
        with urlopen(request, timeout=self.timeout, context=self.ssl_context) as response:
            return response.read().decode(response.headers.get_content_charset() or 'utf-8')

    def check_policy(self, url):
        if self.policy is None:
            policy = RobotFileParser()
            try:
                robots = self.request(urljoin(BASE, 'robots.txt'))
            except HTTPError as exc:
                if exc.code not in (404, 410):
                    raise
                robots = 'User-agent: *\nAllow: /'
            policy.parse(robots.splitlines())
            self.policy = policy
            crawl_delay = self.policy.crawl_delay(USER_AGENT)
            if crawl_delay:
                self.delay = max(self.delay, crawl_delay)
        if not self.policy.can_fetch(USER_AGENT, url):
            raise PermissionError(f'robots.txt disallows downloading {url}')

    def get(self, url, path):
        if path.exists():
            return path.read_text(encoding='utf-8')
        if self.offline:
            raise FileNotFoundError(f'No cached page: {path}')
        self.check_policy(url)
        for attempt in range(self.retries + 1):
            try:
                html = self.request(url)
                atomic_write(path, html)
                return html
            except HTTPError as exc:
                if exc.code not in (408, 429, 500, 502, 503, 504) or attempt == self.retries:
                    raise
                retry_after = exc.headers.get('Retry-After', '')
                time.sleep(max(2 ** (attempt + 1), int(retry_after) if retry_after.isdigit() else 0))
            except (URLError, TimeoutError, socket.timeout):
                if attempt == self.retries:
                    raise
                time.sleep(2 ** (attempt + 1))


def run(output, delay=1.5, limit=None, offline=False, insecure=False, timeout=20, retries=0):
    output = Path(output)
    fetcher = Fetcher(delay, offline, insecure=insecure, timeout=timeout, retries=retries)
    entries = parse_index(fetcher.get(INDEX_URL, output / 'raw/index.html'))
    manifest = {
        'dictionary': 'Ibn Faris, Maqayis al-Lugha', 'source': INDEX_URL,
        'total_index_entries': len(entries), 'downloaded': 0,
        'complete': False, 'skipped': [], 'entries': entries,
    }
    index_path = output / 'index.json'
    selected = entries if limit is None else entries[:limit]
    selected_ids = {entry['id'] for entry in selected}
    failure = None
    try:
        for i, entry in enumerate(entries, 1):
            raw_path = output / 'raw' / (entry['id'] + '.html')
            if entry['id'] not in selected_ids and not raw_path.exists():
                continue
            try:
                try:
                    html = fetcher.get(entry['url'], raw_path)
                except (URLError, TimeoutError, socket.timeout) as exc:
                    # Keep certificate failures and nontransient HTTP errors fatal.
                    if isinstance(exc, HTTPError) and exc.code not in (408, 429, 500, 502, 503, 504):
                        raise
                    if isinstance(getattr(exc, 'reason', None), ssl.SSLError):
                        raise
                    entry['error'] = str(exc)
                    manifest['skipped'].append({'heading': entry['heading'], 'url': entry['url'], 'error': str(exc)})
                    print(f'[{i}/{len(entries)}] SKIPPED {entry["heading"]}: {exc}', file=sys.stderr, flush=True)
                    atomic_write(index_path, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
                    atomic_write(output / 'skipped.json', json.dumps(manifest['skipped'], ensure_ascii=False, indent=2) + '\n')
                    continue
                entry['text'] = parse_entry(html)
                entry['markdown'] = 'entries/' + entry['id'] + '.md'
                markdown = f'# {entry["heading"]}\n\nDictionary: Ibn Faris, Maqayis al-Lugha\n\nSource: {entry["url"]}\n\n{entry["text"]}\n'
                atomic_write(output / entry['markdown'], markdown)
                manifest['downloaded'] += 1
                print(f'[{i}/{len(entries)}] {entry["heading"]}', flush=True)
            except (OSError, ValueError) as exc:
                entry['error'] = str(exc)
                failure = exc
                raise
    finally:
        manifest['complete'] = manifest['downloaded'] == len(entries) and failure is None
        atomic_write(index_path, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        atomic_write(output / 'skipped.json', json.dumps(manifest['skipped'], ensure_ascii=False, indent=2) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent.parent / 'maqayis')
    parser.add_argument('--delay', type=float, default=1.5, help='Minimum seconds between requests (default: 1.5)')
    parser.add_argument('--limit', type=int, help='Process the first N entries for a trial run')
    parser.add_argument('--offline', action='store_true', help='Extract cached HTML without network requests')
    parser.add_argument('--insecure', action='store_true', help='Disable HTTPS certificate and hostname verification for this run')
    parser.add_argument('--timeout', type=float, default=20, help='Socket timeout in seconds per attempt (default: 20)')
    parser.add_argument('--retries', type=int, default=0, help='Extra attempts before skipping a transient request failure (default: 0)')
    args = parser.parse_args()
    if args.delay < 0 or args.timeout <= 0 or args.retries < 0 or (args.limit is not None and args.limit < 1):
        parser.error('--delay and --retries must be nonnegative; --timeout and --limit must be positive')
    if args.insecure:
        print('HTTPS certificate verification disabled for this run.', file=sys.stderr)
    try:
        result = run(args.output, args.delay, args.limit, args.offline, insecure=args.insecure, timeout=args.timeout, retries=args.retries)
    except (OSError, ValueError) as exc:
        print(f'Download stopped: {exc}\nRerun the same command to resume cached downloads.', file=sys.stderr)
        return 1
    print(f'Saved {result["downloaded"]}/{result["total_index_entries"]} entries to {args.output}')
    skipped = len(result.get('skipped', []))
    if skipped:
        print(f'{skipped} entries skipped; see {args.output / "skipped.json"}. Rerun to retry missing pages.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
