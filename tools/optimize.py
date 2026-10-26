#!/usr/bin/env python3
"""Post-build speed pass (run by build.py): WebP variants, <picture>, lazy/async, hero preload, inline CSS."""
import os, re, glob
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = f"{ROOT}/assets/img"
def webp(name, w, suffix=""):
    src = f"{IMG}/{name}"; base = os.path.splitext(name)[0]; out = f"{IMG}/{base}{suffix}.webp"
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        i = Image.open(src); i.thumbnail((w, 10000))
        i.save(out, "WEBP", quality=78, method=6) if i.mode in ("RGBA","LA","P") and name.endswith(".png") else i.convert("RGB").save(out, "WEBP", quality=78, method=6)
    return f"{base}{suffix}.webp"
CSS = open(f"{ROOT}/assets/style.css").read()
CSS = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S); CSS = re.sub(r"\s*\n\s*", "", CSS)
def page(path):
    h = open(path).read()
    if "data-opt" in h: return
    pre = re.search(r'href="((?:\.\./)*)assets/style\.css"', h).group(1)
    # hero background -> image-set webp + preload
    m = re.search(r'background-image:url\(((?:\.\./)*)assets/img/([\w-]+\.jpg)\)', h)
    if m:
        w = webp(m.group(2), 1600)
        h = h.replace(m.group(0), f"background-image:url({m.group(1)}assets/img/{m.group(2)});background-image:image-set(url({m.group(1)}assets/img/{w}) type('image/webp'),url({m.group(1)}assets/img/{m.group(2)}) type('image/jpeg'))")
        h = re.sub(r'<link rel="preload" as="image" href="[^"]*">\n?', "", h)
        h = h.replace('<link rel="icon"', f'<link rel="preload" as="image" href="{pre}assets/img/{w}" type="image/webp" fetchpriority="high">\n<link rel="icon"', 1)
    # <img> -> <picture> with webp; lazy+async for content images
    def r(mm):
        tag = mm.group(0); src = re.search(r'src="([^"]+)"', tag).group(1); name = src.rsplit("/", 1)[1]
        if not os.path.exists(f"{IMG}/{name}"): return tag
        icon = name.endswith(".png")
        w = webp(name, 88 if "logo" in name else 80 if icon else 800, "-sm" if icon else "-800")
        if not icon:
            if "loading=" not in tag: tag = tag.replace("<img", '<img loading="lazy"')
        if "decoding=" not in tag: tag = tag.replace("<img", '<img decoding="async"')
        return f'<picture><source srcset="{src.rsplit("/",1)[0]}/{w}" type="image/webp">{tag}</picture>'
    h = re.sub(r"<img [^>]*>", r, h)
    # inline the (tiny) stylesheet -> no render-blocking request
    h = re.sub(r'<link rel="stylesheet" href="(?:\.\./)*assets/style\.css">', lambda _: f'<style data-opt>{CSS}</style>', h)
    open(path, "w").write(h)
for p in glob.glob(f"{ROOT}/**/index.html", recursive=True): page(p)
