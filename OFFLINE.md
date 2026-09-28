# Original Quran Offline (Go)

This version embeds the website, Quran JSON datasets, and local fonts directly in a single Go executable. No Node.js, Python, database, or web server is required.

## Run a prebuilt executable

Choose the executable for your operating system, open it, and the Quran viewer will launch in your default browser on a private local address (`127.0.0.1`). Nothing is uploaded to a remote server.

- macOS Apple Silicon: `OriginalQuran-mac-arm64`
- macOS Intel: `OriginalQuran-mac-amd64`
- Windows 64-bit: `OriginalQuran-windows-amd64.exe`
- Linux 64-bit: `OriginalQuran-linux-amd64`

The command window/terminal must remain open while you use the app. Close it or press Ctrl+C to stop the local server.

## Build it yourself

Install Go 1.23 or newer, then from the project directory run:

```sh
go build -o OriginalQuran .
```

Run `./OriginalQuran` (macOS/Linux) or `OriginalQuran.exe` (Windows).

Useful options:

```sh
./OriginalQuran -no-browser
./OriginalQuran -page root.html
./OriginalQuran -addr 127.0.0.1:8080
```

## Offline behavior

The Quran text, local Quran fonts, page/verse navigation, translations, root/search data, and morphology datasets are bundled and work without internet access.

Audio playback and links to external manuscript/reference websites are still online features because their media/content is not included in this repository. When offline, the UI now explains that instead of repeatedly trying a remote request.
