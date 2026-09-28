# Merge these fixes into your existing GitHub repository

This package changes only three website files for the loader / PWA control fix:

- `src/index.html`
- `src/styles_page.css`
- `src/sw.js`

## Safest method: use the small patch ZIP

1. In Terminal, go to your existing repository:

   ```bash
   cd /path/to/your/originalquran
   ```

2. Make sure your current work is saved:

   ```bash
   git status
   ```

   If you have uncommitted changes you want to keep, commit them first:

   ```bash
   git add .
   git commit -m "Save current work before PWA UI fix"
   ```

3. Create a branch for this update:

   ```bash
   git switch -c fix/pwa-loader-install-ui
   ```

4. Unzip `originalquran-pwa-loader-patch.zip` directly over the repository root. It contains the same `src/...` paths and will replace only the three files listed above.

5. Review exactly what changed:

   ```bash
   git diff -- src/index.html src/styles_page.css src/sw.js
   ```

6. Test locally:

   ```bash
   go run .
   ```

   Then open `http://localhost:8080/`.

7. Commit the fix:

   ```bash
   git add src/index.html src/styles_page.css src/sw.js
   git commit -m "Fix PWA loader and move install controls"
   ```

8. Push the branch:

   ```bash
   git push -u origin fix/pwa-loader-install-ui
   ```

9. Either create a Pull Request on GitHub and merge it, or merge locally:

   ```bash
   git switch main
   git pull origin main
   git merge fix/pwa-loader-install-ui
   git push origin main
   ```

Your existing GitHub Pages workflow should then deploy the updated `src/` automatically.

## After GitHub Pages deploys

Because an older service worker may still control an already-installed copy, open the site while online and refresh. The new service worker is `originalquran-v6`; the page will now prefer fresh HTML/CSS/JS when online and keep cached Quran data for offline use.
