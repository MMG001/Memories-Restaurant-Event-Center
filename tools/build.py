#!/usr/bin/env python3
"""Static site builder for Memoire's Restaurant & Event Center.

    python3 tools/build.py

Reads every business fact from data/site.json (single source of truth), writes
one folder per page (clean URLs with a trailing slash), sitemap.xml, robots.txt,
_redirects and _headers, then runs the build-time QA checks. The build exits
non-zero if any check fails. Cloudflare Pages serves the output as-is.
"""
import hashlib, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
B = D["business"]
SITE = D["site_url"].rstrip("/")
NAME = B["name"]
SHORT = B["short_name"]
PHONE = B["phone_display"]
TEL = "tel:" + B["phone_e164"]
ADDR1 = B["street"]
ADDR2 = f'{B["city"]}, {B["region"]} {B["postal"]}'
UPDATED = D["updated"]
UPDATED_TXT = D["updated_display"]
M = D["menus"]
GO = D["grand_opening"]

e = lambda s: html.escape(s, quote=True)
amp = lambda s: s.replace("&", "&amp;")


def money(p):
    return "$" + p


# ---------------------------------------------------------------- assets
def _hash(rel):
    p = ROOT / rel.lstrip("/")
    return hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.exists() else "0"


def A(rel):
    """Asset URL with content hash for long caching."""
    rel = "/" + rel.lstrip("/")
    return f"{rel}?v={_hash(rel)}"


def img(name, alt, cls="", lazy=True, sizes="(max-width: 860px) 100vw, 50vw", w=1600, h=900):
    big = f"assets/img/{name}.webp"
    small = f"assets/img/{name}-800.webp"
    srcset = f'{A(small)} 800w, {A(big)} 1600w' if (ROOT / small).exists() else ""
    ss = f' srcset="{srcset}" sizes="{sizes}"' if srcset else ""
    ld = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{A(big)}"{ss} alt="{e(alt)}" width="{w}" height="{h}"{ld}{c}>'


# ---------------------------------------------------------------- navigation (client-specified)
NAV = [
    ("Home", "/", [("Grand Opening", "/events/grand-opening/")]),
    ("About", "/about/", []),
    ("Menu", "/menu/", [("Lunch", "/menu/lunch/"), ("Dinner", "/menu/dinner/")]),
    ("Events", "/events/", [("Brunch Vibez", "/events/brunch-vibez/"), ("Taco Tuesday", "/events/taco-tuesday/"),
                            ("Soulfull Sundays", "/events/soulfull-sunday/")]),
    ("Gallery", "/gallery/", []),
    ("Event Center", "/event-center/", [("Rental", "/event-center/rental/")]),
    ("Contact", "/contact/", [("FAQ", "/faq/")]),
]


def nav_html(path):
    out = []
    for label, href, subs in NAV:
        active = path == href or (href != "/" and path.startswith(href))
        cur = ' aria-current="page"' if path == href else ""
        cls = ' class="top is-active"' if active else ' class="top"'
        if subs:
            sub = "".join(f'<li><a href="{h}"' + (' aria-current="page"' if path == h else "") + f'>{l}</a></li>' for l, h in subs)
            out.append(f'<li class="has-sub"><a href="{href}"{cur}{cls}>{label}<span class="caret" aria-hidden="true"></span></a>'
                       f'<button type="button" class="sub-toggle" aria-label="Show {label} links" aria-expanded="false"></button>'
                       f'<ul class="sub">{sub}</ul></li>')
        else:
            out.append(f'<li><a href="{href}"{cur}{cls}>{label}</a></li>')
    return "".join(out)


# ---------------------------------------------------------------- schema helpers
BIZ_ID = SITE + "/#business"
WEB_ID = SITE + "/#website"


def business_node():
    hrs = []
    for h in D["hours"]:
        if h["days"]:
            hrs.append({"@type": "OpeningHoursSpecification", "dayOfWeek": h["days"], "opens": h["opens"], "closes": h["closes"]})
    node = {
        "@type": ["Restaurant", "EventVenue"],
        "@id": BIZ_ID,
        "name": NAME,
        "url": SITE + "/",
        "telephone": B["phone_e164"],
        "image": SITE + "/assets/img/og-memoires-exterior-storefront-n-44th-ave.jpg",
        "logo": SITE + "/assets/img/logo-light-600.png",
        "address": {"@type": "PostalAddress", "streetAddress": ADDR1, "addressLocality": B["city"],
                    "addressRegion": B["region"], "postalCode": B["postal"], "addressCountry": B["country"]},
        "geo": {"@type": "GeoCoordinates", "latitude": B["geo"]["lat"], "longitude": B["geo"]["lng"]},
        "hasMap": B["directions"],
        "openingHoursSpecification": hrs,
        "servesCuisine": B["cuisine"],
        "acceptsReservations": True,
        "hasMenu": SITE + "/menu/",
        "areaServed": [{"@type": "City", "name": B["city"], "sameAs": B["wikidata_city"]},
                       {"@type": "State", "name": B["region_name"]}],
        "knowsAbout": ["Soul food", "Birria", "Brunch", "Private event hosting", "Event catering"],
        "potentialAction": [
            {"@type": "ReserveAction", "target": {"@type": "EntryPoint", "urlTemplate": TEL}},
            {"@type": "CommunicateAction", "name": "Event center rental request",
             "target": {"@type": "EntryPoint", "urlTemplate": SITE + "/event-center/rental/"}},
        ],
    }
    if B["same_as"]:
        node["sameAs"] = B["same_as"]
    return node


def website_node():
    return {"@type": "WebSite", "@id": WEB_ID, "url": SITE + "/", "name": NAME, "publisher": {"@id": BIZ_ID}, "inLanguage": "en-US"}


def menu_section(name, items):
    return {"@type": "MenuSection", "name": name, "hasMenuItem": [
        {"@type": "MenuItem", "name": i["name"].replace("*", ""), **({"description": i["desc"]} if i.get("desc") else {}),
         "offers": {"@type": "Offer", "price": i["price"], "priceCurrency": "USD"}} for i in items]}


def weekly_event(name, url, day, start, end, desc, image):
    sched = {"@type": "Schedule", "byDay": "https://schema.org/" + day, "repeatFrequency": "P1W",
             "scheduleTimezone": "America/Chicago"}
    if start:
        sched["startTime"] = start
    if end:
        sched["endTime"] = end
    return {"@type": "Event", "@id": url + "#event", "name": name, "url": url, "description": desc,
            "eventSchedule": sched, "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled", "location": {"@id": BIZ_ID},
            "organizer": {"@id": BIZ_ID}, "image": image}


# ---------------------------------------------------------------- page registry
PAGES = {}
CARD_LINKS = []


def crumbs_html(crumbs):
    parts = []
    for i, (label, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            parts.append(f'<li aria-current="page">{label}</li>')
        else:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(parts)}</ol></nav>'


def page(path, *, title, desc, h1, body, og, og_alt, crumbs=None, ptype="WebPage", extra_nodes=None,
         og_type="website", hero_html=None, banner_img=None, lead="", end_html="", indexable=True):
    canonical = SITE + path
    og_url = SITE + "/assets/img/" + og
    graph = [business_node(), website_node()]
    wp = {"@type": ptype, "@id": canonical + "#webpage", "url": canonical, "name": title, "description": desc,
          "isPartOf": {"@id": WEB_ID}, "about": {"@id": BIZ_ID}, "inLanguage": "en-US", "dateModified": UPDATED,
          "primaryImageOfPage": {"@type": "ImageObject", "url": og_url, "width": 1200, "height": 630}}
    if crumbs:
        bl = {"@type": "BreadcrumbList", "@id": canonical + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": html.unescape(re.sub("<[^>]+>", "", l)), "item": SITE + h}
            for i, (l, h) in enumerate(crumbs)]}
        wp["breadcrumb"] = {"@id": bl["@id"]}
        graph.append(bl)
    graph.insert(2, wp)
    graph += extra_nodes or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    robots = "index,follow" if (D["indexable"] and indexable) else "noindex,follow"

    if hero_html is None:
        bg = banner_img or "memoires-dining-room"
        hero_html = f"""<section class="banner">
  <div class="bg">{img(bg, "", lazy=False, sizes="100vw")}</div>
  <div class="wrap">
    {crumbs_html(crumbs) if crumbs else ""}
    <h1>{h1}</h1>
    {f'<p class="lead-in">{lead}</p>' if lead else ""}
  </div>
</section>"""

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#131313">
<meta property="og:site_name" content="{e(NAME)}">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_url}">
<meta property="og:image:alt" content="{e(og_alt)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:type" content="image/jpeg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og_url}">
<link rel="icon" type="image/png" href="{A('assets/img/favicon.png')}">
<link rel="apple-touch-icon" href="{A('assets/img/favicon.png')}">
<link rel="preload" href="/assets/fonts/outfit-latin-300-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/playfair-display-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{A('assets/css/site.css')}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap head-in">
    <a class="brand" href="/" aria-label="{e(NAME)} home"><img src="{A('assets/img/logo-light.webp')}" alt="{e(NAME)} logo" width="1000" height="387"></a>
    <button class="menu-toggle" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav"><span></span></button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul>{nav_html(path)}</ul>
      <a class="btn" href="{TEL}">Reservations</a>
    </nav>
  </div>
</header>
<main id="main">
{hero_html}
{body}
</main>
{footer()}
<a class="call-bar" href="{TEL}" aria-label="Call {SHORT} for reservations at {PHONE}">Call for Reservations · {PHONE}</a>
<div class="modal" id="flyer" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Flyer"><div class="modal-box img"><button class="modal-x" type="button" aria-label="Close">×</button><img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" alt="Flyer"></div></div>
{end_html}
<script src="{A('assets/js/site.js')}" defer></script>
</body>
</html>
"""
    out = ROOT / path.lstrip("/") / "index.html" if path.endswith("/") else ROOT / path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    PAGES[path] = {"title": title, "desc": desc, "h1": re.sub("<[^>]+>", "", html.unescape(h1)), "file": out,
                   "indexable": indexable}


def footer():
    hrs = "".join(f"<li><span>{amp(h['label'])}</span><span>{amp(h['text'])}</span></li>" for h in D["hours"])
    return f"""<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <img class="foot-logo" src="{A('assets/img/logo-light.webp')}" alt="{e(NAME)} logo" width="1000" height="387" loading="lazy">
      <p>Soul food restaurant and event center in {B['neighborhood']}.</p>
      <p class="nap"><strong>{amp(NAME)}</strong><br>{ADDR1}<br>{ADDR2}<br><a href="{TEL}">{PHONE}</a></p>
    </div>
    <div>
      <h2 class="fh">Hours</h2>
      <ul class="foot-hours">{hrs}<li><span>Happy Hour</span><span>{amp(D['happy_hour'])}</span></li></ul>
    </div>
    <div>
      <h2 class="fh">Eat &amp; Drink</h2>
      <ul>
        <li><a href="/menu/">Menu</a></li>
        <li><a href="/menu/lunch/">Lunch Special</a></li>
        <li><a href="/menu/dinner/">Dinner Menu</a></li>
        <li><a href="/events/">Weekly Events</a></li>
        <li><a href="/events/brunch-vibez/">Brunch Vibez</a></li>
        <li><a href="/events/taco-tuesday/">Taco Tuesday</a></li>
        <li><a href="/events/soulfull-sunday/">Soulfull Sunday Buffet</a></li>
        <li><a href="/events/grand-opening/">Grand Opening</a></li>
      </ul>
    </div>
    <div>
      <h2 class="fh">Company</h2>
      <ul>
        <li><a href="/about/">About</a></li>
        <li><a href="/event-center/">Event Center</a></li>
        <li><a href="/event-center/rental/">Rental Request</a></li>
        <li><a href="/gallery/">Gallery</a></li>
        <li><a href="/visit/">Visit &amp; Directions</a></li>
        <li><a href="/guides/">Guides</a></li>
        <li><a href="/faq/">FAQ</a></li>
        <li><a href="/contact/">Contact</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap lower">
    <span>© 2026 {amp(NAME)}. All rights reserved. · Information updated {UPDATED_TXT}</span>
    <nav aria-label="Legal">
      <a href="/privacy-policy/">Privacy Policy</a>
      <a href="/equal-opportunity-employer/">Equal Opportunity Employer</a>
      <a href="/terms/">Terms &amp; Conditions</a>
    </nav>
  </div>
</footer>"""


# ---------------------------------------------------------------- reusable blocks
def items_html(items):
    out = []
    for i in items:
        d = f"<p>{amp(i['desc'])}</p>" if i.get("desc") else ""
        t = f'<span class="tag">{i["tag"]}</span>' if i.get("tag") else ""
        out.append(f'<div class="item"><div class="row"><h3>{amp(i["name"])}</h3><span class="dots" aria-hidden="true"></span>'
                   f'<span class="price">{money(i["price"])}</span></div>{d}{t}</div>')
    return '<div class="menu-list">' + "".join(out) + "</div>"


def opt(title, lst, extra=""):
    return f'<div class="opt"><h3>{title}</h3>{extra}<ul>' + "".join(f"<li>{amp(x)}</li>" for x in lst) + "</ul></div>"


def flyer_btn(src, alt, label):
    return f'<button type="button" class="flyer-link" data-flyer="{A("assets/img/" + src)}" data-alt="{e(alt)}">{label}</button>'


def reviewed():
    return f'<p class="reviewed">Reviewed by the {amp(SHORT)} team · Updated {UPDATED_TXT}</p>'


def kw_table(rows, caption):
    tr = ""
    for t, u, m, w in rows:
        th = f'<a href="{u}" rel="noopener">{t}</a>' if u else t
        tr += f'<tr><th scope="row">{th}</th><td>{m}</td><td>{w}</td></tr>'
    return (f'<div class="kw"><table><caption>{caption}</caption><thead><tr><th scope="col">Term</th>'
            f'<th scope="col">What it means</th><th scope="col">At {amp(SHORT)}</th></tr></thead><tbody>{tr}</tbody></table></div>')


def card(label, badge, sub, text, price, image, alt, href):
    CARD_LINKS.append((label, href))
    pr = f'<span class="price">{price}</span>' if price else "<span></span>"
    return (f'<article class="card reveal"><div class="ph">{img(image, alt, sizes="(max-width: 700px) 100vw, 25vw")}'
            f'<span class="badge">{badge}</span></div><div class="body"><span class="day">{sub}</span>'
            f'<h3><a class="cover" href="{href}">{label}</a></h3><p>{text}</p><div class="foot">{pr}'
            f'<span class="more" aria-hidden="true">Details</span></div></div></article>')


def cta(image="memoires-bar-open-kitchen", heading="Save Your Seat"):
    return f"""<section class="cta">
  <div class="bg">{img(image, "", sizes="100vw")}</div>
  <div class="wrap center reveal">
    <p class="eyebrow">Reservations</p>
    <h2>{heading}</h2>
    <a class="phone-big" href="{TEL}">{PHONE}</a>
    <p class="cta-addr">{ADDR1} · {ADDR2}</p>
  </div>
</section>"""


def related(links, heading="Often Paired Together"):
    li = "".join(f'<a class="rel" href="{h}"><span>{l}</span><small>{s}</small></a>' for l, h, s in links)
    return f'<section class="alt"><div class="wrap"><h2 class="sm-h">{heading}</h2><div class="rel-grid">{li}</div></div></section>'


def hours_table():
    rows = "".join(f"<tr><th scope=\"row\">{amp(h['label'])}</th><td>{amp(h['text'])}</td></tr>" for h in D["hours"])
    return f'<table class="hours">{rows}<tr><th scope="row">Happy Hour</th><td>{amp(D["happy_hour"])}</td></tr></table>'


def map_iframe(title):
    return (f'<div class="map"><iframe src="{B["map_embed"]}" title="{e(title)}" loading="lazy" '
            f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>')


ICON = {
    "food": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M7 2v20M4 2v6a3 3 0 0 0 6 0V2M17 2c-2 2-3 5-3 8h3v12"/></svg>',
    "music": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
    "room": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 21h18M5 21V8l7-5 7 5v13M9 21v-6h6v6"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/></svg>',
}

FAQ = [
    ("Do I need a reservation?",
     f'Reservations are recommended for any visit and required for <a href="/events/brunch-vibez/">Brunch Vibez</a> on Saturdays. Call <a href="{TEL}">{PHONE}</a> to book a table.'),
    ("Where is Memoire’s located?",
     f'We are at {ADDR1}, {ADDR2}, in {B["neighborhood"]}. See the <a href="/visit/">visit page</a> for the map and directions.'),
    ("When are lunch and dinner served?",
     'The <a href="/menu/lunch/">Lunch Special</a> runs Wednesday – Friday, 11AM – 3PM. <a href="/menu/dinner/">Dinner</a> is served Wednesday – Friday, 3:30PM – 8PM.'),
    ("What happens each week?",
     '<a href="/events/taco-tuesday/">Taco Tuesday</a> runs 11AM – 8PM, the lunch special runs midweek, <a href="/events/brunch-vibez/">Brunch Vibez</a> is every Saturday 11AM – 6PM and the <a href="/events/soulfull-sunday/">Soulfull Sunday buffet</a> is every Sunday.'),
    ("When is happy hour?", f"Happy hour is {D['happy_hour'].replace('&', 'and')}."),
    ("Do you have vegan options?",
     'Yes. <a href="/menu/dinner/">Dinner</a> has Meatless Memories and the Dirty Cabbage Skillet, <a href="/menu/lunch/">lunch</a> has a $16 vegan option, and <a href="/events/taco-tuesday/">Taco Tuesday</a> has Veggie Birria.'),
    ("What does the Sunday buffet include?",
     f'The <a href="/events/soulfull-sunday/">Soulfull Sunday</a> soul food buffet is ${M["sunday"]["price"]} and includes a drink and going through the buffet 3 times.'),
    ("Can I host a private event at Memoire’s?",
     'Yes. The <a href="/event-center/">event center</a> hosts every type of event, and we provide the food and the DJ. Send a <a href="/event-center/rental/">rental request</a> or call us.'),
    ("Do you have a kids menu?",
     'At <a href="/events/brunch-vibez/">Brunch Vibez</a>, the Kids Meal ($12) comes with 2 mini waffles or 1 pancake.'),
]


def faq_html(qs):
    return '<div class="faq">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in qs) + "</div>"


def go_rows(with_ids=False):
    out = ""
    for g in GO:
        idattr = f' id="{g["slug"]}"' if with_ids else ""
        sub = f'<p>{g["sub"]}</p>' if g["sub"] else ""
        tm = f'<span class="time">{g["time"]}</span>' if g["time"] else ""
        out += (f'<li{idattr}><div class="go-date"><small>{g["dow"]}</small><b>{g["day"]}</b><em>Nov</em></div>'
                f'<div><h3>{amp(g["title"])}</h3>{sub}{tm}</div></li>')
    return out


# ================================================================ PAGES
def home():
    cards = "".join([
        card("Taco Tuesday", "Tuesdays", "11AM – 8PM", "Beef birria tacos, quesadillas, egg rolls and birria pizza, all with consomé &amp; limes.", "From $14", "beef-birria-tacos", "Beef birria tacos with lime", "/events/taco-tuesday/"),
        card("Lunch Special", "Wed – Fri", "11AM – 3PM", "Choose a meat and sides: catfish, wings, blackened chicken or blackened salmon.", money(M["lunch"]["price"]), "mac-and-cheese-fried-chicken-plate", "Fried chicken with mac and cheese", "/menu/lunch/"),
        card("Dinner Menu", "Wed – Fri", "3:30PM – 8PM", "NY strip steaks, Cajun salmon medley, soul food plates and vegan dishes.", "From $18", "grilled-ny-strip-steak", "Grilled NY strip steak with vegetables", "/menu/dinner/"),
        card("Brunch Vibez", "Saturdays", "11AM – 6PM", "Chicken &amp; waffles, shrimp &amp; grits, steak &amp; eggs and the Boss Brunch.", "From $22", "chicken-and-waffles", "Chicken and waffles with syrup", "/events/brunch-vibez/"),
        card("Soulfull Sunday", "Sundays", "Soul Food Buffet", "Includes a drink &amp; going through the buffet 3 times.", "$" + M["sunday"]["price"], "soul-food-plate-greens-mashed-potatoes", "Soul food plate with greens and mashed potatoes", "/events/soulfull-sunday/"),
    ])
    hero = f"""<section class="hero">
  <div class="bg"><img src="{A('assets/img/memoires-exterior-storefront-n-44th-ave.webp')}" srcset="{A('assets/img/memoires-exterior-storefront-n-44th-ave-800.webp')} 800w, {A('assets/img/memoires-exterior-storefront-n-44th-ave.webp')} 1600w, {A('assets/img/memoires-exterior-storefront-n-44th-ave-1866.webp')} 1866w" sizes="100vw" alt="Memoire’s storefront on N 44th Ave in North Minneapolis" width="1866" height="843" fetchpriority="high"></div>
  <div class="wrap">
    <img class="hero-logo" src="{A('assets/img/logo-light.webp')}" alt="" width="1000" height="387">
    <h1>Soul Food Restaurant &amp; Event Center in North Minneapolis</h1>
    <p class="tag">Where every plate becomes a memory.</p>
    <div class="btn-row center-row">
      <a class="btn" href="{TEL}">Call {PHONE}</a>
      <a class="btn ghost" href="/menu/">View the Menu</a>
    </div>
    <ul class="trust">
      <li>{ADDR1}, Minneapolis</li><li>Lunch &amp; dinner Wed – Fri</li><li>Weekly brunch, tacos &amp; buffet</li><li>Event center rentals</li>
    </ul>
  </div>
</section>"""
    body = f"""
<section class="intro">
  <div class="narrow-c center reveal">
    <p class="lead big"><strong>{amp(NAME)}</strong> is a soul food restaurant and private event venue at {ADDR1} in {B['neighborhood']}, serving lunch, dinner, Saturday brunch, Taco Tuesday and a Sunday soul food buffet for diners, families and event hosts.</p>
  </div>
</section>

<section class="go alt" id="grand-opening">
  <div class="wrap">
    <div class="center reveal head-gap">
      <p class="eyebrow">You’re Invited · Nov 10 – 15</p>
      <h2>Grand Opening Week</h2>
      <p class="lead center-lead">Six days to celebrate: tacos and tequila, live music, karaoke, a 90’s party, the return of <a href="/events/brunch-vibez/">Brunch Vibez</a> and the big game. <a href="/events/grand-opening/">See the full Grand Opening schedule</a>.</p>
    </div>
    <div class="reveal">
      <ul class="go-list two">{go_rows()}</ul>
      <div class="happy wide-happy"><h3>Happy Hour</h3><p>{amp(D['happy_hour'])}</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="center reveal head-gap">
      <p class="eyebrow">Restaurant · Weekly Events · Event Center</p>
      <h2>Three Ways to Enjoy {amp(SHORT)}</h2>
    </div>
    <div class="features media reveal">
      <div class="feature"><div class="fimg">{img("soul-food-plate-fried-chicken-greens", "Fried chicken with greens, mashed potatoes and gravy", sizes="(max-width: 860px) 100vw, 33vw", w=850, h=550)}</div><div class="ico">{ICON['food']}</div><h3><a href="/menu/">The Restaurant</a></h3><p>Soul food plates, NY strip steaks and Cajun salmon. The <a href="/menu/lunch/">$17.99 lunch special</a> and <a href="/menu/dinner/">dinner</a> run Wednesday – Friday.</p></div>
      <div class="feature"><div class="fimg">{img("buffet-line-chicken-waffles", "Buffet line with fried chicken and waffles", sizes="(max-width: 860px) 100vw, 33vw", w=850, h=550)}</div><div class="ico">{ICON['music']}</div><h3><a href="/events/">Weekly Events</a></h3><p><a href="/events/taco-tuesday/">Birria on Tuesdays</a>, <a href="/events/brunch-vibez/">brunch on Saturdays</a> and a <a href="/events/soulfull-sunday/">soul food buffet on Sundays</a>.</p></div>
      <div class="feature"><div class="fimg">{img("event-candlelit-table", "Candlelit event table with glassware", sizes="(max-width: 860px) 100vw, 33vw", w=850, h=550)}</div><div class="ico">{ICON['room']}</div><h3><a href="/event-center/">The Event Center</a></h3><p>Private parties of every kind, with food from our kitchen and a DJ. <a href="/event-center/rental/">Request your date</a>.</p></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap">
    <div class="center reveal head-gap"><p class="eyebrow">Every Week</p><h2>Something to Look Forward To</h2></div>
    <div class="cards five">{cards}</div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="center reveal head-gap"><p class="eyebrow">Who We Serve</p><h2>A Table for Everyone</h2></div>
    <div class="aud reveal">
      <div><h3>Weekday lunch crowd</h3><p>A $17.99 plate with your choice of meat and sides, Wednesday to Friday. <a href="/menu/lunch/">See lunch</a>.</p></div>
      <div><h3>Date night &amp; dinner</h3><p>The Memoire’s Cut, the Boss Cut and the Salmon Medley. <a href="/menu/dinner/">See dinner</a>.</p></div>
      <div><h3>Brunch groups</h3><p>Saturday brunch from 11AM to 6PM, by reservation. <a href="/events/brunch-vibez/">Brunch Vibez</a>.</p></div>
      <div><h3>Families</h3><p>The Sunday buffet and a $12 kids meal at brunch. <a href="/events/soulfull-sunday/">Sunday buffet</a>.</p></div>
      <div><h3>Vegan diners</h3><p>Vegan stroganoff, the Dirty Cabbage Skillet and Veggie Birria. <a href="/faq/">Vegan FAQ</a>.</p></div>
      <div><h3>Event hosts</h3><p>Birthdays, repasts, showers and corporate events. <a href="/event-center/">Event center</a>.</p></div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap split">
    <div class="frame reveal">{img("memoires-main-dining-hall", "Memoire’s dining room with wood floors and pendant lights")}</div>
    <div class="reveal">
      <p class="eyebrow">Our Story</p>
      <h2>Soul Food, Served With Elegance</h2>
      <p class="lead">{amp(SHORT)} brings Southern comfort and a refined night out together on Minneapolis’ North Side: slow-cooked classics, hand-cut steaks and a room built for celebrating.</p>
      <p>Read <a href="/about/">our story</a>, browse the <a href="/gallery/">gallery</a>, or learn <a href="/guides/what-is-soul-food/">what soul food is</a>.</p>
    </div>
  </div>
</section>

<section>
  <div class="wrap split">
    <div class="reveal">
      <p class="eyebrow">Find Us</p>
      <h2>Visit {amp(SHORT)} in North Minneapolis</h2>
      <p class="nap-line"><strong>{amp(NAME)}</strong><br>{ADDR1}, {ADDR2}<br><a href="{TEL}">{PHONE}</a></p>
      {hours_table()}
      <div class="btn-row"><a class="btn ghost" href="/visit/">Map &amp; Directions</a><a class="btn ghost" href="/contact/">Contact</a></div>
    </div>
    <div class="reveal">{map_iframe("Map to Memoire’s, 2201 N 44th Ave, Minneapolis")}</div>
  </div>
</section>

<section class="alt">
  <div class="narrow-c">
    <div class="center reveal head-gap"><p class="eyebrow">FAQ</p><h2>Good to Know</h2></div>
    {faq_html(FAQ[:4])}
    <div class="btn-row center-row"><a class="btn ghost" href="/faq/">All Questions</a><a class="btn ghost" href="/guides/">Guides</a></div>
    {reviewed()}
  </div>
</section>
{cta()}"""
    pop = ""
    for g in GO:
        det = " · ".join(x for x in (g["sub"], g["time"]) if x)
        pop += f'<li><div class="d">{g["dow"]}<b>Nov {g["day"]}</b></div><div><strong>{amp(g["title"])}</strong><span>{det}</span></div></li>'
    promo = f"""<div class="modal" id="promo" aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="promo-t">
  <div class="modal-box">
    <button class="modal-x" type="button" aria-label="Close">×</button>
    <img class="pop-logo" src="{A('assets/img/logo-light.webp')}" alt="" width="1000" height="387">
    <p class="modal-h" id="promo-t">Grand Opening</p>
    <p class="sub-t">November 10 – 15</p>
    <ul class="pop-list">{pop}</ul>
    <div class="btn-row center-row"><a class="btn" href="{TEL}">Call {PHONE}</a><a class="btn ghost" href="/events/grand-opening/">See the Lineup</a></div>
  </div>
</div>"""
    page("/", title="Soul Food Restaurant, North Minneapolis | Memoire's",
         desc="Memoire's is a soul food restaurant and event center at 2201 N 44th Ave in North Minneapolis, with lunch, dinner, brunch and Taco Tuesday. Call to reserve.",
         h1="Soul Food Restaurant &amp; Event Center in North Minneapolis", body=body, hero_html=hero,
         og="og-memoires-exterior-storefront-n-44th-ave.jpg", og_alt="Memoire’s storefront in North Minneapolis",
         og_type="business.business", end_html=promo)


def about():
    body = f"""
<section>
  <div class="wrap split">
    <div class="reveal">
      <p class="lead"><strong>{amp(NAME)}</strong> is a North Minneapolis soul food restaurant and event center for diners who want a relaxed meal or a night to celebrate.</p>
      <h2>Made for Memories</h2>
      <p>Our kitchen serves <a href="/guides/what-is-soul-food/">soul food</a> classics and hand-cut steaks: fried catfish, smothered chicken, mac &amp; cheese, greens and yams, alongside the Memoire’s Cut and Boss Cut NY strips on the <a href="/menu/dinner/">dinner menu</a>.</p>
      <p>Every week brings something to look forward to: <a href="/events/taco-tuesday/">Taco Tuesday</a>, a <a href="/menu/lunch/">weekday lunch special</a>, <a href="/events/brunch-vibez/">Brunch Vibez</a> on Saturdays and our <a href="/events/soulfull-sunday/">Soulfull Sunday buffet</a>.</p>
      <p>Beyond the dining room, our <a href="/event-center/">event center</a> hosts every type of occasion, with food and a DJ provided by our team.</p>
    </div>
    <div class="frame reveal">{img("memoires-exterior-arched-entrance", "Memoire’s white brick building with arched entrance")}</div>
  </div>
</section>
<section class="alt">
  <div class="wrap">
    <h2 class="center head-gap">The {amp(SHORT)} Experience</h2>
    <div class="features reveal">
      <div class="feature"><div class="ico">{ICON['food']}</div><h3>Soulful Cooking</h3><p>Southern comfort, steaks and salmon, plus vegan dishes so everyone has a seat at the table.</p></div>
      <div class="feature"><div class="ico">{ICON['music']}</div><h3>Weekly Vibes</h3><p>Birria Tuesdays, Saturday brunch, the Sunday buffet and happy hour Tuesday through Friday.</p></div>
      <div class="feature"><div class="ico">{ICON['room']}</div><h3>Event Center</h3><p>A warm, modern room for private parties and gatherings of every kind.</p></div>
      <div class="feature"><div class="ico">{ICON['star']}</div><h3>Hospitality</h3><p>An elegant room, a friendly team and a night out that feels like home.</p></div>
    </div>
  </div>
</section>
<section>
  <div class="wrap split rev">
    <div class="frame reveal">{img("memoires-bar-open-kitchen", "Memoire’s bar and open kitchen")}</div>
    <div class="reveal">
      <h2>Our Space</h2>
      <p>Wood floors, black-and-white finishes, a full bar and big windows. See more in the <a href="/gallery/">gallery</a>, plan your trip on the <a href="/visit/">visit page</a>, or <a href="/contact/">contact us</a>.</p>
      <p>We are an <a href="/equal-opportunity-employer/">equal opportunity employer</a>.</p>
      {reviewed()}
    </div>
  </div>
</section>
{cta()}"""
    page("/about/", title="About Our North Minneapolis Restaurant | Memoire's",
         desc="Meet Memoire's Restaurant & Event Center: soul food, NY strip steaks, weekly brunch and birria nights and a private event center in North Minneapolis, MN.",
         h1="About Memoire’s, a North Minneapolis Soul Food Restaurant", crumbs=[("Home", "/"), ("About", "/about/")],
         ptype="AboutPage", body=body, banner_img="memoires-dining-room", og="og-memoires-exterior-arched-entrance.jpg",
         og_alt="Memoire’s building with arched entrance")


def menu_hub():
    cards = "".join([
        card("Lunch Special", "Wed – Fri", "11AM – 3PM", "Pick a meat and sides for a $17.99 plate, or the $16 vegan option.", money(M["lunch"]["price"]), "mac-and-cheese-fried-chicken-plate", "Fried chicken with mac and cheese", "/menu/lunch/"),
        card("Dinner Menu", "Wed – Fri", "3:30PM – 8PM", "NY strip steaks, Salmon Medley, The Memoire’s plate and vegan skillets.", "From $18", "grilled-ny-strip-steak", "Grilled NY strip steak", "/menu/dinner/"),
        card("Brunch Vibez", "Saturdays", "11AM – 6PM", "Chicken &amp; waffles, grits, steak &amp; eggs and a kids meal.", "From $12", "chicken-and-waffles", "Chicken and waffles", "/events/brunch-vibez/"),
        card("Taco Tuesday", "Tuesdays", "11AM – 8PM", "Beef birria tacos, quesadillas, egg rolls and birria pizza.", "From $14", "beef-birria-tacos", "Birria tacos", "/events/taco-tuesday/"),
        card("Soulfull Sunday", "Sundays", "Buffet", "Soul food buffet with a drink and 3 trips through the line.", "$" + M["sunday"]["price"], "soul-food-plate-greens-mashed-potatoes", "Soul food plate", "/events/soulfull-sunday/"),
    ])
    body = f"""
<section>
  <div class="wrap">
    <p class="lead center-lead reveal">The {amp(SHORT)} menu covers a midweek <a href="/menu/lunch/">lunch special</a>, a <a href="/menu/dinner/">steak and soul food dinner</a>, and weekly specials: <a href="/events/brunch-vibez/">Saturday brunch</a>, <a href="/events/taco-tuesday/">birria on Tuesdays</a> and a <a href="/events/soulfull-sunday/">Sunday buffet</a>. Choose a menu below.</p>
    <h2 class="sm-h">Choose a Menu</h2>
    <div class="cards five">{cards}</div>
    {kw_table([
        ("Soul food", "https://en.wikipedia.org/wiki/Soul_food", "Southern African American home cooking", "Catfish, greens, yams, mac &amp; cheese"),
        ("NY strip", "https://en.wikipedia.org/wiki/Strip_steak", "A tender cut from the short loin", "Memoire’s Cut (10oz), Boss Cut (12oz)"),
        ("Birria", "https://en.wikipedia.org/wiki/Birria", "Mexican braised meat served with its broth", "Taco Tuesday, with consomé &amp; limes"),
        ("Texas toast", "https://en.wikipedia.org/wiki/Texas_toast", "Thick-sliced toasted bread", "With steaks, stroganoff and brunch plates"),
    ], "Menu terms")}
    {reviewed()}
  </div>
</section>
{cta("grilled-ny-strip-steak")}"""
    nodes = [{"@type": "Menu", "@id": SITE + "/menu/#menu", "name": f"{NAME} menu", "url": SITE + "/menu/",
              "hasMenuSection": [{"@type": "MenuSection", "name": "Lunch", "url": SITE + "/menu/lunch/"},
                                 {"@type": "MenuSection", "name": "Dinner", "url": SITE + "/menu/dinner/"}]}]
    page("/menu/", title="Menu: Soul Food Lunch & Dinner, Minneapolis | Memoire's",
         desc="See the Memoire's menu in North Minneapolis: a $17.99 lunch special, steak and soul food dinner, Saturday brunch, Taco Tuesday birria and a Sunday buffet.",
         h1="Menu at Memoire’s Soul Food Restaurant in Minneapolis", crumbs=[("Home", "/"), ("Menu", "/menu/")],
         ptype="CollectionPage", body=body, banner_img="steak-fillet-plate", og="og-steak-fillet-plate.jpg",
         og_alt="Steak fillet plate", extra_nodes=nodes,
         lead="Lunch and dinner Wednesday – Friday, plus weekly brunch, tacos and a Sunday buffet.")


def lunch():
    L = M["lunch"]
    body = f"""
<section id="lunch">
  <div class="wrap">
    <div class="split reveal">
      <div>
        <p class="lead">Our $17.99 <strong>lunch special</strong> in North Minneapolis is a build-your-own plate for weekday diners who want soul food fast: pick a meat and sides, Wednesday – Friday, 11AM – 3PM.</p>
        <div class="price-hero"><span>$</span>{L['price']}</div>
        <p><span class="when">{L['when']}</span></p>
        <div class="btn-row"><a class="btn" href="{TEL}">Call {PHONE}</a><a class="btn ghost" href="/menu/dinner/">Dinner Menu</a></div>
      </div>
      <div class="frame">{img("mac-and-cheese-fried-chicken-plate", "Lunch plate of fried chicken and mac and cheese")}</div>
    </div>
    <h2 class="sm-h">Build Your Plate</h2>
    <div class="opts reveal">
      {opt("Meats", L['meats'])}
      {opt("Sides", L['sides'])}
      {opt("Vegan Option", L['vegan'], f'<div class="big">{money(L["vegan_price"])}</div>')}
    </div>
    {flyer_btn("flyer-lunch.webp", "Lunch Special flyer", "View the lunch flyer")}
    <h2 class="sm-h">How Lunch Works</h2>
    <ol class="steps"><li>Come in Wednesday – Friday between 11AM and 3PM.</li><li>Choose your meat, or the vegan option.</li><li>Pick your sides.</li><li>Stay for <a href="/faq/">happy hour</a> from 11AM – 1PM.</li></ol>
    {kw_table([
        ("Blackening", "https://en.wikipedia.org/wiki/Blackening_(cooking)", "Spice-crusted, seared in a hot pan", "Blackened Chicken, Blackened Salmon"),
        ("Red beans and rice", "https://en.wikipedia.org/wiki/Red_beans_and_rice", "Louisiana Creole classic", "A side choice"),
        ("Collard greens", "https://en.wikipedia.org/wiki/Collard_(plant)", "Slow-cooked leafy greens", "“Greens” side"),
        ("Eggplant parmesan", "https://en.wikipedia.org/wiki/Parmigiana", "Breaded eggplant with cheese and sauce", "Vegan option"),
    ], "Lunch terms")}
    {reviewed()}
  </div>
</section>
{related([("Dinner Menu", "/menu/dinner/", "Wed – Fri, 3:30PM – 8PM"), ("Taco Tuesday", "/events/taco-tuesday/", "Taco flight 11AM – 3PM"), ("What Is Soul Food?", "/guides/what-is-soul-food/", "Guide")])}
{cta("mac-and-cheese-fried-chicken-plate")}"""
    nodes = [{"@type": "Menu", "@id": SITE + "/menu/lunch/#menu", "name": "Lunch Special", "url": SITE + "/menu/lunch/",
              "hasMenuSection": [
                  {"@type": "MenuSection", "name": "Lunch Special plate", "description": "Choose a meat and sides. Meats: " + ", ".join(L["meats"]) + ". Sides: " + ", ".join(L["sides"]) + ".",
                   "hasMenuItem": [{"@type": "MenuItem", "name": "Lunch Special", "offers": {"@type": "Offer", "price": L["price"], "priceCurrency": "USD"}}]},
                  {"@type": "MenuSection", "name": "Vegan Option", "hasMenuItem": [
                      {"@type": "MenuItem", "name": v, "suitableForDiet": "https://schema.org/VeganDiet",
                       "offers": {"@type": "Offer", "price": L["vegan_price"], "priceCurrency": "USD"}} for v in L["vegan"]]}]}]
    page("/menu/lunch/", title="Lunch Special $17.99, North Minneapolis | Memoire's",
         desc="Memoire's $17.99 lunch special in North Minneapolis, Wed–Fri 11AM–3PM: catfish, wings or blackened chicken or salmon with two sides. The vegan plate is $16.",
         h1="Lunch Special in North Minneapolis", crumbs=[("Home", "/"), ("Menu", "/menu/"), ("Lunch", "/menu/lunch/")],
         body=body, banner_img="fried-chicken-with-rice", og="og-mac-and-cheese-fried-chicken-plate.jpg",
         og_alt="Fried chicken and mac and cheese lunch plate", extra_nodes=nodes,
         lead="Wednesday – Friday · 11AM – 3PM")


def dinner():
    Dn = M["dinner"]
    body = f"""
<section id="dinner">
  <div class="wrap">
    <p class="lead reveal">Our <strong>dinner menu</strong> in Minneapolis pairs hand-cut <a href="/guides/what-is-soul-food/">soul food</a> plates with NY strip steaks and Cajun salmon, for date nights and dinner with friends, Wednesday – Friday, 3:30PM – 8PM.</p>
    <div class="menu-head reveal"><h2>Dinner Plates</h2><span class="when">{Dn['when']}</span></div>
    <div class="reveal">{items_html(Dn['items'])}</div>
    <h2 class="sm-h">Choose Your Meat &amp; Sides</h2>
    <div class="opts reveal">{opt("Meats", Dn['meats'])}{opt("Sides", Dn['sides'])}</div>
    <p>Lighter midday appetite? The <a href="/menu/lunch/">lunch special</a> runs 11AM – 3PM. Planning a group dinner? Our <a href="/event-center/">event center</a> can host it.</p>
    {flyer_btn("flyer-dinner.webp", "Dinner menu flyer", "View the dinner flyer")}
    {kw_table([
        ("NY strip steak", "https://en.wikipedia.org/wiki/Strip_steak", "Short-loin cut, cooked to order", "Memoire’s Cut 10oz, Boss Cut 12oz"),
        ("Cajun seasoning", "https://en.wikipedia.org/wiki/Cajun_cuisine", "Louisiana spice blend", "Salmon Medley, Dirty Cabbage Skillet"),
        ("Stroganoff", "https://en.wikipedia.org/wiki/Beef_Stroganoff", "Creamy sauce over noodles", "Meatless Memories (vegan)"),
        ("Impossible meat", "https://en.wikipedia.org/wiki/Impossible_Foods", "Plant-based meat", "Dirty Cabbage Skillet"),
    ], "Dinner terms")}
    {reviewed()}
  </div>
</section>
{related([("Lunch Special", "/menu/lunch/", "Wed – Fri, 11AM – 3PM"), ("Brunch Vibez", "/events/brunch-vibez/", "Saturdays"), ("Private Events", "/event-center/", "Food &amp; DJ provided")])}
{cta("grilled-ny-strip-steak")}"""
    nodes = [{"@type": "Menu", "@id": SITE + "/menu/dinner/#menu", "name": "Dinner Menu", "url": SITE + "/menu/dinner/",
              "hasMenuSection": [menu_section("Dinner", Dn["items"])]}]
    page("/menu/dinner/", title="Dinner Menu: Steaks & Soul Food, Minneapolis | Memoire's",
         desc="Dinner at Memoire's in North Minneapolis, Wed–Fri 3:30–8PM: 10oz and 12oz NY strip steaks, Cajun Salmon Medley, soul food plates and vegan dishes from $18.",
         h1="Dinner Menu: Steaks &amp; Soul Food in Minneapolis", crumbs=[("Home", "/"), ("Menu", "/menu/"), ("Dinner", "/menu/dinner/")],
         body=body, banner_img="steak-fillet-plate", og="og-grilled-ny-strip-steak.jpg", og_alt="Grilled NY strip steak",
         extra_nodes=nodes, lead="Wednesday – Friday · 3:30PM – 8PM")


def events_hub():
    cards = "".join([
        card("Brunch Vibez", "Saturdays", "11AM – 6PM", "Chicken &amp; waffles, grits and steak &amp; eggs. Reservations required.", "From $12", "chicken-and-waffles", "Chicken and waffles", "/events/brunch-vibez/"),
        card("Taco Tuesday", "Tuesdays", "11AM – 8PM", "Beef birria tacos, quesadillas, egg rolls and pizza with consomé.", "From $14", "beef-birria-tacos", "Birria tacos", "/events/taco-tuesday/"),
        card("Soulfull Sunday", "Sundays", "Buffet", "A soul food buffet with a drink and 3 trips through the line.", "$" + M["sunday"]["price"], "soul-food-plate-greens-mashed-potatoes", "Soul food buffet plate", "/events/soulfull-sunday/"),
        card("Grand Opening", "Nov 10 – 15", "Six days", "Tacos &amp; tequila, live music, karaoke, a 90’s party and the big game.", "", "memoires-bar-open-kitchen", "Memoire’s bar", "/events/grand-opening/"),
    ])
    body = f"""
<section>
  <div class="wrap">
    <p class="lead center-lead reveal">Weekly events at {amp(SHORT)} in North Minneapolis give regulars a reason to come back: <a href="/events/taco-tuesday/">birria on Tuesdays</a>, <a href="/events/brunch-vibez/">brunch on Saturdays</a> and a <a href="/events/soulfull-sunday/">soul food buffet on Sundays</a>. Midweek, the <a href="/menu/lunch/">lunch special</a> and <a href="/menu/dinner/">dinner</a> keep the kitchen busy.</p>
    <h2 class="sm-h">Every Week &amp; Coming Up</h2>
    <div class="cards four">{cards}</div>
    <div class="happy reveal"><h2 class="h3">Happy Hour</h2><p>{amp(D['happy_hour'])}</p></div>
    {kw_table([
        ("Brunch", "https://en.wikipedia.org/wiki/Brunch", "Late-morning meal combining breakfast and lunch", "Brunch Vibez, Saturdays"),
        ("Birria", "https://en.wikipedia.org/wiki/Birria", "Braised meat from Jalisco, Mexico", "Taco Tuesday"),
        ("Buffet", "https://en.wikipedia.org/wiki/Buffet", "Self-serve spread of dishes", "Soulfull Sunday"),
        ("Happy hour", "https://en.wikipedia.org/wiki/Happy_hour", "Discounted drink hours", "Tue – Fri"),
    ], "Event terms")}
    {reviewed()}
  </div>
</section>
{related([("Event Center", "/event-center/", "Host a private party"), ("Menu", "/menu/", "Lunch &amp; dinner"), ("FAQ", "/faq/", "Reservations &amp; hours")], "Also at Memoire’s")}
{cta("chicken-and-waffles")}"""
    page("/events/", title="Weekly Events & Specials, Minneapolis | Memoire's",
         desc="Weekly events at Memoire's in North Minneapolis: Taco Tuesday birria, Brunch Vibez every Saturday, a Soulfull Sunday soul food buffet and weekday happy hour.",
         h1="Weekly Events &amp; Specials in North Minneapolis", crumbs=[("Home", "/"), ("Events", "/events/")],
         ptype="CollectionPage", body=body, banner_img="chicken-and-waffles", og="og-chicken-and-waffles.jpg",
         og_alt="Chicken and waffles", lead="Tacos on Tuesday, brunch on Saturday, buffet on Sunday.")


def brunch():
    Br = M["brunch"]
    body = f"""
<section id="brunch-vibez">
  <div class="wrap">
    <div class="split reveal">
      <div>
        <p class="lead"><strong>Brunch Vibez</strong> is {amp(SHORT)}’s Saturday brunch in North Minneapolis for friends, birthday groups and families: chicken &amp; waffles, grits and steak &amp; eggs, 11AM – 6PM. Powered by JS Promotions.</p>
        <p><span class="when">{Br['when']}</span></p>
        <p class="must">Reservations required · <a href="{TEL}">{PHONE}</a></p>
      </div>
      <div><img class="logo-card" src="{A('assets/img/brunch-vibez-logo-red.webp')}" alt="Brunch Vibez logo" width="1200" height="800" loading="lazy"></div>
    </div>
    <div class="menu-head reveal"><h2>Brunch Menu Highlights</h2></div>
    <div class="reveal">{items_html(Br['items'])}</div>
    <p class="note">* Consuming raw or undercooked meats, poultry, seafood, shellfish or eggs may increase your risk of foodborne illness.</p>
    {flyer_btn("flyer-brunch-vibez.webp", "Brunch Vibez flyer", "View the Brunch Vibez flyer")}
    <h2 class="sm-h">How to Book Brunch</h2>
    <ol class="steps"><li>Call <a href="{TEL}">{PHONE}</a> to reserve. Brunch is by reservation only.</li><li>Arrive any time from 11AM to 6PM on Saturday.</li><li>Big group or birthday? Ask about the <a href="/event-center/">event center</a> or send a <a href="/event-center/rental/">rental request</a>.</li></ol>
    {kw_table([
        ("Chicken and waffles", "https://en.wikipedia.org/wiki/Chicken_and_waffles", "Fried chicken served on a waffle", "Chicken &amp; Waffle, $22"),
        ("Shrimp and grits", "https://en.wikipedia.org/wiki/Shrimp_and_grits", "Lowcountry shrimp over ground corn", "Shrimp &amp; Grits, $26"),
        ("Grits", "https://en.wikipedia.org/wiki/Grits", "Porridge of ground corn", "Catfish, shrimp, Boss Brunch, Deep Fried Grits"),
        ("French toast", "https://en.wikipedia.org/wiki/French_toast", "Egg-dipped, griddled bread", "French Toast &amp; Flats, $24"),
    ], "Brunch terms")}
    {reviewed()}
  </div>
</section>
{related([("Soulfull Sunday", "/events/soulfull-sunday/", "Sunday buffet"), ("Taco Tuesday", "/events/taco-tuesday/", "Birria all day"), ("Dinner Menu", "/menu/dinner/", "Wed – Fri")])}
{cta("chicken-and-waffles")}"""
    nodes = [weekly_event("Brunch Vibez", SITE + "/events/brunch-vibez/", "Saturday", "11:00", "18:00",
                          "Saturday brunch at Memoire's, powered by JS Promotions. Reservations required.",
                          SITE + "/assets/img/og-brunch-vibez.jpg"),
             {"@type": "Menu", "@id": SITE + "/events/brunch-vibez/#menu", "name": "Brunch Vibez menu",
              "hasMenuSection": [menu_section("Brunch", Br["items"])]}]
    page("/events/brunch-vibez/", title="Brunch Vibez Saturday Brunch, Minneapolis | Memoire's",
         desc="Brunch Vibez at Memoire's, North Minneapolis: Saturdays 11AM–6PM with chicken & waffles, shrimp & grits, steak & eggs and a $12 kids meal. Reserve ahead.",
         h1="Brunch Vibez: Saturday Brunch in Minneapolis", crumbs=[("Home", "/"), ("Events", "/events/"), ("Brunch Vibez", "/events/brunch-vibez/")],
         body=body, banner_img="chicken-and-waffles", og="og-brunch-vibez.jpg", og_alt="Brunch Vibez logo",
         extra_nodes=nodes, lead="Every Saturday · 11AM – 6PM · Reservations required")


def taco():
    T = M["taco"]
    body = f"""
<section id="taco-tuesday">
  <div class="wrap">
    <div class="split reveal">
      <div>
        <p class="lead"><strong>Taco Tuesday</strong> at {amp(SHORT)} is all-day birria in North Minneapolis for taco fans and the lunch crowd: tacos, quesadillas, egg rolls and birria pizza, each with consomé for dipping, 11AM – 8PM.</p>
        <p><span class="when">{T['when']}</span></p>
        <p>New to birria? Read <a href="/guides/what-is-birria/">what birria and consomé are</a>. Stop by for <a href="/faq/">happy hour</a> too, 11AM – 1PM and 6PM – 8PM.</p>
      </div>
      <div class="frame">{img("beef-birria-tacos", "Two beef birria tacos with lime")}</div>
    </div>
    <h2 class="sm-h">Birria Menu</h2>
    <div class="reveal">{items_html(T['items'])}</div>
    <div class="opts reveal">
      <div class="opt"><h3>Taco Flight</h3><div class="big">{money(T['flight']['price'])}</div><ul><li>{T['flight']['detail'].capitalize()}</li><li>{T['flight']['when']}</li></ul></div>
      <div class="opt"><h3>Snack Pack</h3><div class="big">{money(T['snack']['price'])}</div><ul><li>{amp(T['snack']['detail'].capitalize())}</li></ul></div>
      {opt("Meat Options", T['meats'])}
    </div>
    {flyer_btn("flyer-taco-tuesday.webp", "Taco Tuesday flyer", "View the Taco Tuesday flyer")}
    {kw_table([
        ("Birria", "https://en.wikipedia.org/wiki/Birria", "Braised, chile-spiced meat from Jalisco", "3 Beef Birrias, $14"),
        ("Consomé", "https://en.wikipedia.org/wiki/Consomm%C3%A9", "The rich braising broth, for dipping", "Served with every birria item"),
        ("Quesadilla", "https://en.wikipedia.org/wiki/Quesadilla", "Tortilla folded around melted cheese", "Birria Quesadilla, $15"),
        ("Egg roll", "https://en.wikipedia.org/wiki/Egg_roll", "Fried wrapper with a savory filling", "Birria Egg Rolls, $15"),
    ], "Taco Tuesday terms")}
    {reviewed()}
  </div>
</section>
{related([("Lunch Special", "/menu/lunch/", "Wed – Fri"), ("Brunch Vibez", "/events/brunch-vibez/", "Saturdays"), ("What Is Birria?", "/guides/what-is-birria/", "Guide")])}
{cta("beef-birria-tacos")}"""
    nodes = [weekly_event("Taco Tuesday", SITE + "/events/taco-tuesday/", "Tuesday", "11:00", "20:00",
                          "All-day birria at Memoire's: tacos, quesadillas, egg rolls and birria pizza with consomé.",
                          SITE + "/assets/img/og-beef-birria-tacos.jpg"),
             {"@type": "Menu", "@id": SITE + "/events/taco-tuesday/#menu", "name": "Taco Tuesday menu",
              "hasMenuSection": [menu_section("Birria", T["items"] + [
                  {"name": "Taco Flight (4 tacos, 11AM – 3PM)", "price": T["flight"]["price"], "desc": ""},
                  {"name": "Snack Pack (3 tacos & 2 egg rolls)", "price": T["snack"]["price"], "desc": ""}])]}]
    page("/events/taco-tuesday/", title="Taco Tuesday Birria, North Minneapolis | Memoire's",
         desc="Taco Tuesday at Memoire's, North Minneapolis, 11AM–8PM: beef birria tacos with consomé, quesadillas, egg rolls and birria pizza. Taco flight $15 until 3PM.",
         h1="Taco Tuesday Birria in North Minneapolis", crumbs=[("Home", "/"), ("Events", "/events/"), ("Taco Tuesday", "/events/taco-tuesday/")],
         body=body, banner_img="shredded-beef-tacos", og="og-beef-birria-tacos.jpg", og_alt="Beef birria tacos with lime",
         extra_nodes=nodes, lead="Every Tuesday · 11AM – 8PM")


def sunday():
    S = M["sunday"]
    body = f"""
<section id="soulfull-sunday">
  <div class="wrap">
    <div class="split reveal">
      <div>
        <p class="lead"><strong>Soulfull Sunday</strong> is a ${S['price']} soul food buffet in Minneapolis for families and after-church groups, with roast, smothered and fried chicken, catfish, classic sides and dessert.</p>
        <div class="price-hero"><span>$</span>{S['price']}</div>
        <p>{S['includes']}</p>
        <p class="must">Every Sunday · Call <a href="{TEL}">{PHONE}</a> for buffet hours</p>
        <p>Craving these dishes midweek? Try the <a href="/menu/lunch/">lunch special</a> or <a href="/menu/dinner/">dinner</a>. Hosting a family gathering? See the <a href="/event-center/">event center</a>.</p>
      </div>
      <div class="frame">{img("soul-food-plate-greens-mashed-potatoes", "Soul food plate with fried chicken, greens and mashed potatoes")}</div>
    </div>
    <h2 class="sm-h">On the Buffet</h2>
    <div class="opts reveal">{opt("Meats", S['meats'])}{opt("Sides", S['sides'])}{opt("Desserts", S['desserts'])}</div>
    <p class="note">{S['drinks_note']}</p>
    {flyer_btn("flyer-soulfull-sunday.webp", "Soulfull Sunday flyer", "View the Soulfull Sunday flyer")}
    {kw_table([
        ("Soul food", "https://en.wikipedia.org/wiki/Soul_food", "African American Southern cooking", "The whole buffet"),
        ("Smothered chicken", "https://en.wikipedia.org/wiki/Smothered_chicken", "Chicken braised in gravy", "Buffet meat"),
        ("Black-eyed peas", "https://en.wikipedia.org/wiki/Black-eyed_pea", "Southern legume, slow-simmered", "Buffet side"),
        ("Banana pudding", "https://en.wikipedia.org/wiki/Banana_pudding", "Layered custard, bananas and wafers", "Dessert"),
    ], "Buffet terms")}
    {reviewed()}
  </div>
</section>
{related([("Brunch Vibez", "/events/brunch-vibez/", "Saturdays"), ("Event Center", "/event-center/", "Host your gathering"), ("What Is Soul Food?", "/guides/what-is-soul-food/", "Guide")])}
{cta("fried-chicken-cornbread")}"""
    nodes = [weekly_event("Soulfull Sunday Soul Food Buffet", SITE + "/events/soulfull-sunday/", "Sunday", "", "",
                          "Soul food buffet. " + S["includes"], SITE + "/assets/img/og-soul-food-plate-greens-mashed-potatoes.jpg")]
    nodes[0]["offers"] = {"@type": "Offer", "price": S["price"], "priceCurrency": "USD", "url": SITE + "/events/soulfull-sunday/"}
    page("/events/soulfull-sunday/", title="Sunday Soul Food Buffet, Minneapolis | Memoire's",
         desc="Soulfull Sunday at Memoire's in North Minneapolis: a $37.99 soul food buffet with fried and smothered chicken, catfish, sides, dessert and a drink. Call us.",
         h1="Soulfull Sunday Soul Food Buffet in Minneapolis", crumbs=[("Home", "/"), ("Events", "/events/"), ("Soulfull Sunday", "/events/soulfull-sunday/")],
         body=body, banner_img="fried-chicken-cornbread", og="og-soul-food-plate-greens-mashed-potatoes.jpg",
         og_alt="Soul food plate", extra_nodes=nodes, lead="Every Sunday · $" + S["price"] + " · Drink included")


def grand_opening():
    body = f"""
<section class="go">
  <div class="wrap">
    <p class="lead center-lead reveal">The <strong>{amp(SHORT)} Grand Opening</strong> runs November 10 – 15, 2026 at {ADDR1} in North Minneapolis: six days of food, music and the game for neighbors and first-time guests. Reserve at <a href="{TEL}">{PHONE}</a>.</p>
    <div class="go-grid">
      <div class="reveal">
        <h2 class="sm-h">Opening Week Schedule</h2>
        <ul class="go-list">{go_rows(True)}</ul>
        <div class="happy"><h2 class="h3">Happy Hour</h2><p>{amp(D['happy_hour'])}</p></div>
        <p>Saturday marks the return of <a href="/events/brunch-vibez/">Brunch Vibez</a>. Tuesday kicks off with <a href="/events/taco-tuesday/">birria and tequila</a>. Hungry midweek? See <a href="/menu/lunch/">lunch</a> and <a href="/menu/dinner/">dinner</a>.</p>
        {reviewed()}
      </div>
      <div class="go-side reveal">
        <img class="go-photo" src="{A('assets/img/memoires-dining-room-windows.webp')}" alt="Memoire’s dining room with black chairs, pendant lights and big windows" width="750" height="850" loading="lazy" decoding="async">
      </div>
    </div>
  </div>
</section>
{related([("Weekly Events", "/events/", "After opening week"), ("Event Center", "/event-center/", "Book a party"), ("Visit", "/visit/", "Map &amp; directions")], "Plan Your Visit")}
{cta()}"""
    nodes = []
    for g in GO:
        ev = {"@type": "Event", "@id": SITE + "/events/grand-opening/#" + g["slug"], "name": g["title"] + " – Memoire's Grand Opening",
              "startDate": g["start"], "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
              "eventStatus": "https://schema.org/EventScheduled", "location": {"@id": BIZ_ID}, "organizer": {"@id": BIZ_ID},
              "url": SITE + "/events/grand-opening/#" + g["slug"], "image": SITE + "/assets/img/og-grand-opening.jpg"}
        if g["end"]:
            ev["endDate"] = g["end"]
        if g["sub"]:
            ev["description"] = g["sub"]
        nodes.append(ev)
    page("/events/grand-opening/", title="Grand Opening Week Nov 10–15, Minneapolis | Memoire's",
         desc="Memoire's Grand Opening, Nov 10–15, 2026, North Minneapolis: Tacos & Tequila, live music, Jeopardy karaoke, a 90's party, Brunch Vibez and Vikings vs Packers.",
         h1="Grand Opening Week in North Minneapolis, Nov 10 – 15", crumbs=[("Home", "/"), ("Events", "/events/"), ("Grand Opening", "/events/grand-opening/")],
         body=body, banner_img="memoires-bar-open-kitchen", og="og-grand-opening.jpg", og_alt="Memoire’s Grand Opening flyer",
         extra_nodes=nodes, lead="November 10 – 15, 2026")


def event_center():
    tags = "".join(f"<li>{amp(t)}</li>" for t in D["event_types"])
    body = f"""
<section>
  <div class="wrap split">
    <div class="reveal">
      <p class="lead">The <strong>{amp(SHORT)} event center</strong> is a private party venue in North Minneapolis for hosts planning birthdays, receptions, repasts and corporate events, with food from our kitchen and a DJ provided.</p>
      <div class="btn-row"><a class="btn" href="/event-center/rental/">Request a Rental</a><a class="btn ghost" href="{TEL}">Call {PHONE}</a></div>
    </div>
    <div class="frame reveal">{img("memoires-event-space-windows", "Event space with tall windows and dining tables")}</div>
  </div>
</section>
<section class="alt">
  <div class="wrap">
    <h2 class="center head-gap">What We Provide</h2>
    <div class="features reveal">
      <div class="feature"><div class="ico">{ICON['food']}</div><h3>Food</h3><p>Catering from the {amp(SHORT)} kitchen, drawing on our <a href="/menu/">menu</a> of soul food, steaks, salmon and vegan dishes.</p></div>
      <div class="feature"><div class="ico">{ICON['music']}</div><h3>DJ</h3><p>A DJ to set the mood, from dinner music to a full dance floor.</p></div>
      <div class="feature"><div class="ico">{ICON['room']}</div><h3>The Space</h3><p>A modern room with a full bar and warm lighting. See the <a href="/gallery/">gallery</a>.</p></div>
      <div class="feature"><div class="ico">{ICON['star']}</div><h3>Our Team</h3><p>Staff to help you plan and host. Start with our <a href="/guides/planning-a-private-event/">event planning checklist</a>.</p></div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <h2 class="center">Every Type of Event</h2>
    <ul class="tags reveal">{tags}</ul>
    <h2 class="sm-h">How Booking Works</h2>
    <ol class="steps"><li>Send a <a href="/event-center/rental/">rental request</a> with your date, guest count and services.</li><li>Our team contacts you with availability and pricing.</li><li>Plan your menu and music with us.</li><li>Celebrate. We handle the food and the DJ.</li></ol>
    <p>Pricing depends on your date, the number of guests, the menu and the services you choose. Ask us for a quote.</p>
    {kw_table([
        ("Repast", "https://en.wiktionary.org/wiki/repast", "A meal shared after a funeral", "Celebrations of life"),
        ("Catering", "https://en.wikipedia.org/wiki/Catering", "Food prepared for an event", "From our kitchen"),
        ("Disc jockey", "https://en.wikipedia.org/wiki/Disc_jockey", "Plays recorded music for guests", "Provided"),
        ("Party", "https://en.wikipedia.org/wiki/Party", "A social gathering of invited guests", "Every type of event"),
    ], "Event center terms")}
    {reviewed()}
  </div>
</section>
{related([("Rental Request", "/event-center/rental/", "Pick your date"), ("Brunch Vibez", "/events/brunch-vibez/", "Birthday brunches"), ("FAQ", "/faq/", "Common questions")])}
{cta("memoires-main-dining-hall", "Book Your Event")}"""
    svc = {"@type": "Service", "@id": SITE + "/event-center/#service", "name": "Private event venue rental",
           "serviceType": "Event venue rental with catering and DJ", "provider": {"@id": BIZ_ID},
           "areaServed": {"@type": "City", "name": B["city"], "sameAs": B["wikidata_city"]},
           "audience": {"@type": "Audience", "audienceType": "Hosts of birthdays, receptions, repasts and corporate events"},
           "url": SITE + "/event-center/"}
    page("/event-center/", title="Event Venue & Private Parties, Minneapolis | Memoire's",
         desc="Host your event at Memoire's event center in North Minneapolis: birthdays, receptions, repasts and corporate parties, food and DJ provided. Request a date.",
         h1="Event Center &amp; Private Party Venue in North Minneapolis", crumbs=[("Home", "/"), ("Event Center", "/event-center/")],
         body=body, banner_img="memoires-main-dining-hall", og="og-memoires-event-space-windows.jpg",
         og_alt="Memoire’s event space", extra_nodes=[svc], lead="Every type of event. Food and DJ provided.")


def rental():
    ev_opts = "".join(f"<option>{e(t)}</option>" for t in D["event_types"]) + "<option>Other</option>"
    body = f"""
<section id="rental">
  <div class="narrow-c">
    <p class="lead reveal">Use this <strong>event center rental request</strong> to check dates at {amp(SHORT)} in North Minneapolis. It’s for anyone planning a party, reception, repast or business event. We reply with availability and pricing. Prefer the phone? Call <a href="{TEL}">{PHONE}</a>.</p>
    <form class="form reveal" data-inquiry="Event Center Rental Request" novalidate>
      <div class="hp" aria-hidden="true"><label for="r-web">Website</label><input id="r-web" type="text" name="website" tabindex="-1" autocomplete="off"></div>
      <div class="grid2">
        <div><label for="r-name">Full Name <span class="req">*</span></label><input id="r-name" name="Name" required autocomplete="name"></div>
        <div><label for="r-phone">Phone <span class="req">*</span></label><input id="r-phone" name="Phone" type="tel" required autocomplete="tel"></div>
        <div class="full"><label for="r-email">Email <span class="req">*</span></label><input id="r-email" name="Email" type="email" required autocomplete="email"></div>
        <div><label for="r-type">Event Type <span class="req">*</span></label><select id="r-type" name="Event Type" required><option value="">Select…</option>{ev_opts}</select></div>
        <div><label for="r-date">Event Date <span class="req">*</span></label><input id="r-date" name="Event Date" type="date" required></div>
        <div><label for="r-start">Start Time</label><input id="r-start" name="Start Time" type="time"></div>
        <div><label for="r-end">End Time</label><input id="r-end" name="End Time" type="time"></div>
        <div><label for="r-guests">Number of Guests <span class="req">*</span></label><input id="r-guests" name="Guests" type="number" min="1" required></div>
        <div><label for="r-budget">Estimated Budget</label><select id="r-budget" name="Budget"><option value="">Select…</option><option>Under $1,000</option><option>$1,000 – $2,500</option><option>$2,500 – $5,000</option><option>$5,000+</option></select></div>
        <fieldset class="full"><legend class="lg">Services Needed</legend>
          <div class="checks">
            <label for="s-food"><input id="s-food" type="checkbox" name="Services" value="Food / Catering" checked> Food / Catering</label>
            <label for="s-dj"><input id="s-dj" type="checkbox" name="Services" value="DJ" checked> DJ</label>
            <label for="s-bar"><input id="s-bar" type="checkbox" name="Services" value="Bar Service"> Bar Service</label>
            <label for="s-decor"><input id="s-decor" type="checkbox" name="Services" value="Decor"> Decor</label>
          </div>
        </fieldset>
        <div class="full"><label for="r-msg">Tell Us About Your Event</label><textarea id="r-msg" name="Details" placeholder="Theme, menu ideas, special requests…"></textarea></div>
        <div class="full"><button class="btn wide" type="submit">Submit Rental Request</button>
          <p class="fine">By submitting, you agree to our <a href="/privacy-policy/">Privacy Policy</a>. <span class="req">*</span> Required.</p></div>
      </div>
      <div class="form-msg" role="status" aria-live="polite"></div>
    </form>
    <p>Not sure what to ask for? Read <a href="/guides/planning-a-private-event/">how to plan a private event</a>, see the <a href="/event-center/">event center</a>, or browse the <a href="/menu/">menu</a>.</p>
    {reviewed()}
  </div>
</section>
{related([("Event Center", "/event-center/", "What’s included"), ("Event Planning Guide", "/guides/planning-a-private-event/", "Checklist"), ("Contact", "/contact/", "Questions")])}"""
    page("/event-center/rental/", title="Event Center Rental Request, Minneapolis | Memoire's",
         desc="Request a date at Memoire's event center in North Minneapolis. Share your event type, date and guests, and our team replies with availability and pricing.",
         h1="Event Center Rental Request in Minneapolis", crumbs=[("Home", "/"), ("Event Center", "/event-center/"), ("Rental", "/event-center/rental/")],
         body=body, banner_img="memoires-event-space-windows", og="og-memoires-event-space-windows.jpg",
         og_alt="Memoire’s event space", lead="Food and DJ provided · Every type of event")


def gallery():
    body = f"""
<section>
  <div class="wrap">
    <p class="lead center-lead reveal">Photos of {amp(SHORT)}’s restaurant and event space in North Minneapolis, for guests choosing a spot for dinner or a party. The full gallery is coming soon. Until then, browse the <a href="/menu/">menu</a>, see the <a href="/event-center/">event center</a> or <a href="/visit/">plan your visit</a>.</p>
    <p class="center"><span class="soon">Full Gallery Coming Soon</span></p>
    <div class="gallery reveal">
      <figure class="g1">{img("memoires-exterior-storefront-n-44th-ave", "Memoire’s storefront on N 44th Ave")}<figcaption>Storefront</figcaption></figure>
      <figure class="g2">{img("memoires-bar-open-kitchen", "The bar and open kitchen")}<figcaption>The bar</figcaption></figure>
      <figure class="g3">{img("memoires-dining-room", "Dining room with black chairs")}<figcaption>Dining room</figcaption></figure>
      <figure class="g4">{img("memoires-event-space-windows", "Event space with tall windows")}<figcaption>Event space</figcaption></figure>
      <figure class="g5">{img("memoires-exterior-arched-entrance", "Arched front entrance")}<figcaption>Entrance</figcaption></figure>
    </div>
    <p>Want to see the space in person? <a href="/contact/">Contact us</a> or read <a href="/about/">about Memoire’s</a>.</p>
    {reviewed()}
  </div>
</section>
{cta()}"""
    page("/gallery/", title="Gallery: Restaurant & Event Space Photos | Memoire's",
         desc="Photos of Memoire's Restaurant & Event Center in North Minneapolis: the storefront, bar, dining room and event space. The full food and event gallery is coming.",
         h1="Gallery: Memoire’s Restaurant &amp; Event Space, Minneapolis", crumbs=[("Home", "/"), ("Gallery", "/gallery/")],
         ptype="CollectionPage", body=body, banner_img="memoires-event-space-windows", og="og-memoires-dining-room.jpg",
         og_alt="Memoire’s dining room")


def visit():
    body = f"""
<section>
  <div class="wrap split top">
    <div class="reveal">
      <p class="lead"><strong>{amp(NAME)}</strong> is at {ADDR1} in {B['neighborhood']}. This page is for first-time guests planning how to get here and when we’re open.</p>
      <h2>Address</h2>
      <p class="nap-line"><strong>{amp(NAME)}</strong><br>{ADDR1}<br>{ADDR2}<br><a href="{TEL}">{PHONE}</a></p>
      <div class="btn-row"><a class="btn" href="{B['directions']}" rel="noopener">Get Directions</a><a class="btn ghost" href="{TEL}">Call {PHONE}</a></div>
      <h2>Hours</h2>
      {hours_table()}
      <h2>Area</h2>
      <p>We serve guests across <a href="{B['wikipedia_city']}" rel="noopener">Minneapolis</a>, {B['region_name']}, from our home in {B['neighborhood']}. Planning a party? See the <a href="/event-center/">event center</a>. Coming to eat? Check <a href="/menu/lunch/">lunch</a>, <a href="/menu/dinner/">dinner</a> and <a href="/events/">this week’s events</a>. Questions? See the <a href="/faq/">FAQ</a> or <a href="/contact/">contact us</a>.</p>
      {reviewed()}
    </div>
    <div class="reveal">
      {map_iframe("Map to Memoire’s, 2201 N 44th Ave, Minneapolis")}
      <figure class="entrance">{img("memoires-exterior-arched-entrance", "Memoire’s front entrance with arched doorway")}<figcaption>Our front entrance</figcaption></figure>
    </div>
  </div>
</section>"""
    page("/visit/", title="Visit Us: 2201 N 44th Ave, Minneapolis | Memoire's",
         desc="Visit Memoire's Restaurant & Event Center at 2201 N 44th Ave, Minneapolis, MN 55412: map, directions, hours, happy hour and a photo of our front entrance.",
         h1="Visit Memoire’s at 2201 N 44th Ave, Minneapolis", crumbs=[("Home", "/"), ("Visit", "/visit/")],
         body=body, banner_img="memoires-exterior-storefront-n-44th-ave", og="og-memoires-exterior-storefront-n-44th-ave.jpg",
         og_alt="Memoire’s storefront", lead=f"{ADDR1} · {ADDR2}")


def contact():
    body = f"""
<section>
  <div class="wrap split top">
    <div class="reveal">
      <p class="lead">Contact {amp(NAME)} in North Minneapolis for reservations, questions or private events. Calling is the fastest way to book a table.</p>
      <p><a class="phone-big" href="{TEL}">{PHONE}</a></p>
      <p class="nap-line"><strong>{amp(NAME)}</strong><br>{ADDR1}<br>{ADDR2}</p>
      {hours_table()}
      <p>Planning an event? Use the <a href="/event-center/rental/">rental request form</a>. Quick answers are on the <a href="/faq/">FAQ</a>, and directions are on the <a href="/visit/">visit page</a>. Hungry now? See <a href="/menu/lunch/">lunch</a>, <a href="/menu/dinner/">dinner</a> and <a href="/events/">this week’s events</a>.</p>
      {reviewed()}
    </div>
    <div class="reveal">
      <form class="form" data-inquiry="Website Message" novalidate>
        <h2 class="h3">Send a Message</h2>
        <div class="hp" aria-hidden="true"><label for="c-web">Website</label><input id="c-web" type="text" name="website" tabindex="-1" autocomplete="off"></div>
        <div class="grid2">
          <div><label for="c-name">Name <span class="req">*</span></label><input id="c-name" name="Name" required autocomplete="name"></div>
          <div><label for="c-phone">Phone</label><input id="c-phone" name="Phone" type="tel" autocomplete="tel"></div>
          <div class="full"><label for="c-email">Email <span class="req">*</span></label><input id="c-email" name="Email" type="email" required autocomplete="email"></div>
          <div class="full"><label for="c-topic">Topic</label><select id="c-topic" name="Topic"><option>General Question</option><option>Reservation</option><option>Private Event</option><option>Feedback</option><option>Careers</option></select></div>
          <div class="full"><label for="c-msg">Message <span class="req">*</span></label><textarea id="c-msg" name="Message" required></textarea></div>
          <div class="full"><button class="btn wide" type="submit">Send Message</button><p class="fine">By sending, you agree to our <a href="/privacy-policy/">Privacy Policy</a>.</p></div>
        </div>
        <div class="form-msg" role="status" aria-live="polite"></div>
      </form>
    </div>
  </div>
</section>
<section class="flush">{map_iframe("Map to Memoire’s, 2201 N 44th Ave, Minneapolis")}</section>"""
    page("/contact/", title="Contact & Reservations, Minneapolis | Memoire's",
         desc="Contact Memoire's Restaurant & Event Center in North Minneapolis: call 612.223.3679 to reserve, send a message, or find our hours and address on the map.",
         h1="Contact &amp; Reservations at Memoire’s, Minneapolis", crumbs=[("Home", "/"), ("Contact", "/contact/")],
         ptype="ContactPage", body=body, banner_img="memoires-exterior-arched-entrance", og="og-memoires-bar-open-kitchen.jpg",
         og_alt="Memoire’s bar", og_type="business.business", lead="Reservations " + PHONE)


def faq():
    body = f"""
<section>
  <div class="narrow-c">
    <p class="lead reveal">Answers for guests visiting {amp(SHORT)} in North Minneapolis: reservations, hours, menus, vegan options and private events. Still have a question? <a href="/contact/">Contact us</a> or call <a href="{TEL}">{PHONE}</a>.</p>
    {faq_html(FAQ)}
    {reviewed()}
  </div>
</section>
{related([("Menu", "/menu/", "Lunch &amp; dinner"), ("Weekly Events", "/events/", "Tacos, brunch, buffet"), ("Event Center", "/event-center/", "Private parties")], "Explore")}"""
    fq = {"@type": "FAQPage", "@id": SITE + "/faq/#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub("<[^>]+>", "", a))}}
        for q, a in FAQ]}
    page("/faq/", title="FAQ: Reservations, Hours & Events | Memoire's",
         desc="Memoire's FAQ, North Minneapolis: reservations, lunch and dinner hours, happy hour, vegan options, the Sunday buffet, kids meals and private event rentals.",
         h1="Frequently Asked Questions About Memoire’s, Minneapolis", crumbs=[("Home", "/"), ("Contact", "/contact/"), ("FAQ", "/faq/")],
         body=body, banner_img="memoires-dining-room", og="og-memoires-main-dining-hall.jpg", og_alt="Memoire’s dining hall",
         extra_nodes=[fq])


GUIDES = [
    {"slug": "what-is-birria", "crumb": "What Is Birria?", "title": "What Is Birria? Tacos, Consomé & More | Memoire's",
     "h1": "What Is Birria? A Guide to Birria Tacos &amp; Consomé",
     "desc": "What is birria? A short guide to the Jalisco braise, its consomé and quesabirria tacos, and where to eat beef birria on Taco Tuesday in North Minneapolis.",
     "img": "beef-birria-tacos", "og": "og-beef-birria-tacos.jpg",
     "body": """<p class="lead"><strong>Birria</strong> is a Mexican dish of meat slow-braised in a chile-spiced broth, from the state of <a href="https://en.wikipedia.org/wiki/Jalisco" rel="noopener">Jalisco</a>. This guide is for diners curious about birria before ordering it on <a href="/events/taco-tuesday/">Taco Tuesday</a>.</p>
<h2>Where birria comes from</h2>
<p>Birria began in Jalisco, where it was traditionally made with goat. Beef is now common, especially in the taco-stand style that spread from Tijuana into the United States.</p>
<h2>What consomé is</h2>
<p>The braising liquid becomes <em>consomé</em>, a rich broth served on the side for dipping or sipping. At Memoire’s, every birria item comes with consomé and limes.</p>
<h2>Ways to eat it</h2>
<table class="cmp"><thead><tr><th scope="col">Style</th><th scope="col">What it is</th><th scope="col">On our menu</th></tr></thead><tbody>
<tr><td>Birria tacos</td><td>Corn tortillas with braised meat, often griddled</td><td>3 Beef Birrias, $14</td></tr>
<tr><td>Quesabirria</td><td>Birria with melted cheese in a folded tortilla</td><td>Birria Quesadilla, $15</td></tr>
<tr><td>Fusion</td><td>Birria in new formats</td><td>Birria Egg Rolls $15, Birria Pizza $24</td></tr>
<tr><td>Meat-free</td><td>Vegetables in birria style</td><td>Veggie Birria, $14</td></tr></tbody></table>
<h2>Try it in North Minneapolis</h2>
<p>Taco Tuesday runs 11AM – 8PM, with a 4-taco flight for $15 until 3PM. Pair it with the <a href="/menu/lunch/">lunch special</a> later in the week, see the <a href="/menu/">full menu</a>, or learn <a href="/guides/what-is-soul-food/">what soul food is</a>.</p>""",
     "sources": [("Birria – Wikipedia", "https://en.wikipedia.org/wiki/Birria"), ("Jalisco – Wikipedia", "https://en.wikipedia.org/wiki/Jalisco")]},
    {"slug": "what-is-soul-food", "crumb": "What Is Soul Food?", "title": "What Is Soul Food? A Short Guide | Memoire's",
     "h1": "What Is Soul Food? Classic Dishes &amp; Where to Try Them",
     "desc": "What is soul food? A short guide to the African American Southern cuisine and its classic dishes, and where to eat soul food plates and a buffet in Minneapolis.",
     "img": "soul-food-plate-greens-mashed-potatoes", "og": "og-soul-food-plate-greens-mashed-potatoes.jpg",
     "body": """<p class="lead"><strong>Soul food</strong> is the traditional cooking of African Americans, rooted in the American South. This guide is for diners who want to know the classics before sitting down for <a href="/menu/dinner/">dinner</a> or the <a href="/events/soulfull-sunday/">Sunday buffet</a>.</p>
<h2>Where the name comes from</h2>
<p>The cooking is centuries old. The term “soul food” became widely used in the 1960s, alongside “soul” music and culture.</p>
<h2>Classic dishes</h2>
<table class="cmp"><thead><tr><th scope="col">Dish</th><th scope="col">What it is</th><th scope="col">At Memoire’s</th></tr></thead><tbody>
<tr><td>Fried catfish</td><td>Cornmeal-crusted, fried fish</td><td>Lunch, dinner and Sunday buffet</td></tr>
<tr><td>Collard greens</td><td>Slow-cooked leafy greens</td><td>“Greens” side</td></tr>
<tr><td>Candied yams</td><td>Sweet potatoes baked with sugar and spice</td><td>“Yams” side</td></tr>
<tr><td>Mac and cheese</td><td>Baked macaroni and cheese</td><td>Side at lunch, dinner, buffet</td></tr>
<tr><td>Cornbread</td><td>Quick bread of cornmeal</td><td>Sunday buffet</td></tr>
<tr><td>Banana pudding</td><td>Custard, bananas and wafers</td><td>Sunday dessert</td></tr></tbody></table>
<h2>Eat soul food in North Minneapolis</h2>
<p>Try a <a href="/menu/lunch/">$17.99 lunch plate</a> Wednesday – Friday, or the <a href="/events/soulfull-sunday/">$37.99 Sunday buffet</a>. Curious about Tuesdays? Read <a href="/guides/what-is-birria/">what birria is</a>.</p>""",
     "sources": [("Soul food – Wikipedia", "https://en.wikipedia.org/wiki/Soul_food"), ("Cuisine of the Southern United States – Wikipedia", "https://en.wikipedia.org/wiki/Cuisine_of_the_Southern_United_States")]},
    {"slug": "planning-a-private-event", "crumb": "Planning a Private Event", "title": "How to Plan a Private Event: Checklist | Memoire's",
     "h1": "How to Plan a Private Event: A Simple Checklist",
     "desc": "How to plan a private event in Minneapolis: a simple checklist for date, guest count, budget, food, music and timeline, plus what to send when you book a venue.",
     "img": "memoires-event-space-windows", "og": "og-memoires-event-space-windows.jpg",
     "body": """<p class="lead">Planning a <strong>private event</strong> starts with five decisions: date, guest count, budget, food and music. This checklist is for anyone hosting a birthday, shower, repast or work event and getting ready to <a href="/event-center/rental/">request a venue</a>.</p>
<h2>1. Pick a date and a backup</h2>
<p>Popular weekends book first. Have a second date in mind when you contact a venue.</p>
<h2>2. Estimate your guest count</h2>
<p>A close number drives the food order, seating and price. Count confirmed guests plus a small buffer.</p>
<h2>3. Set a budget range</h2>
<p>Venue cost usually depends on the date, the guest count, the menu and add-ons like bar service or decor.</p>
<h2>4. Choose food and music</h2>
<p>Decide between a buffet or plated meal, and whether you want a DJ. At Memoire’s, <a href="/event-center/">food and a DJ are provided</a>, and the menu draws on our <a href="/menu/">restaurant menu</a>.</p>
<h2>5. Build a simple timeline</h2>
<table class="cmp"><thead><tr><th scope="col">When</th><th scope="col">Task</th></tr></thead><tbody>
<tr><td>6–8 weeks out</td><td>Book the venue; send invitations</td></tr>
<tr><td>3–4 weeks out</td><td>Confirm the menu and music</td></tr>
<tr><td>1 week out</td><td>Final guest count to the venue</td></tr>
<tr><td>Day of</td><td>Arrive early; enjoy your guests</td></tr></tbody></table>
<h2>What to send a venue</h2>
<p>Event type, date, start and end time, guest count, budget range and the services you need. Our <a href="/event-center/rental/">rental request form</a> asks for exactly these. Prefer brunch for a birthday? See <a href="/events/brunch-vibez/">Brunch Vibez</a>.</p>""",
     "sources": [("Event planning – Wikipedia", "https://en.wikipedia.org/wiki/Event_planning"), ("Catering – Wikipedia", "https://en.wikipedia.org/wiki/Catering")]},
]


def guides():
    cards = "".join(f'<a class="rel big" href="/guides/{g["slug"]}/"><span>{g["crumb"]}</span><small>{g["desc"].split(". ")[0]}.</small></a>'
                    for g in GUIDES)
    body = f"""
<section>
  <div class="wrap">
    <p class="lead center-lead reveal">Short guides from {amp(SHORT)} in North Minneapolis for curious diners and event hosts: what’s on the plate, and how to plan a party. Then see the <a href="/menu/">menu</a>, the <a href="/events/">weekly events</a> or the <a href="/event-center/">event center</a>.</p>
    <div class="rel-grid">{cards}</div>
    {reviewed()}
  </div>
</section>"""
    page("/guides/", title="Guides: Soul Food, Birria & Event Planning | Memoire's",
         desc="Guides from Memoire's in North Minneapolis: what soul food is, what birria and consomé are, and a simple checklist for planning a private event or party.",
         h1="Guides to Soul Food, Birria &amp; Event Planning in Minneapolis", crumbs=[("Home", "/"), ("Guides", "/guides/")],
         ptype="CollectionPage", body=body, banner_img="fried-chicken-cornbread", og="og-fried-chicken-cornbread.jpg",
         og_alt="Fried chicken with cornbread")
    for g in GUIDES:
        others = [o for o in GUIDES if o is not g]
        src = "".join(f'<li><a href="{u}" rel="noopener">{t}</a></li>' for t, u in g["sources"])
        body = f"""
<section>
  <div class="narrow-c article">
    {g['body']}
    <div class="srcs"><h2 class="h3">Sources</h2><ul>{src}</ul></div>
    <p class="reviewed">By the {amp(SHORT)} team · Updated {UPDATED_TXT}</p>
  </div>
</section>
{related([(o["crumb"], "/guides/" + o["slug"] + "/", "Guide") for o in others] + [("All Guides", "/guides/", "Guides hub")], "Related Guides")}
{cta(g['img'])}"""
        art = {"@type": "Article", "@id": SITE + f"/guides/{g['slug']}/#article", "headline": html.unescape(g["h1"]),
               "description": g["desc"], "author": {"@id": BIZ_ID}, "publisher": {"@id": BIZ_ID},
               "datePublished": UPDATED, "dateModified": UPDATED, "image": SITE + "/assets/img/" + g["og"],
               "mainEntityOfPage": {"@id": SITE + f"/guides/{g['slug']}/#webpage"},
               "citation": [u for _, u in g["sources"]]}
        page(f"/guides/{g['slug']}/", title=g["title"], desc=g["desc"], h1=g["h1"],
             crumbs=[("Home", "/"), ("Guides", "/guides/"), (g["crumb"], f"/guides/{g['slug']}/")],
             body=body, banner_img=g["img"], og=g["og"], og_alt=html.unescape(g["h1"]), og_type="article", extra_nodes=[art])


def legal(path, title, h1, desc, inner, og="og-memoires-dining-room.jpg"):
    body = f'<section><div class="narrow-c legal"><p class="updated">Last updated: {UPDATED_TXT}</p>{inner}</div></section>'
    page(path, title=title, desc=desc, h1=h1, crumbs=[("Home", "/"), (h1, path)], body=body,
         banner_img="memoires-dining-room", og=og, og_alt="Memoire’s dining room")


def legal_pages():
    legal("/privacy-policy/", "Privacy Policy | Memoire's Restaurant & Event Center", "Privacy Policy for Memoire’s, Minneapolis",
          "How Memoire's Restaurant & Event Center in Minneapolis handles information you send through this website, including the contact and event rental request forms.",
          f"""<p>{amp(NAME)} (“{amp(SHORT)},” “we,” “us”) respects your privacy. This policy explains what we collect through this website and how we use it.</p>
<h2>Information we collect</h2><p>We collect only what you choose to send: your name, phone, email and event details when you use the <a href="/contact/">contact form</a> or <a href="/event-center/rental/">rental request</a>. Our hosting provider may record basic technical data such as browser type and pages visited.</p>
<h2>How we use it</h2><ul><li>To answer questions, reservations and event inquiries.</li><li>To plan and provide the services you request.</li><li>To improve our website and guest experience.</li></ul>
<h2>Sharing</h2><p>We do not sell your personal information. We share it only with providers who help run the website or our business, or when the law requires it.</p>
<h2>Third-party services</h2><p>This site embeds Google Maps, which may collect data under Google’s own privacy policy.</p>
<h2>Your choices</h2><p>Ask us to update or delete information you sent by calling <a href="{TEL}">{PHONE}</a>. See also our <a href="/terms/">terms</a>.</p>
<h2>Contact</h2><p>{amp(NAME)}, {ADDR1}, {ADDR2} · <a href="{TEL}">{PHONE}</a> · <a href="/about/">About us</a> · <a href="/visit/">Directions</a></p>""")
    legal("/equal-opportunity-employer/", "Equal Opportunity Employer | Memoire's Minneapolis", "Equal Opportunity Employment at Memoire’s, Minneapolis",
          "Memoire's Restaurant & Event Center in Minneapolis is an equal opportunity employer. Read our commitment, our accommodation policy and how to apply to our team.",
          f"""<p>{amp(NAME)} is proud to be an Equal Opportunity Employer.</p>
<p>We provide equal employment opportunities to all employees and applicants without regard to race, color, religion, creed, sex, sexual orientation, gender identity, national origin, ancestry, age, disability, marital status, familial status, status with regard to public assistance, veteran status, genetic information or any other characteristic protected by federal, state or local law.</p>
<p>This applies to recruiting, hiring, placement, promotion, training, compensation, benefits and termination. We provide reasonable accommodations to qualified individuals with disabilities; call <a href="{TEL}">{PHONE}</a> if you need one when applying.</p>
<h2>Join our team</h2><p>Stop by {ADDR1} or <a href="/contact/">send us a message</a> with “Careers” as the topic. Learn more <a href="/about/">about us</a>, our <a href="/event-center/">event center</a>, our <a href="/menu/">menu</a> and where to <a href="/visit/">find us</a>.</p>""")
    legal("/terms/", "Terms & Conditions | Memoire's Restaurant & Event Center", "Website Terms &amp; Conditions for Memoire’s, Minneapolis",
          "Terms for using the Memoire's Restaurant & Event Center website in Minneapolis: menus and prices, reservations, rentals, food safety, alcohol and site content.",
          f"""<p>By using this website you agree to these terms.</p>
<h2>Menu, pricing &amp; events</h2><p>Menu items, prices, hours and events may change without notice and are available while supplies last. Prices do not include tax or gratuity. See the current <a href="/menu/">menu</a> and <a href="/events/">events</a>.</p>
<h2>Reservations &amp; rentals</h2><p>Reservations and <a href="/event-center/">event center</a> rentals are confirmed only after you hear back from our team. A website request does not guarantee availability.</p>
<h2>Food safety &amp; allergies</h2><p>Consuming raw or undercooked meats, poultry, seafood, shellfish or eggs may increase your risk of foodborne illness. Tell your server about allergies; we cannot guarantee any item is allergen-free.</p>
<h2>Alcohol</h2><p>Alcohol is served only to guests 21 and older with valid ID.</p>
<h2>Website content</h2><p>Logos and content on this site belong to {amp(NAME)} or are used with permission.</p>
<h2>Contact</h2><p>Call <a href="{TEL}">{PHONE}</a> or visit {ADDR1}, {ADDR2}. Read our <a href="/privacy-policy/">privacy policy</a> or <a href="/contact/">contact us</a>.</p>""")


def not_found():
    body = '<section><div class="wrap center"><p class="lead center-lead">The page you’re looking for has moved. Try the <a href="/menu/">menu</a>, <a href="/events/">events</a> or <a href="/contact/">contact</a> pages.</p><p><a class="btn" href="/">Back Home</a></p></div></section>'
    page("/404.html", title="Page Not Found | Memoire's", desc="This page could not be found on the Memoire's Restaurant & Event Center website. Visit the menu, events or contact pages to find what you need in Minneapolis.",
         h1="Page Not Found", body=body, banner_img="memoires-dining-room", og="og-memoires-dining-room.jpg",
         og_alt="Memoire’s dining room", indexable=False)


# ---------------------------------------------------------------- site files
def site_files():
    urls = [p for p, m in PAGES.items() if m["indexable"]]
    sm = "".join(f"<url><loc>{SITE}{p}</loc><lastmod>{UPDATED}</lastmod></url>" for p in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    robots = "User-agent: *\n" + ("Allow: /\n" if D["indexable"] else "Disallow:\n") + f"Sitemap: {SITE}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots)
    old = {"about": "/about/", "menu": "/menu/", "events": "/events/", "gallery": "/gallery/", "event-center": "/event-center/",
           "contact": "/contact/", "privacy-policy": "/privacy-policy/", "terms": "/terms/",
           "equal-opportunity-employer": "/equal-opportunity-employer/"}
    lines = ["/index.html / 301"] + [f"/{k}.html {v} 301" for k, v in old.items()]
    (ROOT / "_redirects").write_text("\n".join(lines) + "\n")
    headers = "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n"
    if not D["indexable"]:
        headers += "  X-Robots-Tag: noindex\n"
    (ROOT / "_headers").write_text(headers)


# ---------------------------------------------------------------- QA (Section 13)
def qa():
    errs = []
    titles, descs = {}, {}
    files = {p: m["file"].read_text(encoding="utf-8") for p, m in PAGES.items()}
    sm = (ROOT / "sitemap.xml").read_text()
    inbound = {p: set() for p in PAGES}
    para_count = {}
    phone_re = re.compile(r"(?<![\d.])\d{3}[.\-) ]\s?\d{3}[.\- ]\d{4}(?![\d.])")
    for p, h in files.items():
        m = PAGES[p]
        t, d = m["title"], m["desc"]
        if len(t) > 60: errs.append(f"{p}: title {len(t)} chars")
        if p != "/404.html" and not 150 <= len(d) <= 160: errs.append(f"{p}: description {len(d)} chars")
        if t in titles: errs.append(f"{p}: duplicate title with {titles[t]}")
        if d in descs: errs.append(f"{p}: duplicate description with {descs[d]}")
        titles[t], descs[d] = p, p
        if p != "/404.html" and m["h1"].strip().lower() == t.split("|")[0].strip().lower(): errs.append(f"{p}: h1 equals title")
        h1s = re.findall(r"<h1[ >]", h)
        if len(h1s) != 1: errs.append(f"{p}: {len(h1s)} h1")
        main = h.split("<main", 1)[1].split("</main>", 1)[0]
        lv = [int(x) for x in re.findall(r"<h([1-6])[ >]", main)]
        for a, b in zip(lv, lv[1:]):
            if b > a + 1: errs.append(f"{p}: heading skips h{a}->h{b}"); break
        can = re.search(r'<link rel="canonical" href="([^"]+)"', h).group(1)
        ogu = re.search(r'<meta property="og:url" content="([^"]+)"', h).group(1)
        if can != ogu: errs.append(f"{p}: canonical != og:url")
        if m["indexable"] and f"<loc>{can}</loc>" not in sm: errs.append(f"{p}: not in sitemap")
        if 'content=""' in h: errs.append(f"{p}: empty meta content")
        if 'href="#"' in h: errs.append(f"{p}: href=#")
        for im in re.findall(r"<img [^>]*>", h):
            if " alt=" not in im: errs.append(f"{p}: img without alt")
        for ph in phone_re.findall(h):
            if ph != PHONE: errs.append(f"{p}: phone format {ph}")
        if "© 2026" not in h: errs.append(f"{p}: (c) year")
        if "updated" not in h.lower() and p != "/404.html": errs.append(f"{p}: no Updated date")
        for href in re.findall(r'href="(/[^"#?]*)', h):
            if href.startswith("/assets/"):
                if not (ROOT / href.lstrip("/")).exists(): errs.append(f"{p}: missing asset {href}")
                continue
            if href not in PAGES: errs.append(f"{p}: broken/non-canonical link {href}")
            elif href != p: inbound[href].add(p)
        for src in re.findall(r'(?:src|data-flyer)="(/assets/[^"?]+)', h):
            if not (ROOT / src.lstrip("/")).exists(): errs.append(f"{p}: missing {src}")
        for ld in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            g = json.loads(ld)["@graph"]
            ids = {n.get("@id") for n in g}
            for ref in re.findall(r'\{"@id":"([^"]+)"\}', ld):
                if ref not in ids: errs.append(f"{p}: unresolved @id {ref}")
            for n in g:
                if n.get("@type") == "FAQPage":
                    for q in n["mainEntity"]:
                        if f"<summary>{q['name']}</summary>" not in h: errs.append(f"{p}: FAQ not visible: {q['name']}")
                if n.get("@type") in ("Review", "AggregateRating"): errs.append(f"{p}: third-party review markup")
        body = re.sub(r'<nav class="crumbs".*?</nav>', "", main, flags=re.S)
        ctx = len(re.findall(r'<a [^>]*href="/(?!assets)', body))
        if p != "/404.html" and ctx < 5: errs.append(f"{p}: only {ctx} contextual links")
        for para in re.findall(r"<p[^>]*>(.*?)</p>", main, re.S):
            txt = re.sub("<[^>]+>", "", para).strip()
            if len(txt.split()) > 40: para_count.setdefault(txt, set()).add(p)
    for p, srcs in inbound.items():
        if p not in ("/", "/404.html") and len(srcs) < 3: errs.append(f"{p}: only {len(srcs)} inbound links")
    for txt, ps in para_count.items():
        if len(ps) > 3: errs.append(f"repeated paragraph on {len(ps)} pages: {txt[:60]}")
    for label, href in CARD_LINKS:
        if label.lower().split()[0] not in (PAGES[href]["h1"] + PAGES[href]["title"]).lower():
            errs.append(f"card '{label}' doesn't match {href}")
    navs = {re.search(r'<nav class="nav".*?</nav>', re.sub(r' aria-current="page"| is-active', "", h), re.S).group(0) for h in files.values()}
    if len(navs) != 1: errs.append("nav differs between pages")
    for f in (ROOT / "assets/img").glob("*.webp"):
        kb = f.stat().st_size / 1024
        if kb > (260 if f.name.endswith("-1866.webp") else 200): errs.append(f"image over budget {f.name} {kb:.0f}KB")
    return errs


if __name__ == "__main__":
    for old in ["index.html", "about.html", "menu.html", "events.html", "gallery.html", "event-center.html", "contact.html",
                "privacy-policy.html", "terms.html", "equal-opportunity-employer.html"]:
        (ROOT / old).unlink(missing_ok=True)
    home(); about(); menu_hub(); lunch(); dinner(); events_hub(); brunch(); taco(); sunday(); grand_opening()
    event_center(); rental(); gallery(); visit(); contact(); faq(); guides(); legal_pages(); not_found()
    site_files()
    errs = qa()
    print(f"Built {len(PAGES)} pages.")
    if errs:
        print("QA FAILED:\n  " + "\n  ".join(errs))
        sys.exit(1)
    print("QA passed: all Section 13 checks.")
