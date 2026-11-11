# Indian Quran Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add Indian Quran with accurate Qudratullah pages and an extensible edition configuration.

**Architecture:** Keep app.js as the reader controller. Add a pure line-layout adapter and a validated offline import command for the matching QUL files. Page metadata selects each edition's files and independent bookmark.

**Tech Stack:** Static HTML/CSS/JavaScript, Python standard library, Node test runner.

**Spec:** docs/superpowers/specs/2026-11-11-indian-quran-design.md

## Global Constraints

- Preserve existing text, page navigation direction, translations and word interactions.
- Indian Quran uses Qudratullah's 610-page, 15-line edition.
- Never synthesize printed line breaks or substitute another script.
- Source files must be obtained and validated before advertising the edition as ready.

## Review Focus

- Split verses need exact word boundaries on both pages.
- Verse-ending markers are source tokens, not extra lexical words.
- Different word numbering must map to existing morphology explicitly.
- Small screens must preserve full lines without clipping.
- Missing data or fonts must fail visibly instead of displaying wrong text.

### Task 1: Reproducible source import

Files: scripts/build_indian_quran.py, tests/test_indian_quran.py.

- [x] Test a small QUL-shaped fixture: line order, word mapping, end markers, split verses, invalid gaps and missing text.
- [x] Implement import from layout JSON or SQLite and word JSON or SQLite into shared-reader pagination, lexical words, line layout and provenance files.
- [x] Validate all 610 pages and all 6,236 verses when running production import.

### Task 2: Optional exact-line rendering

Files: src/js/reader-layout.js, src/app.js, tests/reader-layout.test.js.

- [x] Test that mixed verses on a line and split verses on different pages preserve source order.
- [x] Add optional quran-lines-file metadata and load lines alongside existing local data.
- [x] Replace flowing Arabic only in page mode; keep translation and shared word interactions.

### Task 3: Indian Quran page and verification

Files: src/indian.html, src/indian.css, README.md, src/site.js.

- [x] Add an edition page configured for imported assets and the matching font.
- [x] Install real source files and configure the documented matching font before adding public navigation.
- [ ] Browser visual verification of the font and mobile geometry (Chrome aborts in this environment).
- [x] Run the complete existing automated suite and review the changed code.

## Execution record

The user approved the separate-page direction and asked us to proceed. Work continues in the existing shared workspace to preserve their current local changes. No commit or push is requested for this turn. Actual source exports are a dependency, not an invitation to invent layout data.

Source exports supplied by the user in tools/json.zip and tools/indopak-nastaleeq.json.zip have now been imported. All 610 pages, 6,236 verses and 83,668 source tokens validate. Independent review confirms generated token text matches the source exactly, including four explicit tokenization mappings. The menu now includes Indian Quran. The matching font URL is verified against Quran Foundation documentation; live font loading and mobile visual comparison remain unverified because Chrome aborts and terminal network access is unavailable. A pure geometry simulation tests line fitting, and actual data integration tests cover navigation, independent bookmarks, font selection, selected ranges and the final page.
