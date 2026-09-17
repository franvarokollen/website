#!/usr/bin/env python3
"""
build-faq.py — renders the FAQ page in Swedish (/vanliga-fragor) and English
(/en/faq) from tools/faq.json, using the site shell from om-oss.html.

Edit tools/faq.json (each entry is [question, answerHtml]), then run

    python3 tools/build-faq.py
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://franvarokollen.com"
FK = '<span translate=no class=notranslate>Frånvarokollen</span>'

PAGES = {
    "sv": {
        "out": "vanliga-fragor.html", "url": "/vanliga-fragor", "alt": "/en/faq", "lang": "sv", "locale": "sv_SE",
        "title": "Vanliga frågor om Frånvarokollen – GDPR, inloggning, schemasystem",
        "description": "Svar på de vanligaste frågorna skolor ställer om Frånvarokollen: vad systemet gör, var data lagras, hur personalen loggar in och hur ni kommer igång.",
        "eyebrow": "VANLIGA FRÅGOR", "h1": "Frågor vi ofta får från skolor",
        "lead": f"Kort och rakt om vad {FK} är, hur det fungerar och vad som gäller kring data och inloggning. Saknar ni något? Mejla <a href=\"mailto:info@franvarokollen.com\">info@franvarokollen.com</a>.",
        "back": "Tillbaka till startsidan", "back_href": "/",
        "cta_eyebrow": "KOM IGÅNG", "cta_title": f"Vill ni se hur {FK} fungerar på er skola?",
        "cta_text": "Hösten 2026 bjuder vi in 15 partnerskolor som formar verktyget tillsammans med oss.",
        "cta_primary": "Ansök om partnerplats", "cta_primary_href": "/bli-partnerskola",
        "cta_secondary": "Läs våra guider", "cta_secondary_href": "/guider/",
        "crumbs": [("Start", "/"), ("Vanliga frågor", "/vanliga-fragor")],
    },
    "en": {
        "out": "en/faq.html", "url": "/en/faq", "alt": "/vanliga-fragor", "lang": "en", "locale": "en_GB",
        "title": "Frånvarokollen FAQ – GDPR, sign-in, timetabling systems",
        "description": "Answers to the questions schools ask most about Frånvarokollen: what the system does, where data is stored, how staff sign in and how to get started.",
        "eyebrow": "FREQUENTLY ASKED QUESTIONS", "h1": "Questions schools often ask us",
        "lead": f"Short, plain answers about what {FK} is, how it works and what applies to data and sign-in. Missing something? Email <a href=\"mailto:info@franvarokollen.com\">info@franvarokollen.com</a>.",
        "back": "Back to homepage", "back_href": "/en/",
        "cta_eyebrow": "GET STARTED", "cta_title": f"Want to see how {FK} would work at your school?",
        "cta_text": "In autumn 2026 we are inviting 15 partner schools to shape the tool together with us.",
        "cta_primary": "Apply for a partner place", "cta_primary_href": "/en/partner-schools",
        "cta_secondary": "Read our guides (Swedish)", "cta_secondary_href": "/guider/",
        "crumbs": [("Home", "/en/"), ("FAQ", "/en/faq")],
    },
}

CSS = """
  .faq-wrap{max-width:820px;margin:0 auto;padding:60px 24px 100px}
  .faq-wrap .eyebrow{margin-bottom:14px}
  .faq-wrap h1{font-size:clamp(30px,5vw,44px);color:var(--navy);margin:0 0 14px;line-height:1.12}
  .faq-wrap .lead{font-size:18px;line-height:1.6;color:var(--muted);margin:0 0 44px;max-width:640px}
  .faq-wrap .lead a,.faq-a a{color:var(--blue);font-weight:600;text-decoration:underline}
  .faq-list{border-top:1px solid var(--line)}
  .faq-item{border-bottom:1px solid var(--line)}
  .faq-item summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:22px 4px;font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:18px;color:var(--navy);line-height:1.3}
  .faq-item summary::-webkit-details-marker{display:none}
  .faq-item summary:hover{color:var(--blue)}
  .faq-item summary svg{width:22px;height:22px;flex:none;color:var(--blue);transition:transform .2s ease}
  .faq-item[open] summary svg{transform:rotate(180deg)}
  .faq-a{padding:0 4px 24px;color:var(--ink);font-size:16px;line-height:1.7;max-width:720px}
  .faq-a p{margin:0}
  .faq-cta{margin-top:64px;padding:40px;background:var(--white);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow-sm);text-align:center}
  .faq-cta .eyebrow{justify-content:center}
  .faq-cta h2{font-size:26px;color:var(--navy);margin:8px 0 10px}
  .faq-cta p{color:var(--muted);margin:0 0 24px}
  .faq-cta .hero-ctas{justify-content:center}
  @media(max-width:640px){.faq-wrap{padding:40px 20px 72px}.faq-item summary{font-size:16px;padding:18px 0}.faq-cta{padding:28px 20px}}
"""


def shell():
    src = open(os.path.join(ROOT, "om-oss.html"), encoding="utf-8").read()
    head = src[: src.index("<body>")]
    nav = src[src.index('<header class="nav">'): src.index("</header>") + len("</header>")]
    footer = src[src.index('<footer class="footer">'):]
    head = re.sub(r"<title>.*?</title>\n", "", head, flags=re.S)
    head = re.sub(r'<meta name="description"[^>]*>\n', "", head)
    head = re.sub(r'<link rel="canonical"[^>]*>\n', "", head)
    head = re.sub(r'<link rel="alternate"[^>]*>\n', "", head)
    head = re.sub(r'<meta (?:property|name)="(?:og|twitter):[^"]*"[^>]*>\n', "", head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", head, flags=re.S)
    head = head.replace("</style>", CSS + "</style>", 1)
    return head, nav, footer


def plain(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t))


def build(lang, cfg, faq, head, nav, footer, en_dict):
    q = html.escape
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "FAQPage", "@id": f"{SITE}{cfg['url']}#faq", "url": f"{SITE}{cfg['url']}", "name": cfg["title"],
         "inLanguage": "sv-SE" if lang == "sv" else "en", "isPartOf": {"@id": f"{SITE}/#website"},
         "about": {"@id": f"{SITE}/#software"},
         "mainEntity": [{"@type": "Question", "name": qq, "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for qq, a in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(cfg["crumbs"])]}]}
    sv_url, en_url = (cfg["url"], cfg["alt"]) if lang == "sv" else (cfg["alt"], cfg["url"])
    meta = f"""<title>{q(cfg['title'])}</title>
<meta name="description" content="{q(cfg['description'], True)}" />
<link rel="canonical" href="{SITE}{cfg['url']}" />
<link rel="alternate" hreflang="sv" href="{SITE}{sv_url}" />
<link rel="alternate" hreflang="en" href="{SITE}{en_url}" />
<link rel="alternate" hreflang="x-default" href="{SITE}{sv_url}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Frånvarokollen" />
<meta property="og:locale" content="{cfg['locale']}" />
<meta property="og:title" content="{q(cfg['title'], True)}" />
<meta property="og:description" content="{q(cfg['description'], True)}" />
<meta property="og:url" content="{SITE}{cfg['url']}" />
<meta property="og:image" content="{SITE}/hero-poster.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{q(cfg['title'], True)}" />
<meta name="twitter:description" content="{q(cfg['description'], True)}" />
<meta name="twitter:image" content="{SITE}/hero-poster.jpg" />
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
"""
    h = head.replace('<link rel="icon" href="/favicon.png"', meta + '<link rel="icon" href="/favicon.png"', 1)
    if lang == "en":
        h = h.replace('<html lang="sv">', '<html lang="en">', 1)
    items = "".join(f"""
    <details class="faq-item"{' open' if i == 0 else ''}>
      <summary><span>{qq}</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></summary>
      <div class="faq-a"><p>{a}</p></div>
    </details>""" for i, (qq, a) in enumerate(faq))
    body = f"""<main class="faq-wrap">
  <a href="{cfg['back_href']}" class="back-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>{cfg['back']}</a>
  <p class="eyebrow">{cfg['eyebrow']}</p>
  <h1>{cfg['h1']}</h1>
  <p class="lead">{cfg['lead']}</p>
  <div class="faq-list">{items}
  </div>
  <div class="faq-cta">
    <p class="eyebrow">{cfg['cta_eyebrow']}</p>
    <h2>{cfg['cta_title']}</h2>
    <p>{cfg['cta_text']}</p>
    <div class="hero-ctas">
      <a class="btn btn-red" href="{cfg['cta_primary_href']}">{cfg['cta_primary']} →</a>
      <a class="btn btn-secondary" href="{cfg['cta_secondary_href']}">{cfg['cta_secondary']}</a>
    </div>
  </div>
</main>
"""
    page = h + "<body>\n" + nav + "\n" + body + "\n" + footer
    if lang == "en":
        # nav/footer strings + links, same as build-en.py does for the other pages
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_en", os.path.join(ROOT, "tools", "build-en.py"))
        be = importlib.util.module_from_spec(spec); spec.loader.exec_module(be)
        page = be.apply_i18n(page, en_dict)
        page = be.strip_lang(page, "sv")
        page = be.activate_lang(page, "en")
        for a, b in be.LINK_MAP.items():
            page = page.replace(a, b)
        page = page.replace('href="/en/faq"', f'href="{cfg["url"]}"')
        page = page.replace('data-lang-btn="sv" aria-pressed="true"', 'data-lang-btn="sv" data-lang-href="/vanliga-fragor" aria-pressed="false"')
        page = page.replace('class="active" data-lang-btn="sv"', 'data-lang-btn="sv"')
        page = re.sub(r'<button data-lang-btn="en"[^>]*>', '<button class="active" data-lang-btn="en" aria-pressed="true">', page)
    else:
        page = re.sub(r'<button data-lang-btn="en"[^>]*>', '<button data-lang-btn="en" data-lang-href="/en/faq" aria-pressed="false">', page)
    return page


def main():
    faq = json.load(open(os.path.join(ROOT, "tools", "faq.json"), encoding="utf-8"))
    head, nav, footer = shell()
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_en", os.path.join(ROOT, "tools", "build-en.py"))
    be = importlib.util.module_from_spec(spec); spec.loader.exec_module(be)
    en_dict = be.translations(open(os.path.join(ROOT, "index.html"), encoding="utf-8").read())["en"]
    for lang, cfg in PAGES.items():
        out = os.path.join(ROOT, cfg["out"])
        open(out, "w", encoding="utf-8").write(build(lang, cfg, faq[lang], head, nav, footer, en_dict))
        print(cfg["url"])


if __name__ == "__main__":
    main()
