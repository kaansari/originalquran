# Consistent site interface

Approved direction: retain the cream-and-green appearance, standardize shared navigation,
settings presentation, responsive controls, theme preferences, loading and errors across
all ten top-level HTML pages in src. Preserve Arabic fonts, writing guide geometry,
selectors, dictionary search, verse links, translations, audio and saved reading position.

Use small shared scripts and CSS on the existing static pages. Preserve page-specific
engines and control IDs rather than rewriting them. A delayed, nonblocking loading
status follows actual pending work; no artificial minimum duration or fabricated
percentage. Failures show a persistent message and reload retry. Theme preference is
shared, including the dictionary. Keep generated dictionary output and template aligned.

Alternatives: independent fixes would continue duplication; a framework conversion
would add unnecessary migration risk. Shared vanilla JavaScript fits existing hosting.
Verify runtime behavior, existing dictionary tests, page assets and mobile layouts.


## Follow-up: visible page controls
User requested removing hamburger menus and moving their controls onto the relevant
pages. Use the existing site logo in the home link on every page. Keep the shared
navigation and theme button; move translation/font options to a visible reading
options row. Keep existing writing font selectors without duplicating them. Move
dictionary vowel and text-size controls to the reader toolbar and its source link
to the footer. Preserve IDs, font choices and preferences, and remove theme code
that relied on the removed hidden checkbox. Keep repository and alternate-reading
links in shared navigation.
