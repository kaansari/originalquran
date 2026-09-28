# Deploying Original Quran from GitHub

This repository supports two delivery modes from the same `src/` web application:

1. **GitHub Pages (recommended for your current hosting):** GitHub serves the PWA as static HTTPS files. The service worker makes it installable and usable offline after the assets are cached.
2. **Go server:** `go run .` serves the same `src/` directory through the embedded Go HTTP server. Use this when deploying to a host that actually runs Go processes.

## GitHub Pages setup

The workflow at `.github/workflows/deploy-pages.yml` automatically deploys on every push to `main`.

In the GitHub repository:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **GitHub Actions**.
3. Push this project to the `main` branch.
4. Open **Actions** and confirm **Deploy Original Quran to GitHub Pages** completes successfully.
5. The deployment URL is shown in the workflow run and in **Settings → Pages**.

No repository-name configuration is required. Site URLs, the manifest, and the service worker use relative paths, so both a project URL such as `https://USERNAME.github.io/REPOSITORY/` and a custom domain work.

## Offline/PWA behavior

GitHub Pages provides HTTPS, which lets browsers register the service worker. Once the first cache is populated, the Quran pages, local fonts, scripts, and bundled JSON data can work without a network connection. External audio and third-party manuscript/reference links remain network-dependent.

The main page now includes an **Install App** button. In Chrome/Edge, clicking it opens the browser install prompt once the PWA is eligible. Safari shows platform-specific installation guidance. When a newer deployed service worker is waiting, an **Update App** button appears; clicking it activates the new version and reloads the page.

Home/menu navigation uses `./` rather than `index.html`, so the home URL stays clean and works both at a GitHub project path such as `/originalquran/` and at a custom-domain root.

## Go mode

GitHub Pages cannot execute `main.go`. To test the Go version locally:

```bash
go run .
```

Then open `http://localhost:8080`.

If you later deploy to a Go-capable service, it can build this same repository and run the Go server without changing the frontend.

## Repository layout

- `src/` — public browser/PWA files (this is what GitHub Pages publishes)
- `main.go` — optional Go HTTP server for local or server hosting
- `tools/analysis/` — analysis/Python tooling kept outside the public web root
- `scripts/` — data preparation scripts, also not published by Pages
- `.github/workflows/deploy-pages.yml` — GitHub Pages deployment workflow
