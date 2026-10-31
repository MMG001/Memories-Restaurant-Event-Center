#!/usr/bin/env python3
"""Builds the static pages for Memoire's Restaurant & Event Center.

Run:  python3 tools/build.py
Writes the .html files to the repo root (Cloudflare Pages serves them as-is,
no build command needed). Edit content here, re-run, commit.
"""
from pathlib import Path
import html

ROOT = Path(__file__).resolve().parent.parent
PHONE = "612.223.3679"
TEL = "tel:6122233679"
ADDR1 = "2201 N 44th Ave"
ADDR2 = "Minneapolis, MN 55412"
MAP_SRC = ("https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2819.488616996011!2d-93.30882559999999"
           "!3d45.035305599999994!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x52b33178124f1815%3A0xc4e937c2f0a73bae"
           "!2s2201%20N%2044th%20Ave%2C%20Minneapolis%2C%20MN%2055412!5e0!3m2!1sen!2sus!4v1793425613374!5m2!1sen!2sus")
DIRECTIONS = "https://www.google.com/maps/dir/?api=1&destination=2201+N+44th+Ave,+Minneapolis,+MN+55412"
SITE = "https://memories-restaurant-event-center.pages.dev"

e = html.escape

# ---------------------------------------------------------------- content

GRAND_OPENING = [
    ("Tues", "Nov", "10", "Tacos &amp; Tequila", "$20 rail happy hour flights", ""),
    ("Wed", "Nov", "11", "Live &amp; Local", "Just Dream", "8PM – 12AM"),
    ("Thur", "Nov", "12", "Jeopardy Karaoke", "", "8PM – 12AM"),
    ("Fri", "Nov", "13", "Finally Fridays!", "90’s Party", "9PM – 1AM"),
    ("Sat", "Nov", "14", "Brunch Vibez!!!", "The official return of Brunch Vibez", "11AM – 6PM"),
    ("Sun", "Nov", "15", "Vikings vs Packers", "", "11AM – 6PM"),
]

DINNER = [
    ("Memoire’s Cut", "$28", "A juicy, cooked-to-your-liking 10oz NY strip steak with 1 delicious side &amp; Texas toast."),
    ("Boss Cut", "$35", "12oz NY strip steak with 2 delicious sides &amp; Texas toast."),
    ("Salmon Medley", "$26", "7oz salmon over a bed of seasoned rice with a Cajun drizzle and vegetable medley."),
    ("The Memoire’s", "$25", "Choose 1 meat along with 2 delicious sides."),
    ("Meatless Memories", "$23", "Vegan stroganoff with Texas toast.", "Vegan"),
    ("Dirty Cabbage Skillet", "$18", "Vegan sizzling skillet with Impossible meat, caramelized cabbage and peppers, smothered in Cajun seasoning.", "Vegan"),
]
DINNER_MEATS = ["Catfish", "Chicken Wings", "Salmon"]
DINNER_SIDES = ["Mac &amp; Cheese", "Greens", "Yams", "Rice", "Red Beans and Rice", "Broccoli"]

LUNCH_MEATS = ["Catfish (1.6oz filet)", "Chicken Wings (3)", "Blackened Chicken", "Blackened Salmon"]
LUNCH_SIDES = ["Mac &amp; Cheese", "Greens", "Yams", "Rice", "Red Beans and Rice", "Broccoli", "Fries", "House Salad"]
LUNCH_VEGAN = ["Vegan Stroganoff with Texas Toast", "Parmesan Eggplant"]

TACO = [
    ("3 Beef Birrias", "$14", "Comes with consomé &amp; limes."),
    ("Birria Quesadilla", "$15", "Comes with consomé &amp; limes."),
    ("Birria Egg Rolls", "$15", "Comes with consomé &amp; limes."),
    ("Birria Pizza", "$24", "Comes with consomé &amp; limes."),
    ("Veggie Birria", "$14", "Comes with consomé &amp; limes."),
]

SUNDAY_MEATS = ["Roast", "Smothered Chicken", "Fried Chicken", "Catfish"]
SUNDAY_SIDES = ["Black Eyed Peas", "Cabbage (Turkey)", "Rice", "Yams", "Mac &amp; Cheese", "Green Beans &amp; Potatoes (Pork)", "Cornbread"]
SUNDAY_DESSERTS = ["Caramel Cake", "Banana Pudding"]

BRUNCH = [
    ("French Toast &amp; Flats", "$24", "Berry topping."),
    ("Vibe", "$26", "1 meat &amp; 2 sides."),
    ("Vibration", "$28", "1 meat &amp; 3 sides."),
    ("That’s a Vibe", "$32", "2 meats &amp; 3 sides."),
    ("Catfish &amp; Grits", "$26", ""),
    ("Shrimp &amp; Grits", "$26", ""),
    ("Steak &amp; Egg*", "$30", "2 eggs any style, steak &amp; Texas toast."),
    ("Chicken &amp; Waffle", "$22", "Choice of 3 whole wings or 2 strips. Waffle comes with strawberries &amp; powdered sugar."),
    ("Deep Fried Grits", "$23", "Comes with Texas toast, topped with green onions, shredded cheese &amp; a creamy buttersauce."),
    ("Boss Brunch*", "$40", "Grits, shrimp (4), 10oz NY strip steak &amp; Texas toast."),
    ("Kids Meal", "$12", "2 mini waffles or 1 pancake."),
]

FAQ = [
    ("Do I need a reservation?",
     f"Reservations are recommended, and they’re required for Brunch Vibez on Saturdays. Call <a href=\"{TEL}\">{PHONE}</a> to book your table."),
    ("Where are you located?",
     f"{ADDR1}, {ADDR2}. <a href=\"{DIRECTIONS}\" target=\"_blank\" rel=\"noopener\">Get directions</a>."),
    ("When is lunch and dinner served?",
     "Lunch is Wednesday – Friday, 11AM – 3PM. Dinner is Wednesday – Friday, 3:30PM – 8PM."),
    ("What’s happening each week?",
     "Taco Tuesday (11AM – 8PM), the Lunch Special Wednesday – Friday, Brunch Vibez every Saturday (11AM – 6PM) and the Soulfull Sunday soul food buffet."),
    ("When is happy hour?",
     "Tuesday – Friday, 11AM – 1PM and 6PM – 8PM."),
    ("Do you have vegan options?",
     "Yes. Meatless Memories (vegan stroganoff), the Dirty Cabbage Skillet with Impossible meat, Parmesan eggplant at lunch, and Veggie Birria on Taco Tuesday."),
    ("What’s included in the Soulfull Sunday buffet?",
     "The $37.99 buffet includes a drink and going through the buffet 3 times. We serve Pepsi products."),
    ("Can I host a private event at Memoire’s?",
     "Absolutely. Our event center hosts every type of event, and we provide the food and the DJ. <a href=\"event-center.html#rental\">Send a rental request</a> or call us."),
    ("Do you have a kids menu?",
     "At Brunch Vibez, the Kids Meal ($12) comes with 2 mini waffles or 1 pancake."),
]

HOURS = [
    ("Tuesday", "11AM – 8PM · Taco Tuesday"),
    ("Wednesday – Friday", "Lunch 11AM – 3PM<br>Dinner 3:30PM – 8PM"),
    ("Saturday", "11AM – 6PM · Brunch Vibez"),
    ("Sunday", "11AM – 6PM · Soulfull Sunday"),
    ("Happy Hour", "Tue – Fri · 11AM – 1PM &amp; 6PM – 8PM"),
]

# ---------------------------------------------------------------- shell

NAV = [
    ("Home", "index.html", [("Grand Opening", "index.html#grand-opening")]),
    ("About", "about.html", []),
    ("Menu", "menu.html", [("Lunch", "menu.html#lunch"), ("Dinner", "menu.html#dinner")]),
    ("Events", "events.html", [
        ("Brunch Vibez", "events.html#brunch-vibez"),
        ("Taco Tuesday", "events.html#taco-tuesday"),
        ("Soulfull Sundays", "events.html#soulfull-sunday"),
    ]),
    ("Gallery", "gallery.html", []),
    ("Event Center", "event-center.html", [("Rental", "event-center.html#rental")]),
    ("Contact", "contact.html", [("FAQ", "contact.html#faq")]),
]


def nav_html(active):
    out = []
    for label, href, subs in NAV:
        cur = ' aria-current="page"' if href == active else ""
        if subs:
            sub = "".join(f'<li><a href="{h}">{l}</a></li>' for l, h in subs)
            out.append(
                f'<li class="has-sub"><a href="{href}"{cur} class="top">{label}<span class="caret"></span></a>'
                f'<button type="button" class="sub-toggle" aria-label="Show {label} links" aria-expanded="false"></button>'
                f'<ul class="sub">{sub}</ul></li>'
            )
        else:
            out.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "".join(out)


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap" rel="stylesheet">')

FLYER_MODAL = ('<div class="modal" id="flyer" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Flyer">'
               '<div class="modal-box img"><button class="modal-x" type="button" aria-label="Close">×</button><img src="" alt=""></div></div>')


def page(fname, title, desc, active, main, extra_end=""):
    full_title = f"{title} | Memoire’s Restaurant &amp; Event Center" if title else "Memoire’s Restaurant &amp; Event Center | Minneapolis"
    ld = ""
    if fname == "index.html":
        ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@type":"Restaurant","name":"Memoire\'s Restaurant & Event Center",'
              f'"telephone":"+1-612-223-3679","servesCuisine":["Soul Food","Southern","American"],"acceptsReservations":true,'
              f'"address":{{"@type":"PostalAddress","streetAddress":"{ADDR1}","addressLocality":"Minneapolis","addressRegion":"MN","postalCode":"55412","addressCountry":"US"}},'
              f'"image":"{SITE}/assets/img/exterior-front.webp","url":"{SITE}/"}}</script>')
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#000000">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE}/assets/img/exterior-front.webp">
<meta property="og:type" content="website">
<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="apple-touch-icon" href="assets/img/favicon.png">
{FONTS}
<link rel="stylesheet" href="assets/css/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap head-in">
    <a class="brand" href="index.html" aria-label="Memoire’s Restaurant &amp; Event Center — Home"><img src="assets/img/logo-light.png" alt="Memoire’s Restaurant &amp; Event Center" width="1000" height="387"></a>
    <button class="menu-toggle" type="button" aria-label="Menu" aria-expanded="false" aria-controls="site-nav"><span></span></button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <ul>{nav_html(active)}</ul>
      <a class="btn" href="{TEL}">Reservations</a>
    </nav>
  </div>
</header>
<main id="main">
{main}
</main>
<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <img class="foot-logo" src="assets/img/logo-light.png" alt="Memoire’s Restaurant &amp; Event Center" width="1000" height="387" loading="lazy">
      <p>Soul food, steaks and good company — a Minneapolis restaurant and event center made for memories.</p>
    </div>
    <div>
      <h4>Visit</h4>
      <p>{ADDR1}<br>{ADDR2}</p>
      <p><a href="{DIRECTIONS}" target="_blank" rel="noopener">Get directions</a></p>
    </div>
    <div>
      <h4>Reservations</h4>
      <p><a href="{TEL}" style="font-family:var(--serif);font-size:1.6rem;color:#fff">{PHONE}</a></p>
      <p>Happy Hour<br>Tue – Fri · 11AM – 1PM &amp; 6PM – 8PM</p>
    </div>
    <div>
      <h4>Explore</h4>
      <ul>
        <li><a href="menu.html#lunch">Lunch Menu</a></li>
        <li><a href="menu.html#dinner">Dinner Menu</a></li>
        <li><a href="events.html">Weekly Events</a></li>
        <li><a href="event-center.html">Event Center</a></li>
        <li><a href="gallery.html">Gallery</a></li>
        <li><a href="contact.html#faq">FAQ</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap lower">
    <span>© <span id="year">2026</span> Memoire’s Restaurant &amp; Event Center. All rights reserved.</span>
    <nav aria-label="Legal">
      <a href="privacy-policy.html">Privacy Policy</a>
      <a href="equal-opportunity-employer.html">Equal Opportunity Employer</a>
      <a href="terms.html">Terms &amp; Conditions</a>
    </nav>
  </div>
</footer>
{FLYER_MODAL}
{extra_end}
<script src="assets/js/site.js"></script>
</body>
</html>
"""
    (ROOT / fname).write_text(doc, encoding="utf-8")


def banner(eyebrow, title, text, img, crumb):
    return f"""<section class="banner">
  <div class="bg"><img src="assets/img/{img}" alt="" fetchpriority="high"></div>
  <div class="wrap">
    <span class="eyebrow">{eyebrow}</span>
    <h1>{title}</h1>
    <p>{text}</p>
    <div class="crumbs"><a href="index.html">Home</a> &nbsp;/&nbsp; {crumb}</div>
  </div>
</section>"""


def items(rows):
    out = []
    for r in rows:
        name, price, desc = r[0], r[1], r[2]
        tag = f'<span class="tag">{r[3]}</span>' if len(r) > 3 else ""
        d = f"<p>{desc}</p>" if desc else ""
        out.append(f'<div class="item"><div class="row"><h4>{name}</h4><span class="dots"></span><span class="price">{price}</span></div>{d}{tag}</div>')
    return '<div class="menu-list">' + "".join(out) + "</div>"


def opt(title, lst, extra=""):
    li = "".join(f"<li>{x}</li>" for x in lst)
    return f'<div class="opt"><h4>{title}</h4>{extra}<ul>{li}</ul></div>'


def flyer_btn(src, alt, label="View the flyer"):
    return f'<button type="button" class="flyer-link" data-flyer="assets/img/{src}" data-alt="{alt}">{label}</button>'


def cta(img="bar.webp"):
    return f"""<section class="cta">
  <div class="bg"><img src="assets/img/{img}" alt="" loading="lazy"></div>
  <div class="wrap center reveal">
    <span class="eyebrow">Reservations</span>
    <h2>Save Your Seat</h2>
    <a class="phone-big" href="{TEL}">{PHONE}</a>
    <p style="color:#ccc">{ADDR1} · {ADDR2}</p>
  </div>
</section>"""


def go_list():
    out = []
    for dow, mon, day, title, sub, time in GRAND_OPENING:
        s = f"<p>{sub}</p>" if sub else ""
        t = f'<span class="time">{time}</span>' if time else ""
        out.append(f'<li><div class="go-date"><small>{dow}</small><b>{day}</b><em>{mon}</em></div><div><h3>{title}</h3>{s}{t}</div></li>')
    return "".join(out)


def pop_list():
    out = []
    for dow, mon, day, title, sub, time in GRAND_OPENING:
        detail = " · ".join(x for x in (sub, time) if x)
        out.append(f'<li><div class="d">{dow}<b>{mon} {day}</b></div><div><strong>{title}</strong><span>{detail}</span></div></li>')
    return "".join(out)


ICONS = {
    "food": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M7 2v20M4 2v6a3 3 0 0 0 6 0V2M17 2c-2 2-3 5-3 8h3v12"/></svg>',
    "music": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>',
    "star": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/></svg>',
    "room": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 21h18M5 21V8l7-5 7 5v13M9 21v-6h6v6"/></svg>',
}

# ---------------------------------------------------------------- pages


def home():
    weekly = [
        ("Tuesdays", "11AM – 8PM", "Taco Tuesday", "Birria tacos, quesadillas, egg rolls and birria pizza, all with consomé &amp; limes.", "From $14", "food-birria.webp", "events.html#taco-tuesday"),
        ("Wed – Fri", "11AM – 3PM", "Lunch Special", "Choose your meat and sides — catfish, wings, blackened chicken or salmon.", "$17.99", "food-mac-chicken.webp", "menu.html#lunch"),
        ("Wed – Fri", "3:30PM – 8PM", "Dinner", "NY strip steaks, Cajun salmon medley, soul plates and vegan favorites.", "From $18", "food-steak.webp", "menu.html#dinner"),
        ("Saturdays", "11AM – 6PM", "Brunch Vibez", "Chicken &amp; waffles, shrimp &amp; grits, steak &amp; eggs and the Boss Brunch.", "From $22", "food-chicken-waffle.webp", "events.html#brunch-vibez"),
        ("Sundays", "Soul Food Buffet", "Soulfull Sunday", "Includes a drink &amp; going through the buffet 3 times.", "$37.99", "food-soul-plate.webp", "events.html#soulfull-sunday"),
    ]
    cards = "".join(
        f'<article class="card reveal"><div class="ph"><img src="assets/img/{img}" alt="" loading="lazy"><span class="badge">{b}</span></div>'
        f'<div class="body"><span class="day">{d}</span><h3>{t}</h3><p>{p}</p><div class="foot"><span class="price">{pr}</span><span class="more">Details</span></div></div>'
        f'<a class="cover" href="{h}" aria-label="{e(t)}"></a></article>'
        for b, d, t, p, pr, img, h in weekly)
    main = f"""
<section class="hero">
  <div class="bg"><img src="assets/img/exterior-front.webp" alt="" fetchpriority="high"></div>
  <div class="wrap">
    <img class="hero-logo" src="assets/img/logo-light.png" alt="Memoire’s Restaurant &amp; Event Center" width="1000" height="387">
    <p class="tag">Where every plate becomes a memory.</p>
    <div class="btn-row" style="justify-content:center">
      <a class="btn" href="{TEL}">Reserve · {PHONE}</a>
      <a class="btn ghost" href="menu.html">View the Menu</a>
    </div>
    <div class="meta"><span>{ADDR1} · Minneapolis</span><a href="#grand-opening">Grand Opening · Nov 10 – 15</a></div>
  </div>
  <span class="scroll-cue" aria-hidden="true"></span>
</section>

<section class="go" id="grand-opening">
  <div class="wrap">
    <div class="center reveal" style="margin-bottom:46px">
      <span class="eyebrow">You’re Invited</span>
      <h2>Grand Opening Week</h2>
      <p class="lead">Six nights to celebrate. Tacos and tequila, live music, karaoke, a 90’s party, the return of Brunch Vibez and the big game — join us November 10 – 15.</p>
    </div>
    <div class="go-grid">
      <div class="reveal">
        <ul class="go-list">{go_list()}</ul>
        <div class="happy">
          <h4>Happy Hour</h4>
          <p>Tues – Fri · 11AM – 1PM &amp; 6PM – 8PM</p>
        </div>
      </div>
      <div class="go-side reveal">
        <button type="button" data-flyer="assets/img/flyer-grand-opening.jpg" data-alt="Grand Opening flyer" style="all:unset;cursor:zoom-in;display:block">
          <img src="assets/img/flyer-grand-opening.jpg" alt="Memoire’s Grand Opening flyer, November 10 – 15" loading="lazy" width="1238" height="1838">
        </button>
        <div class="center" style="margin-top:18px"><a class="btn" href="{TEL}">Reserve Your Table</a></div>
      </div>
    </div>
  </div>
</section>

<section class="alt">
  <div class="wrap split">
    <div class="frame reveal"><img src="assets/img/dining-hall.webp" alt="Memoire’s dining room with warm wood floors and pendant lighting" loading="lazy"></div>
    <div class="reveal">
      <span class="eyebrow">Our Story</span>
      <h2>Soul Food, Served With Elegance</h2>
      <p class="lead">Memoire’s brings Southern comfort and a refined night out together under one roof on Minneapolis’ North Side — slow-cooked classics, hand-cut steaks and a room built for celebrating.</p>
      <p>Whether you’re here for a quick lunch, a Saturday brunch with friends or a celebration in our event center, we’re here to make it memorable.</p>
      <div class="btn-row"><a class="btn ghost" href="about.html">About Memoire’s</a></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="center reveal" style="margin-bottom:46px">
      <span class="eyebrow">Every Week</span>
      <h2>Something to Look Forward To</h2>
    </div>
    <div class="cards five">{cards}</div>
  </div>
</section>

<section class="alt">
  <div class="wrap split rev">
    <div class="frame reveal"><img src="assets/img/dining-windows.webp" alt="Bright event space with large windows" loading="lazy"></div>
    <div class="reveal">
      <span class="eyebrow">Event Center</span>
      <h2>Host Your Next Celebration</h2>
      <p class="lead">Birthdays, showers, receptions, repasts, corporate gatherings — every type of event. We provide the food and the DJ; you bring the guests.</p>
      <div class="btn-row"><a class="btn" href="event-center.html#rental">Request a Rental</a><a class="btn ghost" href="event-center.html">Explore the Space</a></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">Find Us</span>
      <h2>Visit Memoire’s</h2>
      <div class="info">
        <div><h4>Address</h4><p>{ADDR1}<br>{ADDR2}</p></div>
        <div><h4>Reservations</h4><p><a href="{TEL}">{PHONE}</a></p></div>
        <div><table class="hours">{"".join(f"<tr><td>{d}</td><td>{h}</td></tr>" for d, h in HOURS)}</table></div>
      </div>
      <div class="btn-row" style="margin-top:26px"><a class="btn ghost" href="{DIRECTIONS}" target="_blank" rel="noopener">Get Directions</a></div>
    </div>
    <div class="map reveal"><iframe src="{MAP_SRC}" title="Map to Memoire’s, 2201 N 44th Ave, Minneapolis" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
  </div>
</section>
"""
    promo = f"""<div class="modal" id="promo" aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="promo-t">
  <div class="modal-box">
    <button class="modal-x" type="button" aria-label="Close">×</button>
    <img class="pop-logo" src="assets/img/logo-light.png" alt="" style="width:190px;margin:0 auto 8px" width="1000" height="387">
    <h2 id="promo-t">Grand Opening</h2>
    <div class="sub-t">November 10 – 15</div>
    <ul class="pop-list">{pop_list()}</ul>
    <div class="btn-row" style="justify-content:center">
      <a class="btn" href="{TEL}">Reserve · {PHONE}</a>
      <a class="btn ghost" href="#grand-opening" data-close>See the Lineup</a>
    </div>
  </div>
</div>"""
    page("index.html", "", "Memoire’s Restaurant & Event Center — soul food, steaks, weekly events and private event rentals at 2201 N 44th Ave, Minneapolis. Reservations 612.223.3679.", "index.html", main, promo)


def about():
    main = banner("About Us", "The Memoire’s Story", "A North Minneapolis home for soul food, good company and celebrations worth remembering.", "dining-room.webp", "About") + f"""
<section>
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">Who We Are</span>
      <h2>Made for Memories</h2>
      <p class="lead">Memoire’s Restaurant &amp; Event Center is a place to slow down, gather and celebrate.</p>
      <p>Our kitchen serves soul food classics and hand-cut steaks — fried catfish, smothered chicken, mac &amp; cheese, greens and yams, alongside our Memoire’s Cut and Boss Cut NY strips. Every week brings something to look forward to: Taco Tuesday, a weekday lunch special, Brunch Vibez on Saturdays and our Soulfull Sunday buffet.</p>
      <p>Beyond the dining room, our event center is ready for every type of occasion, with food and a DJ provided by our team.</p>
    </div>
    <div class="frame reveal"><img src="assets/img/exterior-corner.webp" alt="Memoire’s white brick exterior with arched doorway" loading="lazy"></div>
  </div>
</section>
<section class="alt">
  <div class="wrap">
    <div class="center reveal" style="margin-bottom:46px"><span class="eyebrow">What We’re About</span><h2>The Memoire’s Experience</h2></div>
    <div class="features reveal">
      <div class="feature"><div class="ico">{ICONS['food']}</div><h3>Soulful Cooking</h3><p>Southern comfort classics, steaks and salmon — plus vegan dishes so everyone has a seat at the table.</p></div>
      <div class="feature"><div class="ico">{ICONS['music']}</div><h3>Weekly Vibes</h3><p>Taco Tuesday, Brunch Vibez, Soulfull Sunday and happy hour Tuesday through Friday.</p></div>
      <div class="feature"><div class="ico">{ICONS['room']}</div><h3>Event Center</h3><p>A warm, modern space for private parties and gatherings of every kind.</p></div>
      <div class="feature"><div class="ico">{ICONS['star']}</div><h3>Hospitality</h3><p>An elegant room, a friendly team and a night out that feels like home.</p></div>
    </div>
  </div>
</section>
<section>
  <div class="wrap split rev">
    <div class="frame reveal"><img src="assets/img/bar.webp" alt="Memoire’s bar and open kitchen" loading="lazy"></div>
    <div class="reveal">
      <span class="eyebrow">Our Space</span>
      <h2>Warm, Modern &amp; Welcoming</h2>
      <p>Wood floors, black-and-white finishes, a full bar and big windows that fill the room with light. Come for lunch, stay for happy hour.</p>
      <div class="btn-row"><a class="btn" href="menu.html">See the Menu</a><a class="btn ghost" href="events.html">Weekly Events</a></div>
    </div>
  </div>
</section>
""" + cta()
    page("about.html", "About", "About Memoire’s Restaurant & Event Center — soul food, steaks and celebrations in North Minneapolis.", "about.html", main)


def menu():
    main = banner("Our Menu", "Lunch &amp; Dinner", "Soul food plates, hand-cut steaks and Cajun salmon — served Wednesday through Friday.", "food-steak-fillet.webp", "Menu") + f"""
<section id="lunch">
  <div class="wrap">
    <div class="split reveal">
      <div>
        <span class="eyebrow">Lunch Menu · Wednesday – Friday</span>
        <h2>Lunch Special</h2>
        <div class="price-hero"><span>$</span>17.99</div>
        <p class="lead">Pick your meat and sides for a midday plate done right.</p>
        <p><span class="when">Wed – Fri · 11AM – 3PM</span></p>
      </div>
      <div class="frame"><img src="assets/img/food-mac-chicken.webp" alt="Lunch plate with mac and cheese" loading="lazy"></div>
    </div>
    <div class="opts reveal">
      {opt("Meats", LUNCH_MEATS)}
      {opt("Sides", LUNCH_SIDES)}
      {opt("Vegan Option", LUNCH_VEGAN, '<div class="big">$16</div>')}
    </div>
    {flyer_btn("flyer-lunch.jpg", "Lunch Special flyer", "View the lunch flyer")}
  </div>
</section>

<section id="dinner" class="alt">
  <div class="wrap">
    <div class="menu-head reveal">
      <div><span class="eyebrow">Dinner Menu</span><h2>Dinner</h2></div>
      <span class="when">Wed – Fri · 3:30PM – 8PM</span>
    </div>
    <div class="reveal">{items(DINNER)}</div>
    <div class="opts reveal">
      {opt("Meats", DINNER_MEATS)}
      {opt("Sides", DINNER_SIDES)}
    </div>
    <div class="reveal">{flyer_btn("flyer-dinner.jpg", "Dinner menu flyer", "View the dinner flyer")}</div>
  </div>
</section>
<section>
  <div class="wrap center reveal">
    <span class="eyebrow">More to Taste</span>
    <h2>Brunch &amp; Weekly Specials</h2>
    <p class="lead">Taco Tuesday, Brunch Vibez and Soulfull Sunday menus live on the Events page.</p>
    <div class="pills">
      <a href="events.html#taco-tuesday">Taco Tuesday</a>
      <a href="events.html#brunch-vibez">Brunch Vibez</a><a href="events.html#soulfull-sunday">Soulfull Sunday</a>
    </div>
  </div>
</section>
""" + cta("food-steak.webp")
    page("menu.html", "Lunch & Dinner Menu", "Memoire’s menu — $17.99 lunch special Wed–Fri 11AM–3PM; dinner with Memoire’s Cut, Boss Cut, Salmon Medley and vegan options Wed–Fri 3:30PM–8PM.", "menu.html", main)


def events():
    main = banner("Every Week at Memoire’s", "Events &amp; Specials", "Brunch on Saturday, buffet on Sunday and tacos on Tuesday.", "food-chicken-waffle.webp", "Events") + f"""
<section style="padding-bottom:0">
  <div class="wrap center">
    <div class="pills" style="margin-top:0">
      <a href="#brunch-vibez">Brunch Vibez</a><a href="#taco-tuesday">Taco Tuesday</a><a href="#soulfull-sunday">Soulfull Sundays</a>
    </div>
  </div>
</section>

<section id="brunch-vibez">
  <div class="wrap">
    <div class="split reveal" style="margin-bottom:30px">
      <div>
        <span class="eyebrow">Each &amp; Every Saturday</span>
        <h2>Brunch Vibez</h2>
        <p class="lead">Chicken &amp; waffles, grits done every way and steak &amp; eggs — Saturdays from 11AM to 6PM. Powered by JS Promotions.</p>
        <p><span class="when">Saturdays · 11AM – 6PM</span></p>
        <p style="color:#fff;letter-spacing:.18em;text-transform:uppercase;font-size:.85rem">Reservations required · <a href="{TEL}" class="red">{PHONE}</a></p>
      </div>
      <div><img src="assets/img/brunch-vibez-logo.webp" alt="Brunch Vibez" loading="lazy" style="border-radius:4px;border:1px solid var(--line)"></div>
    </div>
    <div class="menu-head reveal"><h3>Menu Highlights</h3></div>
    <div class="reveal">{items(BRUNCH)}</div>
    <p class="note">* Consuming raw or undercooked meats, poultry, seafood, shellfish or eggs may increase your risk of foodborne illness.</p>
    {flyer_btn("flyer-brunch-vibez.jpg", "Brunch Vibez flyer", "View the Brunch Vibez flyer")}
  </div>
</section>

<section id="taco-tuesday" class="alt">
  <div class="wrap">
    <div class="split rev reveal" style="margin-bottom:30px">
      <div>
        <span class="eyebrow">Each &amp; Every Tuesday</span>
        <h2>Taco Tuesday</h2>
        <p class="lead">Rich, slow-braised birria with consomé for dipping.</p>
        <p><span class="when">Open 11AM – 8PM</span></p>
      </div>
      <div class="frame"><img src="assets/img/food-tacos.webp" alt="Birria tacos" loading="lazy"></div>
    </div>
    <div class="reveal">{items(TACO)}</div>
    <div class="opts reveal">
      <div class="opt"><h4>Taco Flight</h4><div class="big">$15</div><ul><li>4 Tacos</li><li>11AM – 3PM</li></ul></div>
      <div class="opt"><h4>Snack Pack</h4><div class="big">$22</div><ul><li>3 Tacos &amp; 2 Egg Rolls</li></ul></div>
      {opt("Meat Options", ["Chicken", "Shredded Beef", "Shrimp"])}
    </div>
    {flyer_btn("flyer-taco-tuesday.jpg", "Taco Tuesday flyer", "View the Taco Tuesday flyer")}
  </div>
</section>

<section id="soulfull-sunday">
  <div class="wrap">
    <div class="split reveal">
      <div>
        <span class="eyebrow">Each &amp; Every Sunday</span>
        <h2>Soulfull Sunday</h2>
        <p style="font-family:var(--serif);font-style:italic;font-size:1.5rem;color:#fff;margin:0">Soul Food Buffet</p>
        <div class="price-hero"><span>$</span>37.99</div>
        <p class="lead">Includes a drink &amp; going through the buffet 3 times.</p>
      </div>
      <div class="frame"><img src="assets/img/food-soul-plate.webp" alt="Soul food plate with fried chicken, greens and mashed potatoes" loading="lazy"></div>
    </div>
    <div class="opts reveal">
      {opt("Meats", SUNDAY_MEATS)}
      {opt("Sides", SUNDAY_SIDES)}
      {opt("Desserts", SUNDAY_DESSERTS)}
    </div>
    <p class="note">We proudly serve Pepsi products.</p>
    {flyer_btn("flyer-soulfull-sunday.jpg", "Soulfull Sunday flyer", "View the Soulfull Sunday flyer")}
  </div>
</section>
""" + cta("food-chicken-cornbread.webp")
    page("events.html", "Events & Specials", "Weekly at Memoire’s: Brunch Vibez Saturdays, Taco Tuesday and Soulfull Sunday soul food buffet.", "events.html", main)


def gallery():
    main = banner("Gallery", "Gallery", "A look inside Memoire’s.", "dining-windows.webp", "Gallery") + """
<section>
  <div class="wrap center reveal">
    <span class="eyebrow">Full Gallery</span>
    <h2>Coming Soon</h2>
    <p class="lead">We’re capturing our food, our space and your celebrations. Here’s a first look.</p>
    <span class="soon">Coming Soon</span>
  </div>
  <div class="wrap" style="margin-top:50px">
    <div class="gallery reveal">
      <figure class="g1"><img src="assets/img/exterior-front.webp" alt="Memoire’s exterior" loading="lazy"></figure>
      <figure class="g2"><img src="assets/img/bar.webp" alt="The bar" loading="lazy"></figure>
      <figure class="g3"><img src="assets/img/food-chicken-waffle.webp" alt="Chicken and waffles" loading="lazy"></figure>
      <figure class="g4"><img src="assets/img/dining-room.webp" alt="Dining room" loading="lazy"></figure>
      <figure class="g5"><img src="assets/img/food-steak.webp" alt="Grilled steak" loading="lazy"></figure>
    </div>
  </div>
</section>
""" + cta()
    page("gallery.html", "Gallery", "Gallery coming soon — a look inside Memoire’s Restaurant & Event Center.", "gallery.html", main)


def event_center():
    types = ["Birthdays", "Weddings &amp; Receptions", "Bridal &amp; Baby Showers", "Anniversaries", "Graduations",
             "Family Reunions", "Repasts &amp; Celebrations of Life", "Corporate Events", "Holiday Parties",
             "Fundraisers", "Networking Mixers", "Private Dinners"]
    tags = "".join(f"<span>{t}</span>" for t in types)
    ev_opts = "".join(f"<option>{t.replace('&amp;', '&')}</option>" for t in types) + "<option>Other</option>"
    main = banner("Event Center", "Celebrate at Memoire’s", "Every type of event, with the food and the DJ provided.", "dining-hall.webp", "Event Center") + f"""
<section>
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">Private Events</span>
      <h2>Your Event, Handled</h2>
      <p class="lead">Our event center is a warm, modern space ready for gatherings of every size and style.</p>
      <p>Our team takes care of the details that matter most — a full menu from our kitchen and a DJ to keep the night moving — so you can enjoy your guests.</p>
      <div class="btn-row"><a class="btn" href="#rental">Request a Rental</a><a class="btn ghost" href="{TEL}">Call {PHONE}</a></div>
    </div>
    <div class="frame reveal"><img src="assets/img/dining-windows.webp" alt="Event space with tall windows" loading="lazy"></div>
  </div>
</section>
<section class="alt">
  <div class="wrap">
    <div class="center reveal" style="margin-bottom:46px"><span class="eyebrow">Included</span><h2>We Provide</h2></div>
    <div class="features reveal">
      <div class="feature"><div class="ico">{ICONS['food']}</div><h3>Food</h3><p>Catering from the Memoire’s kitchen — soul food favorites, steaks, salmon and vegan options, buffet or plated.</p></div>
      <div class="feature"><div class="ico">{ICONS['music']}</div><h3>DJ</h3><p>A DJ to set the mood, from dinner music to a full dance floor.</p></div>
      <div class="feature"><div class="ico">{ICONS['room']}</div><h3>The Space</h3><p>An elegant room with a full bar, warm lighting and flexible seating.</p></div>
      <div class="feature"><div class="ico">{ICONS['star']}</div><h3>Our Team</h3><p>Friendly staff to help plan and host your event from start to finish.</p></div>
    </div>
  </div>
</section>
<section>
  <div class="wrap center reveal">
    <span class="eyebrow">Every Type of Event</span>
    <h2>If You’re Celebrating, We’re Hosting</h2>
    <div class="tags" style="margin-top:30px">{tags}</div>
  </div>
</section>
<section id="rental" class="alt">
  <div class="narrow">
    <div class="center reveal" style="margin-bottom:36px">
      <span class="eyebrow">Rental</span>
      <h2>Request Your Date</h2>
      <p class="lead">Tell us about your event and our team will follow up with availability and pricing.</p>
    </div>
    <form class="form reveal" data-inquiry="Event Center Rental Request" novalidate>
      <div class="hp" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
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
            <label><input type="checkbox" name="Services" value="Food / Catering" checked> Food / Catering</label>
            <label><input type="checkbox" name="Services" value="DJ" checked> DJ</label>
            <label><input type="checkbox" name="Services" value="Bar Service"> Bar Service</label>
            <label><input type="checkbox" name="Services" value="Decor"> Decor</label>
          </div>
        </fieldset>
        <div class="full"><label for="r-msg">Tell Us About Your Event</label><textarea id="r-msg" name="Details" placeholder="Theme, menu ideas, special requests…"></textarea></div>
        <div class="full"><button class="btn" type="submit" style="width:100%">Submit Rental Request</button></div>
      </div>
      <div class="form-msg" role="status" aria-live="polite"></div>
    </form>
  </div>
</section>
""" + cta("dining-room.webp")
    page("event-center.html", "Event Center & Rentals", "Rent Memoire’s Event Center in Minneapolis for every type of event — food and DJ provided. Request your date online.", "event-center.html", main)


def contact():
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)
    main = banner("Contact", "Get in Touch", "Reservations, questions or private events — we’d love to hear from you.", "exterior-corner.webp", "Contact") + f"""
<section>
  <div class="wrap split" style="align-items:start">
    <div class="reveal">
      <span class="eyebrow">Visit &amp; Call</span>
      <h2>Memoire’s</h2>
      <div class="info">
        <div><h4>Reservations</h4><p><a class="phone-big" style="font-size:2.2rem;margin:0" href="{TEL}">{PHONE}</a></p></div>
        <div><h4>Address</h4><p>{ADDR1}<br>{ADDR2}<br><a href="{DIRECTIONS}" target="_blank" rel="noopener">Get directions →</a></p></div>
        <div><h4>Hours &amp; Specials</h4><table class="hours">{"".join(f"<tr><td>{d}</td><td>{h}</td></tr>" for d, h in HOURS)}</table></div>
      </div>
    </div>
    <div class="reveal">
      <form class="form" data-inquiry="Website Message" novalidate>
        <h3 style="margin-bottom:.8em">Send a Message</h3>
        <div class="hp" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
        <div class="grid2">
          <div><label for="c-name">Name <span class="req">*</span></label><input id="c-name" name="Name" required autocomplete="name"></div>
          <div><label for="c-phone">Phone</label><input id="c-phone" name="Phone" type="tel" autocomplete="tel"></div>
          <div class="full"><label for="c-email">Email <span class="req">*</span></label><input id="c-email" name="Email" type="email" required autocomplete="email"></div>
          <div class="full"><label for="c-topic">Topic</label><select id="c-topic" name="Topic"><option>General Question</option><option>Reservation</option><option>Private Event</option><option>Feedback</option><option>Careers</option></select></div>
          <div class="full"><label for="c-msg">Message <span class="req">*</span></label><textarea id="c-msg" name="Message" required></textarea></div>
          <div class="full"><button class="btn" type="submit" style="width:100%">Send Message</button></div>
        </div>
        <div class="form-msg" role="status" aria-live="polite"></div>
      </form>
    </div>
  </div>
</section>
<section style="padding:0">
  <div class="map"><iframe src="{MAP_SRC}" title="Map to Memoire’s, 2201 N 44th Ave, Minneapolis" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
</section>
<section id="faq" class="alt">
  <div class="narrow">
    <div class="center reveal" style="margin-bottom:30px"><span class="eyebrow">FAQ</span><h2>Frequently Asked Questions</h2></div>
    <div class="faq reveal">{faq}</div>
  </div>
</section>
"""
    page("contact.html", "Contact & FAQ", "Contact Memoire’s Restaurant & Event Center — 2201 N 44th Ave, Minneapolis. Reservations 612.223.3679. FAQ.", "contact.html", main)


def legal(fname, title, body_html):
    main = banner("Legal", title, "", "dining-room.webp", title) + f"""
<section><div class="narrow legal"><p class="updated">Last updated: October 31, 2026</p>{body_html}</div></section>"""
    page(fname, title, f"{title} — Memoire’s Restaurant & Event Center.", "", main)


def legal_pages():
    legal("privacy-policy.html", "Privacy Policy", f"""
<p>Memoire’s Restaurant &amp; Event Center (“Memoire’s,” “we,” “us”) respects your privacy. This policy explains what information we collect through this website and how we use it.</p>
<h2>Information We Collect</h2>
<p>We only collect information you choose to give us — for example your name, phone number, email address and event details when you send a message or rental request. Like most websites, our hosting provider may also record basic technical data such as browser type and pages visited.</p>
<h2>How We Use It</h2>
<ul><li>To respond to your questions, reservations and event inquiries.</li><li>To plan and provide services you request.</li><li>To improve our website and guest experience.</li></ul>
<h2>Sharing</h2>
<p>We do not sell your personal information. We only share it with service providers who help us operate the website or our business, or when required by law.</p>
<h2>Third-Party Services</h2>
<p>This site uses Google Maps and Google Fonts, which may collect data under their own privacy policies.</p>
<h2>Your Choices</h2>
<p>You can ask us to update or delete information you’ve sent us by calling <a href="{TEL}">{PHONE}</a>.</p>
<h2>Contact</h2>
<p>Memoire’s Restaurant &amp; Event Center, {ADDR1}, {ADDR2} · <a href="{TEL}">{PHONE}</a></p>
""")
    legal("equal-opportunity-employer.html", "Equal Opportunity Employer", f"""
<p>Memoire’s Restaurant &amp; Event Center is proud to be an Equal Opportunity Employer.</p>
<p>We are committed to providing equal employment opportunities to all employees and applicants without regard to race, color, religion, creed, sex, sexual orientation, gender identity, national origin, ancestry, age, disability, marital status, familial status, status with regard to public assistance, veteran status, genetic information or any other characteristic protected by federal, state or local law.</p>
<p>This policy applies to all terms and conditions of employment, including recruiting, hiring, placement, promotion, training, compensation, benefits and termination.</p>
<p>We are also committed to providing reasonable accommodations to qualified individuals with disabilities. If you need an accommodation during the application process, please call <a href="{TEL}">{PHONE}</a>.</p>
<h2>Join Our Team</h2>
<p>Interested in working at Memoire’s? Stop by {ADDR1} or <a href="contact.html">send us a message</a> with “Careers” as the topic.</p>
""")
    legal("terms.html", "Terms &amp; Conditions", f"""
<p>By using this website you agree to these terms. If you do not agree, please do not use the site.</p>
<h2>Menu, Pricing &amp; Events</h2>
<p>Menu items, prices, hours and events are subject to change without notice. Items and specials are available while supplies last. Prices do not include tax or gratuity.</p>
<h2>Reservations &amp; Rentals</h2>
<p>Reservations and event center rentals are confirmed only after you hear back from our team. Submitting a request through this website does not guarantee availability. Deposits, minimums and cancellation terms for private events will be provided in writing.</p>
<h2>Food Safety &amp; Allergies</h2>
<p>Consuming raw or undercooked meats, poultry, seafood, shellfish or eggs may increase your risk of foodborne illness. Please tell your server about any allergies; our kitchen handles common allergens and we cannot guarantee any item is allergen-free.</p>
<h2>Alcohol</h2>
<p>Alcohol is served only to guests 21 and older with valid ID. Please drink responsibly.</p>
<h2>Website Content</h2>
<p>All logos, images and content on this site belong to Memoire’s Restaurant &amp; Event Center or are used with permission and may not be reused without written consent.</p>
<h2>Limitation of Liability</h2>
<p>This website is provided “as is.” We make reasonable efforts to keep information accurate but are not liable for errors or omissions.</p>
<h2>Contact</h2>
<p>Questions? Call <a href="{TEL}">{PHONE}</a> or visit us at {ADDR1}, {ADDR2}.</p>
""")


def not_found():
    main = f"""<section class="banner" style="min-height:80vh;display:grid;place-items:center">
  <div class="bg"><img src="assets/img/dining-room.webp" alt=""></div>
  <div class="wrap"><span class="eyebrow">404</span><h1>Page Not Found</h1><p>The page you’re looking for has moved or no longer exists.</p>
  <div class="btn-row" style="justify-content:center;margin-top:24px"><a class="btn" href="index.html">Back Home</a><a class="btn ghost" href="menu.html">View Menu</a></div></div>
</section>"""
    page("404.html", "Page Not Found", "Page not found.", "", main)


if __name__ == "__main__":
    home(); about(); menu(); events(); gallery(); event_center(); contact(); legal_pages(); not_found()
    print("Built pages in", ROOT)
