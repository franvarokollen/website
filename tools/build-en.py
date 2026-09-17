#!/usr/bin/env python3
"""
build-en.py — generates the server-rendered English pages under /en/ from the
Swedish source pages, so Google can index the English content on its own URLs
(with hreflang), instead of only seeing the client-side language toggle.

Run after editing index.html, om-oss.html or bli-partnerskola.html:

    python3 tools/build-en.py

Outputs (committed to the repo, Cloudflare Pages serves them as static files):
    en/index.html             ← index.html
    en/about.html             ← om-oss.html
    en/partner-schools.html   ← bli-partnerskola.html

What it does per page:
  - applies translations.en to every [data-i18n] element (same dictionary the
    toggle uses at runtime, so nothing is translated twice)
  - keeps only the [data-lang="en"] blocks (and strips the sv ones)
  - sets <html lang="en">, English <title>/description/canonical/OG/Twitter
  - rewrites internal links to the English counterparts
  - swaps the JSON-LD for English variants
The Swedish source pages are also touched: they get hreflang links and the EN
toggle button is pointed at the /en/ URL. Their hidden [data-lang="en"] blocks
are left in place so the source stays editable and the build is re-runnable.

Requires node (to evaluate the JS translations object) — no npm packages.
"""
import json, os, re, subprocess, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://franvarokollen.com"

PAGES = {
    "index.html": {
        "out": "en/index.html",
        "sv_url": "/", "en_url": "/en/",
        "title": "Frånvarokollen – Absence and substitute management for schools",
        "description": "Frånvarokollen helps cover coordinators and principals handle staff absence, find substitutes and keep track of staffing and costs – in one system. Built in Sweden, data stored in the EU, GDPR-compliant.",
        "og_description": "Handle absence, find substitutes and keep track of staffing and costs – in one system. Built in Sweden, data stored in the EU.",
    },
    "om-oss.html": {
        "out": "en/about.html",
        "sv_url": "/om-oss", "en_url": "/en/about",
        "title": "About us – Frånvarokollen | Why we built a substitute system for schools",
        "description": "Frånvarokollen Sverige AB was founded by people who have worked in schools themselves. CEO Ibrahim Amdaouech on why we built a system for absence, substitutes and staffing.",
        "og_description": "Behind every gap in the schedule is a pupil's school day. CEO Ibrahim Amdaouech on why we built Frånvarokollen.",
    },
    "bli-partnerskola.html": {
        "out": "en/partner-schools.html",
        "sv_url": "/bli-partnerskola", "en_url": "/en/partner-schools",
        "title": "Partnerplatsen – become a partner school | Frånvarokollen",
        "description": "We are inviting 15 schools to build Frånvarokollen together with us – as partner schools, not just customers. Open to schools across Sweden.",
        "og_description": "15 places. Open to schools across Sweden. Shape Frånvarokollen from the inside.",
    },
}

LINK_MAP = {
    'href="/"': 'href="/en/"',
    'href="/om-oss"': 'href="/en/about"',
    'href="/bli-partnerskola"': 'href="/en/partner-schools"',
    'href="/anvandarvillkor"': 'href="/terms"',
    'href="/vanliga-fragor"': 'href="/en/faq"',
}

VOID = {"img", "br", "hr", "input", "meta", "link", "source", "path", "circle", "rect", "line", "polyline"}
TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9-]*)\b[^>]*?(/?)>", re.S)


def element_span(s, start):
    """Return (open_end, close_start, close_end) for the element whose opening
    tag begins at s[start]. Handles nesting of the same tag name."""
    m = TAG_RE.match(s, start)
    assert m and not m.group(1), s[start:start + 60]
    name = m.group(2)
    depth = 1
    pos = m.end()
    for t in TAG_RE.finditer(s, pos):
        if t.group(2) != name or t.group(3) == "/" or name in VOID:
            continue
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return m.end(), t.start(), t.end()
    raise ValueError(f"unclosed <{name}> at {start}")


def translations(src):
    m = re.search(r"const translations = (\{[\s\S]*?\n  \});", src)
    if not m:  # page has no dictionary of its own (om-oss) → use the homepage's
        m = re.search(r"const translations = (\{[\s\S]*?\n  \});", open(os.path.join(ROOT, "index.html"), encoding="utf-8").read())
    js = f"const t={m.group(1)};process.stdout.write(JSON.stringify(t))"
    return json.loads(subprocess.check_output(["node", "-e", js]))


def apply_i18n(s, d):
    out, i = [], 0
    for m in re.finditer(r'<[a-zA-Z][a-zA-Z0-9-]*\b[^>]*\bdata-i18n="([^"]+)"[^>]*>', s):
        key = m.group(1)
        if m.start() < i or key not in d:
            continue
        open_end, close_start, close_end = element_span(s, m.start())
        out.append(s[i:open_end]); out.append(d[key]); i = close_start
    out.append(s[i:])
    return "".join(out)


def strip_lang(s, lang):
    """Remove every element carrying data-lang="<lang>"."""
    while True:
        m = re.search(r'<[a-zA-Z][a-zA-Z0-9-]*\b[^>]*\bdata-lang="%s"[^>]*>' % lang, s)
        if not m:
            return s
        _, _, close_end = element_span(s, m.start())
        # eat one trailing newline so the source stays tidy
        end = close_end + (1 if s[close_end:close_end + 1] == "\n" else 0)
        s = s[:m.start()] + s[end:]


def activate_lang(s, lang):
    return re.sub(r'(<[a-zA-Z][a-zA-Z0-9-]*\b[^>]*\bdata-lang="%s")(?![^>]*\bclass=)' % lang,
                  r'\1 class="active"', s)


def hreflang(cfg):
    return (f'<link rel="alternate" hreflang="sv" href="{SITE}{cfg["sv_url"]}" />\n'
            f'<link rel="alternate" hreflang="en" href="{SITE}{cfg["en_url"]}" />\n'
            f'<link rel="alternate" hreflang="x-default" href="{SITE}{cfg["sv_url"]}" />')


def plain(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t))


def build_en(src_name, cfg, src):
    d = translations(src)["en"]
    s = apply_i18n(src, d)
    s = strip_lang(s, "sv")
    s = activate_lang(s, "en")
    s = s.replace('<html lang="sv">', '<html lang="en">', 1)
    # the EN blocks carry an <h2> in the source (so the SV page has one h1); promote it here
    s = s.replace('<h2 class="vd-headline">', '<h1 class="vd-headline">').replace('</h2>', '</h1>', 1) if '<h2 class="vd-headline">' in s else s
    s = s.replace('<h2 class="pk-title">Partnerplatsen</h2>', '<h1>Partnerplatsen</h1>')

    # ---- head ----
    s = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*"\s*/>', f'<meta name="description" content="{cfg["description"]}" />', s, count=1)
    s = re.sub(r'<link rel="canonical" href="[^"]*" />', f'<link rel="canonical" href="{SITE}{cfg["en_url"]}" />\n{hreflang(cfg)}', s, count=1)
    s = s.replace('<meta property="og:locale" content="sv_SE" />', '<meta property="og:locale" content="en_GB" />')
    s = s.replace('<meta property="og:locale:alternate" content="en_GB" />', '<meta property="og:locale:alternate" content="sv_SE" />')
    for prop in ("og:title", "twitter:title"):
        s = re.sub(rf'(<meta (?:property|name)="{prop}" content=")[^"]*(")', rf'\g<1>{cfg["title"]}\2', s, count=1)
    for prop in ("og:description", "twitter:description"):
        s = re.sub(rf'(<meta (?:property|name)="{prop}" content=")[^"]*(")', rf'\g<1>{cfg["og_description"]}\2', s, count=1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf'\g<1>{SITE}{cfg["en_url"]}\2', s, count=1)

    # ---- JSON-LD ----
    if src_name == "index.html":
        s = s.replace('"@id": "https://franvarokollen.com/#webpage",\n      "url": "https://franvarokollen.com/",\n      "name": "Frånvarokollen – Frånvarohantering och vikariehantering för skolor",',
                      f'"@id": "{SITE}/en/#webpage",\n      "url": "{SITE}/en/",\n      "name": "{cfg["title"]}",')
        s = s.replace('"about": { "@id": "https://franvarokollen.com/#software" },\n      "inLanguage": "sv-SE"',
                      '"about": { "@id": "https://franvarokollen.com/#software" },\n      "inLanguage": "en"')
    else:
        s = s.replace(f'"@id": "{SITE}{cfg["sv_url"]}#webpage",\n      "url": "{SITE}{cfg["sv_url"]}",',
                      f'"@id": "{SITE}{cfg["en_url"]}#webpage",\n      "url": "{SITE}{cfg["en_url"]}",')
        s = re.sub(r'("name": ")[^"]*(",\n      "inLanguage": ")sv-SE(")', rf'\g<1>{cfg["title"]}\2en\3', s, count=1)
        s = s.replace('"name": "Start", "item": "https://franvarokollen.com/"', '"name": "Home", "item": "https://franvarokollen.com/en/"')
        s = s.replace('"name": "Om oss", "item": "https://franvarokollen.com/om-oss"', '"name": "About us", "item": "https://franvarokollen.com/en/about"')
        s = s.replace('"name": "Partnerplatsen", "item": "https://franvarokollen.com/bli-partnerskola"', '"name": "Partnerplatsen", "item": "https://franvarokollen.com/en/partner-schools"')

    # ---- links ----
    for a, b in LINK_MAP.items():
        s = s.replace(a, b)
    # language toggle: SV goes to the Swedish URL, EN is the current page
    s = s.replace('data-lang-btn="sv" aria-pressed="true"', f'data-lang-btn="sv" data-lang-href="{cfg["sv_url"]}" aria-pressed="false"')
    s = s.replace('class="active" data-lang-btn="sv"', 'data-lang-btn="sv"')
    s = s.replace('<button data-lang-btn="en" aria-pressed="false">', '<button class="active" data-lang-btn="en" aria-pressed="true">')
    s = s.replace('<button data-lang-btn="en" data-lang-href=', '<button class="active" data-lang-btn="en" data-lang-href=')
    s = re.sub(r'data-lang-btn="en" data-lang-href="[^"]*" aria-pressed="false"', 'data-lang-btn="en" aria-pressed="true"', s)
    return s


def prep_sv(cfg, src):
    """Swedish source page: hreflang + toggle navigates to /en/ + drop EN blocks."""
    s = src
    if 'hreflang="en"' not in s:
        s = re.sub(r'(<link rel="canonical" href="[^"]*" />)', lambda m: m.group(1) + "\n" + hreflang(cfg), s, count=1)
    s = re.sub(r'<button data-lang-btn="en"( data-lang-href="[^"]*")? aria-pressed="false">',
               f'<button data-lang-btn="en" data-lang-href="{cfg["en_url"]}" aria-pressed="false">', s)
    return s


def main():
    os.makedirs(os.path.join(ROOT, "en"), exist_ok=True)
    for name, cfg in PAGES.items():
        path = os.path.join(ROOT, name)
        src = open(path, encoding="utf-8").read()
        sv = prep_sv(cfg, src)
        if sv != src:
            open(path, "w", encoding="utf-8").write(sv)
        en = build_en(name, cfg, src)
        out = os.path.join(ROOT, cfg["out"])
        open(out, "w", encoding="utf-8").write(en)
        print(f"{name} → {cfg['out']} ({len(en)//1024} KB)")


if __name__ == "__main__":
    main()
