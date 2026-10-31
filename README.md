# Memoire's Restaurant & Event Center

Static site · 2201 N 44th Ave, Minneapolis, MN 55412 · 612.223.3679

## How it works
- **`data/site.json`**: single source of truth (NAP, hours, menus, prices, events, the "need from client" list).
- **`tools/build.py`**: generates every page as `/path/index.html` (clean URLs), plus `sitemap.xml`, `robots.txt`,
  `_redirects` and `_headers`, then runs the build-time QA. The build fails if any QA check fails.
- Cloudflare Pages: no build command, output directory `/`. Every push to `main` deploys.

## Edit content
Change `data/site.json` (or page copy in `tools/build.py`), run `python3 tools/build.py`, commit, push.

## Going live on a custom domain
Set `site_url` to the domain and `"indexable": true` in `data/site.json`, rebuild, push.
While `indexable` is false, every page is `noindex` (preview host).
