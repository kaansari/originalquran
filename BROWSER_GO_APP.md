# Original Quran — Go browser app

This version is a web application served by Go. It is not a desktop wrapper.

## Run locally

```bash
go run .
```

Then open:

- http://localhost:8080

You can choose another address/port:

```bash
go run . -addr :3000
```

## Deploy

The app respects the standard `PORT` environment variable, so it can run on common Go hosting platforms and containers.

```bash
PORT=8080 ./originalquran
```

Build it with:

```bash
go build -o originalquran .
```

## Browser offline installation

The site includes a Web App Manifest and Service Worker. Once served over HTTPS (or localhost), compatible browsers can install it as an app. The service worker caches the Quran pages, scripts, styles, local fonts, and JSON datasets so the installed browser app works offline.

Audio and external manuscript/reference links still require internet because those remote media/files are not bundled in this repository.
