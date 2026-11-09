# Root notes

Write free-form notes in Markdown files under `data/notes_dir/`. Point to each
file from `data/root_notes.json`:

```json
{
  "رزق": {
    "source": "notes_dir/رزق.md"
  }
}
```

Paths are relative to `data/root_notes.json`. The example resolves to
`data/notes_dir/رزق.md`. Use ordinary Markdown with paragraphs, headings, lists,
and links. There is no required structure inside the file and no need to escape
newlines or quotation marks for JSON. Put brief meanings and longer explanations
in the same Markdown file as desired.

Run `python3 scripts/rootwordsjson.py --notes-only` from the repository root to
publish notes into `src/notes/` and update `src/json/root_notes.json` without
regenerating the Quran root index or CSV report. Only indexed notes are published.

Run `python3 scripts/rootwordsjson.py` to also copy your
Markdown text into `Notes` for that root in `src/json/root_words.json` and
regenerate the CSV report.
Empty notes are omitted. The generator checks root keys and source paths before
writing output; missing files cause generation to fail. Source paths must be
relative `.md` paths within `data/`. It never rewrites your Markdown files.

Run the generator check with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts -p 'test_rootwordsjson.py'
```

The eight trial entries have been moved into Markdown files, including the
rizq/risk explanation and its links. Their short meanings remain editable drafts
adapted from the [Quranic Arabic Corpus](https://corpus.quran.com/),
Copyright © Kais Dukes, 2009–2017, under its
[license](https://corpus.quran.com/license.jsp) and
[terms of use](https://corpus.quran.com/download/).
Morphology popups show a Notes link for roots with a published, nonempty note.
The link opens the Markdown file in a new tab. Roots without notes have no Notes
row. Published notes are cached with the app for offline access after the updated
service worker installs. When deploying later note changes, bump `CACHE_NAME` in
`src/sw.js` so installed apps refresh their cached note index and files.
