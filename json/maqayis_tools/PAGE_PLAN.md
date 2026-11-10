# Maqayis single-page browser

Build a standalone HTML dictionary page that works when opened directly and when
served from the existing src directory. Use the existing download as a read-only
source while it continues running. Keep all implementation files under the writable
src/json directory; do not change the site's deployment or current Quran pages.

The page uses a restrained ivory/forest reading layout, English controls with
Arabic headings and right-to-left definitions, Arabic letter browsing, normalized
Arabic search across headings and definitions, a selectable result list, previous
and next entry navigation, dark mode, and adjustable reading size. On small screens
the result list and reader stack. Search results are progressively displayed.
Use semantic controls, visible focus, status announcements, and safe DOM text.

Tasks:
1. Test and implement a snapshot builder that reconciles index metadata with all
   available Markdown, including files newer than the current download manifest.
2. Test and implement search normalization, exact-headword ranking, letter filters,
   and missing-definition handling in a shared dependency-free JavaScript module.
3. Implement the HTML template and embed the snapshot and scripts into one page.
4. Run Python and JavaScript tests, validate the generated artifact, and attempt
   browser QA using the installed Chrome. Record browser limits if restricted.

Rebuild after downloading completes with build_page.py. The page is a static
snapshot and never reads or writes the running downloader's output in the browser.
