# Site Consistency Implementation Plan

> Execute inline using superpowers:executing-plans. User authorized proceeding.

**Goal:** Consistent chrome, theme, loading and errors without changing reading engines.
**Architecture:** Shared site.js manages status and chrome; common.js uses its load tracker.
Existing HTML retains all functional control IDs; site-theme.css provides scoped styling.
**Tech Stack:** Static HTML, CSS, vanilla JavaScript, Node tests, Python checks.
**Spec:** docs/superpowers/specs/2026-11-10-site-consistency-design.md

## Global Constraints
Preserve Arabic fonts, writing guide geometry and all page-specific reading controls.
Retain cream-and-green appearance. No new production dependencies or artificial delays.

## Review Focus
Fast cached loads must not flash; overlapping requests must all settle; failed requests
must stop spinning; dictionary regeneration must retain shared chrome; mobile arrows
must remain compact. Test shared state with deterministic timers and page integration.

## Tasks
- [x] Test delayed loading, concurrency, double completion, failures and subsequent retry.
- [x] Implement shared status tracker and accessible status/retry UI; wire JSON and random rendering.
- [x] Unify header navigation, settings accessibility, theme and responsive control styles.
- [x] Update dictionary template and generated HTML without changing dictionary data.
- [x] Verify JavaScript, HTML assets, existing dictionary tests and available browser checks.

## Decisions
Work in the current checkout to preserve the user's workspace and avoid duplicating the
large dictionary archive. No commit or publish requested. Existing application engines
continue owning their settings checkboxes; the shared theme button uses those controls
where available to avoid double toggles.


## Verification record
17 Node tests cover loading lifecycle, request parsing/failure/timeout, navigation,
theme persistence, dictionary colors, keyboard settings and custom-output links.
15 Python dictionary tests and the existing JavaScript dictionary search checks pass.
All ten pages retain their previous functional IDs; assets and inline scripts validate.
The embedded dictionary dataset is unchanged; a custom-output build resolves shared assets.
Independent review findings (dictionary header selector and custom-output paths) were
fixed with regression checks. Browser visual verification remains unavailable: sandbox
blocks local listening sockets and the installed headless Chrome crashes at launch.


## Follow-up execution: remove hamburger menus
- [x] Test all ten pages have a linked logo and no hamburger controls.
- [x] Move reader options to visible labeled controls; preserve existing font choices.
- [x] Move dictionary reading controls into its toolbar in template and generated page.
- [x] Remove obsolete hidden theme-checkbox handlers; retain the shared theme button.
- [x] Exercise actual reader translation/font event handlers in a VM on five pages.
- [x] Keep alternate-reading and repository links in shared navigation.
Browser visual checks remain blocked by the environment as recorded above.
