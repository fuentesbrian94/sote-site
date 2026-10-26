#!/usr/bin/env python3
"""Builds inner pages from sq-clip/md copy. BASE = canonical base URL (change at launch)."""
import re, json, os, markdown
from PIL import Image
BASE = "https://example.com/sote-site/"   # <-- change at launch
MD = "/workspace/sq-clip/md"; COPY = "/workspace/squarespace-site/copy"; PH = "/workspace/yelp-photos-from-google"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUOTE = "https://sparkle-book-85ab8582.base44.app/"
CITIES = ["Richardson","Plano","Garland","Dallas","Murphy","Wylie","Sachse","Allen","Rowlett","Frisco","McKinney","Arlington","Fort Worth","Denton"]
# slug: (kind, crumb, hero photo, alt, service name / city)
PAGES = {
 "standard-house-cleaning": ("service","Standard Cleaning","24","Clean bathroom double vanity after a standard house cleaning","Standard House Cleaning"),
 "deep-cleaning": ("service","Deep Cleaning","41","Deep-cleaned kitchen island and farmhouse sink","Deep Cleaning"),
 "recurring-cleaning": ("service","Recurring Cleaning","39","Tidy living room maintained with recurring house cleaning","Recurring House Cleaning"),
 "move-in-move-out-cleaning": ("service","Move-In/Move-Out","45","Empty living room cleaned for move-out","Move-In and Move-Out Cleaning"),
 "airbnb-cleaning": ("service","Airbnb Cleaning","40","Clean, empty bedroom ready for the next guest","Airbnb and Short-Term Rental Cleaning"),
 "post-construction-cleaning": ("service","Post-Construction","47","Newly renovated room during post-construction cleanup","Post-Construction Cleaning"),
 "house-cleaning-service-areas-dfw": ("area","Service Areas","14","Bright, freshly cleaned living room","Dallas–Fort Worth"),
 "house-cleaning-richardson-tx": ("city","Richardson","17","Clean vintage tile bathroom in a classic ranch home","Richardson"),
 "house-cleaning-plano-tx": ("city","Plano","46","Stair rails and floors cleaned in a two-story home","Plano"),
 "house-cleaning-garland-tx": ("city","Garland","42","Clean, empty home ready for move-in","Garland"),
 "house-cleaning-north-dallas-tx": ("city","North Dallas","08","Spotless bathroom with marble and glass","Dallas"),
 "faq": ("faq","FAQ","05","Clean tile bathroom floor and vanity",None),
}
BUILT = set(PAGES) | {""}
def img(n):
    import glob
    src = glob.glob(f"{PH}/photo-{n}.*")[0]; out = f"{ROOT}/assets/img/p{n}.jpg"
    if not os.path.exists(out):
        i = Image.open(src); i.thumbnail((1600,1600)); i.convert("RGB").save(out, quality=78, optimize=True)
    return f"p{n}.jpg"
def seo(slug):
    t = open(f"{COPY}/{slug}.md").read()
    g = lambda k: re.search(rf"\*\*{k}[^*]*:\*\*\s*(.+)", t).group(1).strip()
    return g("SEO title"), g("Meta description")
def hero(slug):
    d = {}
    for l in open(f"{MD}/{slug}-hero.txt"):
        if ":" in l: k, v = l.split(":", 1); d[k.strip()] = v.strip()
    return d
def esc(s): return s.replace("&","&amp;").replace('"',"&quot;").replace("<","&lt;")
def fixlinks(h, pre):
    def r(m):
        p = m.group(1).strip("/")
        return f'href="{pre}{p + "/" if p else ""}"'
    return re.sub(r'href="/([^"#]*)"', r, h)
def nav(pre):
    return f'''<header class="site"><div class="wrap">
<a class="brand" href="{pre}"><img src="{pre}assets/img/logo.png" alt="Salt of the Earth Cleaning Co. logo" width="44" height="44">Salt of the Earth Cleaning Co.</a>
<nav aria-label="Main"><a href="{pre}deep-cleaning/">Deep</a><a href="{pre}recurring-cleaning/">Recurring</a><a href="{pre}move-in-move-out-cleaning/">Move-Out</a><a href="{pre}house-cleaning-service-areas-dfw/">Areas</a><a href="{pre}reviews/">Reviews</a><a href="{pre}blog/">Blog</a><a href="{pre}faq/">FAQ</a><a href="{pre}about/">About</a></nav>
<a class="btn" href="{QUOTE}">Get My Instant Quote</a>
</div></header>'''
def footer(pre):
    L = lambda s, n: f'<a href="{pre}{s}/">{n}</a><br>'
    return f'''<footer><div class="wrap cols">
<div><strong>Salt of the Earth Cleaning Co.</strong><br>Serving all of Dallas–Fort Worth · Based in Richardson, TX<br><a href="tel:+14692108005">(469) 210-8005</a><br><a href="mailto:info@sotecleaning.com">info@sotecleaning.com</a><br>Mon–Sun 8:30 AM–7:30 PM</div>
<div><strong>Services</strong><br>{L("deep-cleaning","Deep Cleaning")}{L("recurring-cleaning","Recurring Cleaning")}{L("move-in-move-out-cleaning","Move-In/Move-Out")}{L("standard-house-cleaning","Standard Cleaning")}{L("airbnb-cleaning","Airbnb Cleaning")}{L("post-construction-cleaning","Post-Construction")}{L("pet-friendly-house-cleaning","Pet-Friendly Cleaning")}</div>
<div><strong>Areas</strong><br>{L("house-cleaning-richardson-tx","Richardson")}{L("house-cleaning-plano-tx","Plano")}{L("house-cleaning-garland-tx","Garland")}{L("house-cleaning-north-dallas-tx","North Dallas")}{L("house-cleaning-service-areas-dfw","All DFW areas")}</div>
<div><strong>Company</strong><br>{L("about","About")}{L("reviews","Reviews")}{L("blog","Blog")}{L("faq","FAQ")}{L("get-a-quote","Get a Quote")}</div>
</div><p class="wrap">© 2026 Salt of the Earth Cleaning Co.</p></footer>'''
BIZ = {"@type":["HouseCleaningService","LocalBusiness"],"@id":BASE+"#business","name":"Salt of the Earth Cleaning Co.","url":BASE,
 "telephone":"+1-469-210-8005","email":"info@sotecleaning.com","image":BASE+"assets/img/hero.jpg",
 "address":{"@type":"PostalAddress","addressLocality":"Richardson","addressRegion":"TX","addressCountry":"US"},
 "areaServed":[{"@type":"City","name":c+", TX"} for c in CITIES],
 "openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],"opens":"08:30","closes":"19:30"}]}
def faqs(body):
    out = []
    for m in re.finditer(r"^###\s+(.+\?)\s*\n+((?:(?!^#|^---).+\n?)+)", body, re.M):
        ans = "\n".join(l for l in m.group(2).splitlines() if not re.fullmatch(r"[\s*·→]*(\[[^\]]+\]\([^)]+\)[\s*·→]*)+", l))
        ans = "\n".join(re.sub(r"(?<=[.!?])(\s*[·→]?\s*\*{0,2}\[[^\]]+\]\([^)]+\)\*{0,2})+\s*$", "", l) for l in ans.splitlines())
        a = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", ans).replace("**","").strip()
        out.append({"@type":"Question","name":m.group(1).strip(),"acceptedAnswer":{"@type":"Answer","text":" ".join(a.split())}})
    return out
for slug, (kind, crumb, ph, alt, name) in PAGES.items():
    pre = "../"; url = BASE + slug + "/"
    title, desc = seo(slug); h = hero(slug)
    body = open(f"{MD}/{slug}-body.txt").read()
    body = "\n".join(l for l in body.splitlines() if "CONFIRM WITH BRIAN" not in l)
    html = fixlinks(markdown.markdown(body, extensions=["extra"]), pre)
    html = html.replace("<h1", "<h2").replace("</h1>", "</h2>")
    photo = img(ph)
    graph = [BIZ, {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":BASE},
        {"@type":"ListItem","position":2,"name":crumb,"item":url}]}]
    if kind == "service":
        graph.append({"@type":"Service","name":name,"serviceType":name,"url":url,"description":desc,"provider":{"@id":BASE+"#business"},
                      "areaServed":{"@type":"AdministrativeArea","name":"Dallas–Fort Worth, TX"}})
    elif kind in ("city","area"):
        graph.append({"@type":"Service","name":f"House Cleaning in {name}","serviceType":"House Cleaning","url":url,"description":desc,
                      "provider":{"@id":BASE+"#business"},"areaServed":{"@type":"City" if kind=="city" else "AdministrativeArea","name":name+", TX" if kind=="city" else "Dallas–Fort Worth, TX"}})
    f = faqs(body)
    if f: graph.append({"@type":"FAQPage","mainEntity":f})
    ld = json.dumps({"@context":"https://schema.org","@graph":graph}, ensure_ascii=False)
    quote = ""
    if h.get("QUOTE"):
        quote = "<p><em>" + markdown.markdown(h["QUOTE"])[3:-4].replace("<p>","") + "</em></p>"
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<!-- PREVIEW: remove noindex at launch (see README). Generated by tools/build.py -->
<meta name="robots" content="noindex, nofollow">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Salt of the Earth Cleaning Co.">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{BASE}assets/img/{photo}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{pre}assets/img/logo.png">
<link rel="stylesheet" href="{pre}assets/style.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
{nav(pre)}
<main>
<section class="hero" style="background-image:url({pre}assets/img/{photo})" role="img" aria-label="{esc(alt)}"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="{pre}" style="color:#fff">Home</a> › {esc(crumb)}</nav>
<h1>{esc(h["H1"])}</h1>
<p>{esc(h["SUBHEAD"])}</p>
<div class="actions"><a class="btn" href="{QUOTE}">{esc(h.get("PRIMARY_BUTTON","Get My Instant Quote"))}</a><a class="btn ghost" href="tel:+14692108005">Call (469) 210-8005</a></div>
<p>{esc(h.get("TRUST_STRIP",""))}</p>{quote}
</div></section>
<section><div class="wrap narrow prose">
<img class="lead" src="{pre}assets/img/{photo}" alt="{esc(alt)}" loading="lazy" width="780" height="520">
{html}
</div></section>
</main>
{footer(pre)}
</body>
</html>
'''
    os.makedirs(f"{ROOT}/{slug}", exist_ok=True)
    open(f"{ROOT}/{slug}/index.html", "w").write(page)
    print("built", slug, len(f), "faqs")
# sitemap of built pages
urls = [BASE] + [BASE + s + "/" for s in PAGES]
open(f"{ROOT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
