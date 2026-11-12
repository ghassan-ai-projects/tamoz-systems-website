#!/usr/bin/env python3
"""SEO/GEO pass for the designs in designs/*.html. Safe to re-run.

- fixes <html lang>, charset, self-hosted fonts
- sets title + meta description per design (CONFIG below)
- writes canonical, icons, Open Graph, Twitter card and a JSON-LD @graph
  (Organization, WebSite, WebPage, FAQPage built from the page's own <dl class="faq">)
  between <!-- seo:start --> and <!-- seo:end -->
- adds a visually hidden keyword prefix inside the <h1>
- turns the JS-filled empty <h2 id="logTitle"> into a <p>

Usage: python3 scripts/seo.py && ./switch.sh homepage
Only put verified facts into ORG.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://tamoz-systems.com/"

ORG = {
    "@type": "Organization",
    "@id": SITE + "#organization",
    "name": "Tamoz",
    "url": SITE,
    "logo": {"@type": "ImageObject", "url": SITE + "img/icon-512.png", "width": 512, "height": 512},
    "description": "Tamoz is an AI operator for IoT sensors and physical equipment. It watches sensor data, "
                   "works out what each change means, acts within fixed limits and asks a person before anything risky.",
    # Fill only once confirmed: "legalName", "email", "address", "foundingDate", "sameAs"
}

CONFIG = {
    "homepage": {
        "title": "Tamoz – AI Operator for IoT Sensors and Equipment Alarms",
        "description": "Tamoz watches your sensor data around the clock, works out what each alarm means, "
                       "acts within fixed limits and asks a person before anything risky.",
        "h1_prefix": "Tamoz, the AI operator for IoT equipment alarms: ",
    },
    "manufacturing": {
        "title": "Tamoz for Manufacturing – AI Operator for Factory Alarms",
        "description": "Tamoz watches machine and utility data in your plant, works out what each alarm means, "
                       "acts within fixed limits and asks a person before anything risky.",
        "h1_prefix": "Tamoz for manufacturing, the AI operator for factory alarms: ",
    },
    "conveyor": {
        "title": "Tamoz for Belt Conveyors – AI Operator for Conveyor Drives",
        "description": "Tamoz compares each conveyor drive with its peers, predicts when a failing drive "
                       "will trip, and asks a person to stop it by plan before the belt strands.",
        "h1_prefix": "Tamoz for belt conveyors, the AI operator for multi-drive conveyors: ",
    },
}

HIDDEN_CSS = (".visually-hidden{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;"
              "clip:rect(0 0 0 0);white-space:nowrap;border:0}")


def text(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


def faq(page):
    m = re.search(r'<dl class="faq">(.*?)</dl>', page, re.S)
    if not m:
        return None
    pairs = re.findall(r"<dt>(.*?)</dt>\s*<dd>(.*?)</dd>", m.group(1), re.S)
    return {
        "@type": "FAQPage",
        "@id": SITE + "#faq",
        "isPartOf": {"@id": SITE + "#website"},
        "mainEntity": [
            {"@type": "Question", "name": text(q),
             "acceptedAnswer": {"@type": "Answer", "text": text(a)}}
            for q, a in pairs
        ],
    }


def head_block(cfg, page):
    t, d = html.escape(cfg["title"]), html.escape(cfg["description"])
    graph = [
        ORG,
        {"@type": "WebSite", "@id": SITE + "#website", "url": SITE, "name": "Tamoz",
         "inLanguage": "en", "publisher": {"@id": SITE + "#organization"}},
        {"@type": "WebPage", "@id": SITE + "#webpage", "url": SITE, "name": cfg["title"],
         "description": cfg["description"], "inLanguage": "en",
         "isPartOf": {"@id": SITE + "#website"}, "about": {"@id": SITE + "#organization"},
         "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + "img/og-image.jpg"}},
    ]
    f = faq(page)
    if f:
        graph.append(f)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return f"""<!-- seo:start -->
<link rel="canonical" href="{SITE}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/img/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<meta name="theme-color" content="#0a1224">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Tamoz">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="{SITE}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:image" content="{SITE}img/og-image.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Tamoz logo">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{SITE}img/og-image.jpg">
<script type="application/ld+json">
{ld}
</script>
<!-- seo:end -->"""


def process(path, cfg):
    s = path.read_text(encoding="utf-8")
    s = s.replace("<!doctype html><html><head>", '<!doctype html><html lang="en"><head>', 1)
    s = s.replace("<meta charset=utf8>", '<meta charset="utf-8">', 1)
    # The exported wrapper closes <head> on line 1, which pushes title/meta/canonical into <body>.
    # Move the boundary to just before the first body element (the SVG sprite).
    first_line, rest = s.split("\n", 1)
    if first_line.endswith("</head><body>"):
        s = first_line[: -len("</head><body>")] + "\n" + rest
        s = s.replace('\n<svg width="0" height="0"', '\n</head>\n<body>\n<svg width="0" height="0"', 1)
    s = s.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")
    s = re.sub(r'<link rel="preconnect" href="https://fonts\.g[^"]*"[^>]*>\n', "", s)
    s = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*">',
               '<link rel="stylesheet" href="/fonts/fonts.css">', s)
    s = re.sub(r"<title>.*?</title>", f"<title>{html.escape(cfg['title'])}</title>", s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">',
               f'<meta name="description" content="{html.escape(cfg["description"])}">', s, count=1)
    s = re.sub(r"<!-- seo:start -->.*?<!-- seo:end -->\n?", "", s, flags=re.S)
    s = s.replace('<link rel="stylesheet" href="/fonts/fonts.css">',
                  '<link rel="stylesheet" href="/fonts/fonts.css">\n' + head_block(cfg, s), 1)
    if ".visually-hidden{" not in s:
        s = s.replace("<style>\n", "<style>\n" + HIDDEN_CSS + "\n", 1)
    s = re.sub(r'<h1>(?:<span class="visually-hidden">.*?</span>)?',
               f'<h1><span class="visually-hidden">{html.escape(cfg["h1_prefix"])}</span>', s, count=1)
    s = s.replace('<h2 id="logTitle"></h2>', '<p class="log-title" id="logTitle"></p>')
    s = s.replace(".log h2{", ".log .log-title{")
    path.write_text(s, encoding="utf-8")
    print("updated", path.relative_to(ROOT))


for name, cfg in CONFIG.items():
    process(ROOT / "designs" / f"{name}.html", cfg)
