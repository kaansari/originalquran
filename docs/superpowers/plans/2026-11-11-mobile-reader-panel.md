# Mobile reading panel

User-approved scope: Eastern Reading (`index.html` and its `page.html` alias) and Western Reading (`warsh.html`) only. Quran content uses 85% of the available mobile viewport; the remaining 15% holds chapter/page controls and arrows. Existing navigation and secondary settings expand upward from this panel. Shrink content to fit rather than introducing a reading scrollbar. Other readers remain unchanged.

- Preserve the existing control elements and handlers by moving nodes, never cloning them. Restore their desktop positions when the viewport changes.
- Keep the shared reader from moving a docked heading back into the reading area on page changes.
- Fit actual rendered Arabic and enabled translation text using a shared scale variable, measured after layout, font loading and control changes. Never truncate or remove words.
- Respect the iPhone safe area and changing browser viewport height. Retain page arrows; no swipe navigation.
- Verify node movement, desktop restoration, shrinking and shared-reader page changes with regression tests. Run all reader and dictionary tests. Browser/iPhone visual verification is unavailable in this environment and must not be claimed.

Implementation files: `src/js/mobile-reader.js`, `src/mobile-reader.css`, the three reader HTML files, and the shared heading placement in `src/app.js`.

Scope extension requested by the user: apply the same mobile layout to Old Quran
and Indian Quran, preserving Qahiri italics and Indian's 15 printed line slots.
The whole-page fitter takes over from per-line font fitting on mobile; desktop
restoration reinstates per-line fitting. Indian page credits have moved into
README.md, with the original source metadata and archives retained.
