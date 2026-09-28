# Fixed / Offline Go Edition changes

## Correctness and runtime fixes

- Removed the duplicated second copy of `src/app.js` from the prior cleanup.
- Fixed deployment-sensitive favicon paths.
- Fixed accidental global `vpage` variables.
- Fixed secondary viewers validating a saved ayah against the wrong dataset index.
- Made font preference keys independent of a GitHub Pages `/originalquran/` path so the same build works at `/`, a subfolder, or the local Go server.
- Disabled page navigation until pagination data is loaded.
- Added HTTP-status checking for local JSON loads through the shared `QuranUtils.loadJSON` helper.

## Offline/UI fixes

- Removed Font Awesome CDN dependency and replaced it with a tiny local icon stylesheet.
- Removed Google Fonts dependencies from application stylesheets.
- Reused bundled Quran fonts and system UI fonts instead.
- Fixed the undefined `var(--latin-fonts)` CSS variable typo.
- Fixed invalid `--verse-text-color: color: ...` declarations in the writing stylesheet.
- Added a small offline-status banner.
- Quran text, translation data, local fonts, root search, navigation, and morphology datasets are local.
- Audio and Corpus Coranicum/external sharing links remain optional online-only features and now fail gracefully offline.

## Safety / maintainability fixes

- External links opened in a new tab use `noopener/noreferrer` behavior.
- Morphology popup values are escaped before template insertion.
- Plain translation rendering in the primary page viewer uses `textContent`.
- Shared JSON-loading, escaping, offline detection, and safe-new-tab helpers moved into `src/common.js`.
- The Go server binds to loopback (`127.0.0.1`) by default and adds `nosniff`, frame-deny, referrer, and permissions headers.

## Go offline application

- Added `go.mod` and `main.go`.
- Web assets are compressed into `web/site.zip` and embedded into the executable.
- The app starts a private local HTTP server on a free port and opens the default browser.
- Added `/healthz` for a simple local health check.
- Added `-no-browser`, `-page`, and `-addr` flags.
- Prebuilt macOS Intel, macOS Apple Silicon, Windows x64, and Linux x64 executables are provided separately.
