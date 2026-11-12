/* Mobile paginated-reader layout; existing controls keep their listeners. */
((root) => {
  const MEDIA = '(max-width: 620px), (max-width: 900px) and (pointer: coarse)';
  function fitPage(page) {
    if (!page.clientHeight || !page.clientWidth) return;
    const apply = scale => page.style.setProperty('--mobile-page-scale', String(scale));
    const printedLines = Array.from(page.querySelectorAll?.('.mushaf-line') || []);
    const fits = () => page.scrollHeight <= page.clientHeight + 1 && page.scrollWidth <= page.clientWidth + 1
      && printedLines.every(line => {
        const bounds = line.getBoundingClientRect();
        return Array.from(line.children).every(word => {
          const rect = word.getBoundingClientRect();
          return rect.left >= bounds.left - 1 && rect.right <= bounds.right + 1;
        });
      });
    apply(1);
    if (!fits()) {
      let low = 0.001, high = 1;
      for (let i = 0; i < 14; i++) {
        const middle = (low + high) / 2;
        apply(middle);
        if (fits()) low = middle;
        else high = middle;
      }
      apply(low);
    }
    page.scrollTop = 0;
    page.scrollLeft = 0;
  }

  function createController(document, window) {
    const page = document.getElementById('quran-container');
    const heading = document.getElementById('reader-page-heading');
    const controls = document.querySelector('.site-page-controls');
    const masthead = document.querySelector('.site-masthead');
    const filters = controls?.querySelector('.reader-filter-options');
    if (!page || !heading || !controls || !masthead || !filters) return null;
    const media = window.matchMedia(MEDIA);
    const anchors = [masthead, controls].map(node => {
      const anchor = document.createComment('reader desktop position');
      node.parentNode.insertBefore(anchor, node);
      return [anchor, node];
    });
    const dock = document.createElement('aside');
    dock.className = 'mobile-reader-dock';
    dock.setAttribute('aria-label', 'Reading controls');
    dock.hidden = true;
    document.body.appendChild(dock);
    let active = false, scheduled = false;
    const scheduleFit = () => {
      if (!active || scheduled) return;
      scheduled = true;
      window.requestAnimationFrame(() => {
        scheduled = false;
        if (active) fitPage(page);
      });
    };
    function refresh() {
      if (media.matches && !active) {
        page.dataset.fitPage = 'true';
        heading.dataset.mobileDocked = 'true';
        dock.appendChild(heading);
        dock.appendChild(controls);
        filters.appendChild(masthead);
        dock.hidden = false;
        document.body.classList.add('mobile-reader-active');
        active = true;
      } else if (!media.matches && active) {
        active = false;
        document.body.classList.remove('mobile-reader-active');
        delete heading.dataset.mobileDocked;
        delete page.dataset.fitPage;
        for (const [anchor, node] of anchors) anchor.parentNode.insertBefore(node, anchor.nextSibling);
        const arabic = page.querySelector('.arabic-text-container') || page;
        arabic.insertBefore(heading, arabic.firstChild);
        page.style.removeProperty('--mobile-page-scale');
        document.body.style.removeProperty('--mobile-reader-height');
        window.ReaderLayout?.fitLines(page);
        dock.hidden = true;
      }
      if (active) {
        const viewport = window.visualViewport;
        const height = viewport && viewport.scale === 1 ? viewport.height : window.innerHeight;
        document.body.style.setProperty('--mobile-reader-height', `${height}px`);
        scheduleFit();
      }
    }
    if (media.addEventListener) media.addEventListener('change', refresh);
    else media.addListener?.(refresh);
    window.addEventListener('resize', refresh);
    window.addEventListener('orientationchange', refresh);
    window.visualViewport?.addEventListener('resize', refresh);
    window.addEventListener('quran:ready', scheduleFit);
    document.fonts?.addEventListener?.('loadingdone', scheduleFit);
    if (window.MutationObserver) {
      new window.MutationObserver(records => {
        if (records.some(record => record.type === 'childList' || record.target !== page)) scheduleFit();
      }).observe(page, {childList: true, subtree: true, attributes: true, attributeFilter: ['style', 'class']});
    }
    refresh();
    return {refresh, fit: scheduleFit};
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = {fitPage, createController};
  else root.MobileReader = createController(document, root);
})(globalThis);
