# Indian Quran

Approved direction: a separate Indian Quran page using the existing shared reader, Qudratullah's 610-page / 15-line edition and its matching IndoPak Nastaleeq text and font. Existing readers keep their text and layouts.

Edition configuration supplies the pagination file, word file, optional exact line file, font and bookmark key. Printed lines are data, never calculated by dividing verses or counting words. Page rendering must support verses split across lines or pages. Selected-verse mode may flow naturally.

Use QUL resources 12 (layout), 59 (word-by-word text), and 242 (font), with source attribution. Validate the imported files together before publishing the new navigation link. Missing or incompatible assets must produce a useful error, never substitute Uthmani words while labeling them IndoPak.

Source exports have been supplied by the user in tools/json.zip and tools/indopak-nastaleeq.json.zip. The importer validates and preserves the word export verbatim, using word IDs from the layout. Two redundant layout text-preview discrepancies are recorded in provenance. Four explicit split/join mappings keep the shared morphology references correct. The matching font is loaded from Quran Foundation’s documented CDN. Browser visual verification remains unavailable in this environment.
