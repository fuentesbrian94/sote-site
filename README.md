# Salt of the Earth Cleaning Co. — static site (PREVIEW, not indexable)

32 pages, plain HTML + one CSS file (`assets/style.css`), all images local in `assets/img/`.
All links are relative, so it works at a domain root or a GitHub Pages subpath (e.g. `/sote-site/`).

## Rebuild
`python3 tools/build.py` (needs `pip install markdown pillow`). Copy comes from `/workspace/sq-clip/md` and
`/workspace/squarespace-site/copy`. The homepage is generated from `tools/home.template.html` — edit the template, not `index.html`.

## Launch checklist (flip to indexable)
1. Set `BASE` at the top of `tools/build.py` to the real URL (e.g. `https://sotecleaningco.com/`) and rerun the build. That updates canonicals, Open Graph, JSON-LD and sitemap.xml everywhere, homepage included.
2. Remove `<meta name="robots" content="noindex, nofollow">`: delete that line from the `page`/`shell` templates in `tools/build.py` and from `tools/home.template.html`, then rebuild.
3. Replace `robots.txt` with the Allow block commented inside it (and point Sitemap at the real domain).
4. Submit sitemap.xml in Google Search Console / Bing Webmaster Tools.
