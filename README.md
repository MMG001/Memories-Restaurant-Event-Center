# Memoire's Restaurant & Event Center

Static website for Memoire's Restaurant & Event Center — 2201 N 44th Ave, Minneapolis, MN 55412 · 612.223.3679.

## Deploy (Cloudflare Pages)
- Framework preset: **None** · Build command: *(empty)* · Output directory: `/`
- Every push to `main` deploys.

## Editing content
All page content (menus, prices, events, FAQ, hours) lives in `tools/build.py`.
Edit it, then run `python3 tools/build.py` to regenerate the `.html` pages and commit.

## Forms
Rental and contact forms open the visitor's email app, addressed to `INQUIRY_EMAIL`
in `assets/js/site.js`. Until that's set, visitors are shown their request and asked to call.
