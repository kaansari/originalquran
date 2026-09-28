package main

import (
	"embed"
	"flag"
	"fmt"
	"io/fs"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

// Browser application assets are embedded into the Go server binary.
// The browser can also install/cache the app as a PWA for offline use.
//
//go:embed src
var content embed.FS

type securityHeaders struct{ next http.Handler }

func (h securityHeaders) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.Header().Set("X-Frame-Options", "SAMEORIGIN")
	w.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")
	w.Header().Set("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

	// Service workers should always be revalidated so browser clients pick up updates.
	if r.URL.Path == "/sw.js" || strings.HasSuffix(r.URL.Path, ".html") || r.URL.Path == "/" {
		w.Header().Set("Cache-Control", "no-cache")
	} else {
		w.Header().Set("Cache-Control", "public, max-age=3600")
	}
	h.next.ServeHTTP(w, r)
}

func main() {
	defaultAddr := ":8080"
	if port := os.Getenv("PORT"); port != "" {
		defaultAddr = ":" + port
	}

	addr := flag.String("addr", defaultAddr, "listen address (or set PORT for deployment)")
	flag.Parse()

	site, err := fs.Sub(content, "src")
	if err != nil {
		log.Fatalf("open embedded site: %v", err)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		_, _ = w.Write([]byte(`{"status":"ok"}`))
	})
	mux.Handle("/", http.FileServer(http.FS(site)))

	server := &http.Server{
		Addr:              *addr,
		Handler:           securityHeaders{next: mux},
		ReadHeaderTimeout: 5 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	fmt.Printf("Original Quran browser app: http://localhost%s\n", *addr)
	fmt.Println("The Go server serves the website; install it from your browser for offline use.")
	log.Fatal(server.ListenAndServe())
}
