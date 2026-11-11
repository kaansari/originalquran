# Maqayis al-Lugha downloader

Download the entries linked from:
https://arabiclexicon.hawramani.com/ibn-faris-maqayis-al-lugha/

Requires Python 3.9 or newer. No packages need installing.

From the repository root, try two entries first:

```bash
python3 src/json/maqayis_tools/download.py --output src/json/maqayis --limit 2
```

Inspect the resulting Markdown alongside the source pages. Then download all entries:

```bash
python3 src/json/maqayis_tools/download.py --output src/json/maqayis
```

The same command resumes an interrupted run using saved HTML. Cached entries are
parsed again, allowing extraction fixes without downloading them again. The default
1.5-second request interval means thousands of entries can take several hours.
Ctrl+C stops the run; processed entries remain available.

Output:

- `raw/index.html`: original index page.
- `raw/<id>.html`: original entry pages, keyed by stable URL hashes.
- `entries/<id>.md`: Arabic heading, dictionary name, source URL, and extracted text.
- `index.json`: discovered headings and URLs, extracted text, Markdown filenames,
  downloaded count, and a `complete` flag. Undownloaded entries have no `text` field.

Use `--offline` to re-extract only cached pages without network access; a missing
required page stops the run. `--delay 3` increases the minimum request interval.
The downloader checks robots.txt before uncached requests, honors crawl delay,
records transient request failures and continues; extraction errors still stop the run.

Entries are not automatically mapped to Quran roots or merged into root notes.
Headings include inflected forms, doubled letters, and book section titles; preserve
the originals until their mappings can be reviewed.

## Verification status

Tests cover link discovery and deduplication, dictionary section isolation,
Arabic text preservation, rejection of unexpected pages, and cached resume behavior.
The extractor also has a regression fixture from the downloaded حَشْرَجَةُ page.
It preserves both Ibn Faris definition blocks in the main article and excludes
related articles. The complete dictionary has not yet been downloaded and checked.
If extraction stops, its saved raw page can be inspected and reparsed without
downloading again.

Run tests from the repository root:

```bash
python3 -B -m unittest discover -s src/json/maqayis_tools -v
```

## Implementation plan

1. Discover and deduplicate only same-host links for dictionary `book=9`.
2. Preserve cached HTML and extract only the initial Ibn Faris dictionary section.
3. Save attributed Markdown and a JSON manifest atomically; resume cached entries.
4. Test extraction and resume with controlled fixtures, then attempt a live trial.

The standard library implementation avoids an installation step. Browser automation
would add dependencies for pages that already contain server-rendered entry links.

## Expired site certificate

If the site has an expired certificate, explicitly opt out of HTTPS certificate
and hostname verification for this run:

```bash
python3 src/json/maqayis_tools/download.py --output src/json/maqayis --limit 2 --insecure
```

After inspecting the trial entries, remove `--limit 2` for the full download.
This option applies to robots.txt and entry requests, uses a per-downloader TLS
context, and leaves Python's global SSL configuration unchanged. Verification
remains enabled when the option is omitted.

## Slow or unavailable entries

The default socket timeout is 20 seconds, with no immediate retries. A timed-out
entry or transient network/HTTP failure is recorded in `skipped.json` and the
manifest; downloading continues with later entries. Rerun the same command to
retry missing pages while reusing cached successes. Skipped entries keep the
manifest's `complete` flag false. Parse errors, local file errors, and nontransient
HTTP errors still stop the download for investigation. The index and robots.txt
must be available before entry downloads can proceed.

For a fast first pass:

```bash
python3 src/json/maqayis_tools/download.py --output src/json/maqayis --insecure --timeout 15
```

For a later pass with more patience:

```bash
python3 src/json/maqayis_tools/download.py --output src/json/maqayis --insecure --timeout 60 --retries 1
```

`--timeout` limits individual socket operations, not the total page duration.
A missing page is retried on every rerun; entries successfully downloaded are
re-extracted from cache without another network request.

## Single-page dictionary browser

Build the dictionary page from the entries downloaded so far:

```bash
python3 src/json/maqayis_tools/build_page.py
```

Then open `src/maqayis.html` directly in your browser, or visit
`/maqayis.html` on the existing site. The HTML embeds the dictionary and browser logic, and uses the shared site scripts
and theme alongside it. Keep the page with the site assets; it needs no external
library or API. Shared navigation and theme changes also apply to this page. When
served by the existing site, its Quran roots link opens the existing root page.

The browser supports Arabic letter selection, headword and definition search,
search without vowel marks, doubled root spellings such as `أبب`, incremental
result lists, previous/next entries, shareable entry fragments, dark mode, vowel
visibility, and adjustable text size. The layout stacks the list and reader on
small screens. Dictionary text is inserted as text nodes, not executable HTML.

The builder reads the download directory without changing it. Markdown definitions
are preferred over manifest text so a file downloaded after the latest manifest
checkpoint is included. Headings without downloaded definitions remain browsable,
with a link to the original entry. The header distinguishes indexed headwords
from available definitions. The page is a snapshot; rerun the build command after
the download finishes, or whenever more entries arrive, then reload the page.

`--source` and `--output` can override the default paths:

```bash
python3 src/json/maqayis_tools/build_page.py --source src/json/maqayis --output src/maqayis.html
```

The latter puts it alongside `root.html`; the builder adjusts its Quran roots link
to the output location automatically.

Tests:

```bash
python3 -B -m unittest discover -s src/json/maqayis_tools -v
node src/json/maqayis_tools/test_browser_core.js
```


## Definitions on the Roots page

The builder also writes `json/maqayis-root-index.json` beside the generated page.
The Roots page uses this compact headword index and loads matching Markdown entries
on demand. Rebuild after adding downloaded definitions to refresh both views:

```bash
python3 src/json/maqayis_tools/build_page.py
```

`--root-index` overrides the lookup output path. Root matching uses the dictionary's
Arabic normalization, ignores vowel marks and tatweel, and recognizes doubled roots.
