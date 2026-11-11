# Root reader refactor

User requested a small refactor preserving behavior, not a new architecture.

- Extract root.html's inline application script into the currently unused src/js/root.js.
- Share audio playback, word audio URLs, morphology table/popups and root links through
  common.js; keep root-specific selection/search/rendering and app.js pagination separate.
- Remove unreferenced app_writing.js. Preserve current root statistics work.
- Update behavioral tests to execute the external root script and add shared interaction
  tests for word audio, switching playback, escaped popup content, root links and dismissal.
- Verify reader, root search, statistics, dictionary, navigation and asset references.

No framework, build system, data migration, or changes to public page paths.

Implementation complete. The previous root.js stub was unreferenced and replaced;
public root.html and reader page paths remain unchanged. Regression checks execute
the external script, cover all five search modes, statistics and dictionary hooks,
and test the shared popup/audio behavior. Browser visual verification remains unavailable.
