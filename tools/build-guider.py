#!/usr/bin/env python3
"""
build-guider.py — renders the Swedish guide articles under /guider/ using the
site shell (head, CSS, nav, footer) from om-oss.html, so they always match the
design without a copy of the CSS in every file.

Add an article: append a dict to ARTICLES below (body is HTML), then run

    python3 tools/build-guider.py

and add the new URL to sitemap.xml. Outputs guider/index.html + one file per slug.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://franvarokollen.com"
FK = '<span translate=no class=notranslate>Frånvarokollen</span>'

ARTICLES = [
    {
        "slug": "vad-kostar-en-vikarie",
        "title": "Vad kostar en vikarie? Så räknar du på skolans vikariekostnader",
        "h1": "Vad kostar en vikarie egentligen?",
        "description": "Timlön, arbetsgivaravgift, semesterersättning och bemanningsföretagets påslag – så räknar du ut vad en vikarie kostar skolan, och vad intern täckning kostar i stället.",
        "eyebrow": "GUIDE · EKONOMI",
        "date": "2026-09-17",
        "read": "6 min",
        "body": f"""
<p class="lead">Frågan låter enkel, men de flesta skolor har inte ett svar. Kostnaden för vikarier ligger utspridd på flera konton, en del av den syns aldrig i budgeten och den största posten – tid – bokförs inte alls. Här är en modell för att räkna på det.</p>

<h2>Tre sorters kostnad</h2>
<p>När en lärare är frånvarande täcks lektionen på ett av tre sätt, och de kostar olika:</p>
<ol>
  <li><strong>Extern vikarie</strong> – timanställd eller via bemanningsföretag. Syns tydligt på fakturan.</li>
  <li><strong>Intern täckning</strong> – en kollega tar lektionen på håltimme, planeringstid eller som övertid. Syns sällan, men kostar.</li>
  <li><strong>Ingen täckning</strong> – eleverna får självstudier, slås ihop med en annan klass eller skickas hem. Kostar ingenting i kronor, men i undervisningstid.</li>
</ol>

<h2>1. Extern vikarie: räkna hela vägen</h2>
<p>Timlönen är bara början. För en timanställd vikarie tillkommer:</p>
<ul>
  <li><strong>Arbetsgivaravgift</strong> – 31,42 % på lönen (2026 års nivå för de flesta anställda).</li>
  <li><strong>Semesterersättning</strong> – minst 12 % enligt semesterlagen, ofta mer enligt kollektivavtal.</li>
  <li><strong>Administration</strong> – anställningsavtal, tidrapport, lönekörning, introduktion. Räkna med 20–30 minuter per uppdrag för den som administrerar.</li>
</ul>
<p>Ett räkneexempel: en vikarie med 180 kr i timlön kostar skolan cirka <strong>180 × 1,12 × 1,3142 ≈ 265 kr per timme</strong> innan administration. Går uppdraget via bemanningsföretag ligger timpriset i stället på en fast nivå som redan inkluderar avgifterna plus företagets påslag – vanligtvis betydligt över det egna timpriset, i utbyte mot att någon annan hittar personen.</p>

<h2>2. Intern täckning: den osynliga kostnaden</h2>
<p>När en kollega tar lektionen sparar skolan fakturan, men tre saker händer:</p>
<ul>
  <li><strong>Planeringstid försvinner.</strong> Lektionen som skulle förberetts förbereds sämre, eller på kvällen.</li>
  <li><strong>Belastningen fördelas ojämnt.</strong> Det är ofta samma personer som säger ja – de som sitter nära expeditionen eller har luckor i schemat. Efter en termin syns det i sjuktalen.</li>
  <li><strong>Övertid uppstår.</strong> Enligt HÖK 21 ska övertid ersättas eller kompenseras – och om den inte registreras blir den en dold skuld.</li>
</ul>
<p>Ett rimligt sätt att sätta pris på intern täckning är att utgå från lärarens egen timkostnad (månadslön × 1,4 för avgifter och semester, delat på cirka 165 timmar). För en lärare med 38 000 kr i månadslön blir det runt <strong>320 kr per timme</strong> – ofta mer än en extern vikarie, men utan fakturan som gör kostnaden synlig.</p>

<h2>3. Hur många lektioner handlar det om?</h2>
<p>För att gå från timpris till årskostnad behöver ni en uppskattning av volymen. Nationella riktvärden:</p>
<ul>
  <li>Lärare har i snitt omkring <strong>16 frånvarodagar per år</strong> (SCB 2022, Skandia 2025).</li>
  <li>En lärare undervisar i snitt <strong>3,4 lektioner per dag</strong> (Sveriges Lärare 2023).</li>
  <li>Ett läsår har omkring <strong>200 skoldagar</strong>.</li>
</ul>
<p>För en skola med 40 lärare ger det <strong>40 × 16 × 3,4 ≈ 2 200 lektioner per år</strong> som måste täckas på något sätt – i praktiken 11 lektioner per skoldag. Byt ut riktvärdena mot era egna siffror från lönesystemet om ni har dem; frånvaron varierar mycket mellan skolor.</p>

<h2>Sätt ihop det</h2>
<table>
  <tr><th>Post</th><th>Så räknar du</th><th>Exempel, 40 lärare</th></tr>
  <tr><td>Lektioner att täcka per år</td><td>lärare × frånvarodagar × lektioner/dag</td><td>≈ 2 200</td></tr>
  <tr><td>Andel extern täckning</td><td>er uppskattning (ofta 30–60 %)</td><td>40 % → 880 lektioner</td></tr>
  <tr><td>Kostnad extern</td><td>lektioner × timpris inkl. avgifter</td><td>880 × 265 kr ≈ 233 000 kr</td></tr>
  <tr><td>Kostnad intern</td><td>lektioner × lärarens timkostnad</td><td>1 320 × 320 kr ≈ 422 000 kr</td></tr>
  <tr><td><strong>Total vikariekostnad</strong></td><td></td><td><strong>≈ 655 000 kr/år</strong></td></tr>
</table>
<p>Exemplet är just ett exempel – poängen är att den interna delen, som aldrig syns på en faktura, ofta är den största. Det är också den som går att påverka mest: rätt person på rätt lucka, fördelat jämnt, i stället för samma tre kollegor varje gång.</p>

<h2>Vad kan ni göra med siffran?</h2>
<ul>
  <li><strong>Budgetera på riktigt.</strong> Lägg intern täckning som en synlig post, så att diskussionen om vikariepool eller extra resurs kan föras med siffror.</li>
  <li><strong>Följ upp per månad.</strong> Vilka veckor, ämnen och arbetslag drar mest? Mönstren är ofta tydliga när man väl mäter.</li>
  <li><strong>Fördela jämnare.</strong> Om belastningen syns kan den styras. Det är också ett arbetsmiljöargument, inte bara ett ekonomiskt.</li>
</ul>
<p>{FK} gör exakt den här uppföljningen automatiskt – varje täckt lektion loggas som intern eller extern, och rektor får kostnad, belastning och mönster i en översikt. <a href="/bli-partnerskola">Läs mer om hur ni blir partnerskola</a>.</p>
""",
    },
    {
        "slug": "bemanning-vid-sjukfranvaro",
        "title": "Sjukanmälan klockan 06.43 – checklista för bemanning vid sjukfrånvaro",
        "h1": "Sjukanmälan 06.43: så täcker ni dagen utan kaos",
        "description": "En praktisk checklista för vikariesamordnare och rektorer: vad som ska hända från att sjukanmälan kommer in tills alla lektioner är täckta – och hur ni bygger en rutin som håller.",
        "eyebrow": "GUIDE · RUTINER",
        "date": "2026-09-17",
        "read": "5 min",
        "body": f"""
<p class="lead">De flesta skolor löser morgonen. Frågan är till vilket pris – i samtal, i stress och i lektioner som blir självstudier. Här är rutinen vi ser fungera bäst, steg för steg.</p>

<h2>Innan det händer: förberedelser som gör morgonen kort</h2>
<ul>
  <li><strong>En kanal för sjukanmälan.</strong> Inte sms till rektor, mejl till expeditionen och ett samtal till arbetslaget. En väg in, som samordnaren ser direkt.</li>
  <li><strong>Aktuella scheman.</strong> Samordnaren måste kunna se vilka lektioner den frånvarande läraren har i dag, och vilka kollegor som har lucka samtidigt. Om det kräver tre system tar det tio minuter per lärare.</li>
  <li><strong>En vikarielista som är sann.</strong> Timvikarier med aktuella telefonnummer, vilka stadier och ämnen de klarar, och när de senast jobbade. Listan som senast uppdaterades i augusti är värdelös i november.</li>
  <li><strong>Tydlig prioritering.</strong> Vilka lektioner täcks alltid (lågstadiet, praktiska ämnen, NP-veckor)? Vilka kan bli självstudier om det krisar? Bestäm det i lugn och ro, inte 06.45.</li>
  <li><strong>En reservplan för lärarens material.</strong> Delad mapp eller vikariepärm per klass, så att en vikarie kan hålla lektionen även om läraren är för sjuk för att skicka planering.</li>
</ul>

<h2>Morgonen: sju steg</h2>
<ol>
  <li><strong>Bekräfta frånvaron</strong> och notera omfattning – hela dagen, flera dagar, tills vidare?</li>
  <li><strong>Lista dagens lektioner</strong> för den frånvarande läraren: tid, klass, sal, ämne.</li>
  <li><strong>Sortera efter prioritet.</strong> Vilka måste täckas av en vuxen i rummet, vilka kan lösas annorlunda?</li>
  <li><strong>Sök intern täckning först</strong> – kollegor med lucka som har rätt behörighet eller känner klassen. Titta på vem som täckt mest den senaste tiden och sprid uppdragen.</li>
  <li><strong>Ring externa vikarier</strong> för det som återstår, i den ordning ni bestämt (kända vikarier före nya, egna före bemanningsföretag).</li>
  <li><strong>Meddela alla berörda</strong> – vikarien, klassen/mentorn, expeditionen och den frånvarande läraren om vad som är löst.</li>
  <li><strong>Logga vad som gjordes.</strong> Vem täckte vad, internt eller externt. Det tar en minut nu och sparar timmar vid löneunderlag och uppföljning.</li>
</ol>

<h2>Under dagen</h2>
<ul>
  <li>Se till att vikarien vet var material, närvarolista och kontaktperson finns.</li>
  <li>Följ upp de lektioner som blev självstudier – vad behöver tas igen?</li>
  <li>Om frånvaron förlängs: börja planera morgondagen före klockan 14, när kollegor och vikarier fortfarande går att nå.</li>
</ul>

<h2>Efteråt: det som skiljer en rutin från en räddningsaktion</h2>
<p>Skolor som slutar släcka bränder gör en sak till – de tittar på mönstren. Varje månad:</p>
<ul>
  <li>Hur många lektioner täcktes, och hur stor andel blev självstudier?</li>
  <li>Vilka kollegor har täckt mest? Är det rimligt, eller är det samma tre personer varje gång?</li>
  <li>Vilka veckodagar och ämnen är svårast att täcka? Kan vikarielistan förstärkas där?</li>
  <li>Vad kostade det – externt och internt? (<a href="/guider/vad-kostar-en-vikarie">Så räknar du</a>.)</li>
</ul>

<h2>Vanliga fallgropar</h2>
<ul>
  <li><strong>Kunskapen sitter i en person.</strong> När samordnaren själv är sjuk står skolan still. Rutinen och listorna måste finnas utanför hens huvud.</li>
  <li><strong>Övertid som inte registreras.</strong> Kollegor som täcker på planeringstid ska ha ersättning eller kompensation enligt avtal. Ologgad täckning är en arbetsmiljörisk.</li>
  <li><strong>Att alltid ringa den som säger ja.</strong> Effektivt i stunden, dyrt på sikt.</li>
</ul>
<p>Mycket av ovanstående går att göra i ett kalkylark och en telefonlista. {FK} är byggt för att göra det på några minuter i stället för en timme: frånvaron registreras, dagens luckor visas, kollegor med lucka och rätt behörighet föreslås – rankade efter hur mycket de täckt nyligen – och allt loggas automatiskt. <a href="/">Se hur det fungerar</a>.</p>
""",
    },
    {
        "slug": "vikariehantering-system-eller-telefonlista",
        "title": "Vikariehantering: telefonlista, kalkylark eller system? Så väljer ni",
        "h1": "Vikariehantering: när räcker telefonlistan – och när behövs ett system?",
        "description": "Vad ett vikariesystem faktiskt ska lösa, vilka frågor ni bör ställa innan ni väljer, och när telefonlistan och kalkylarket fortfarande är rätt verktyg.",
        "eyebrow": "GUIDE · VERKTYG",
        "date": "2026-09-17",
        "read": "5 min",
        "body": f"""
<p class="lead">Nästan alla skolor hanterar vikarier på samma sätt: ett kalkylark med tillgängliga personer, en telefonlista och en samordnare som ringer. Det fungerar – tills det inte gör det. Här är hur ni avgör var ni står.</p>

<h2>Tre tecken på att telefonlistan räcker</h2>
<ul>
  <li>Ni har färre än cirka 20 lärare och en samordnare som känner alla.</li>
  <li>Frånvaron är låg och ojämnt fördelad – enstaka dagar, inte varje morgon.</li>
  <li>Ingen frågar efter uppföljning. Rektor behöver inte veta vad täckningen kostar eller vem som bär den.</li>
</ul>
<p>I det läget är ett system mest administration. Lägg tiden på att hålla listan uppdaterad i stället.</p>

<h2>Tre tecken på att ni har växt ur den</h2>
<ul>
  <li><strong>Morgonen tar mer än 30 minuter.</strong> Samordnaren hoppar mellan schemasystem, personallista och telefon – och gör det varje dag.</li>
  <li><strong>Samma kollegor täcker alltid.</strong> Ingen vet exakt hur mycket, förrän någon säger upp sig eller blir sjukskriven.</li>
  <li><strong>Ingen kan svara på vad det kostar.</strong> Fakturorna från bemanningsföretaget finns, men den interna täckningen är osynlig. (<a href="/guider/vad-kostar-en-vikarie">Så räknar ni ut den.</a>)</li>
</ul>

<h2>Vad ett vikariesystem ska lösa – och inte</h2>
<p>Ett bra system gör tre saker: <strong>samlar</strong> frånvaro, scheman och tillgänglig personal på ett ställe, <strong>föreslår</strong> vem som kan täcka utifrån schema, behörighet och belastning, och <strong>loggar</strong> vad som gjordes så att uppföljningen sköter sig själv.</p>
<p>Det ska däremot inte fatta beslutet åt er. Vem som ska stå i ett klassrum är en bedömning som kräver kännedom om klassen, kollegan och dagen. Var skeptisk till verktyg som lovar att "automatisera bemanningen" – det som behövs är ett bättre underlag, inte en algoritm som bestämmer.</p>

<h2>Frågor att ställa innan ni väljer</h2>
<ol>
  <li><strong>Var lagras uppgifterna?</strong> Personaluppgifter och frånvaro är personuppgifter. Kräv lagring inom EU och ett personuppgiftsbiträdesavtal. Fråga vad som händes om leverantören försvinner.</li>
  <li><strong>Hur loggar personalen in?</strong> Nya lösenord används inte. Inloggning med skolans befintliga Google- eller Microsoft-konton är i praktiken ett krav.</li>
  <li><strong>Måste vi byta schemasystem?</strong> Nej borde vara svaret. Systemet ska komplettera det ni har, inte ersätta det.</li>
  <li><strong>Vad ser rektor?</strong> Om svaret är "en exportfil" är uppföljningen inte löst. Belastning per person, andel intern/extern täckning och kostnad per månad ska finnas färdigt.</li>
  <li><strong>Hur lång tid tar det att komma igång?</strong> En skola ska kunna vara igång på dagar, inte terminer. Kräv att få prova med er egen personal och ert eget schema.</li>
  <li><strong>Vad händer i kommunen?</strong> Om ni är en kommunal skola: kan huvudmannen se över flera enheter, och kan vikarier delas mellan skolor?</li>
  <li><strong>Vem har byggt det?</strong> Verktyg byggda av personer som själva stått i skolans morgon ser annorlunda ut än verktyg byggda för HR i allmänhet.</li>
</ol>

<h2>Tre varianter i praktiken</h2>
<table>
  <tr><th></th><th>Telefonlista + kalkylark</th><th>Modul i befintligt system</th><th>Fristående vikariesystem</th></tr>
  <tr><td>Kostnad</td><td>Ingen licens, mycket tid</td><td>Ofta tillägg till befintlig licens</td><td>Egen licens, oftast per skola</td></tr>
  <tr><td>Överblick i realtid</td><td>Nej</td><td>Delvis</td><td>Ja</td></tr>
  <tr><td>Förslag på vem som kan täcka</td><td>Samordnarens huvud</td><td>Sällan</td><td>Ja, utifrån schema och belastning</td></tr>
  <tr><td>Uppföljning av kostnad och belastning</td><td>Manuellt, om alls</td><td>Begränsat</td><td>Inbyggt</td></tr>
  <tr><td>Beroende av en person</td><td>Högt</td><td>Medel</td><td>Lågt</td></tr>
</table>

<h2>Vår rekommendation</h2>
<p>Börja med att mäta en månad: hur många lektioner täcktes, av vem, och hur lång tid tog morgonen? Om siffrorna gör er obekväma har ni ert svar. {FK} är ett fristående vikariesystem byggt av personer som arbetat i svensk skola, med data inom EU, inloggning via Google och Microsoft och en uppföljning som rektor faktiskt kan använda. Under hösten 2026 bjuder vi in 15 skolor som <a href="/bli-partnerskola">partnerskolor</a> – ett sätt att prova på riktigt, med er egen personal, och påverka hur verktyget utvecklas.</p>
""",
    },
]

HUB = {
    "title": "Guider för vikariesamordnare och rektorer – Frånvarokollen",
    "h1": "Guider",
    "description": "Praktiska guider om frånvaro, vikarier och bemanning i svensk skola: vad en vikarie kostar, rutiner vid sjukfrånvaro och hur ni väljer vikariesystem.",
}


def shell():
    src = open(os.path.join(ROOT, "om-oss.html"), encoding="utf-8").read()
    head = src[: src.index("<body>")]
    nav = src[src.index("<header class=\"nav\">"): src.index("</header>") + len("</header>")]
    footer = src[src.index("<footer class=\"footer\">"):]
    # head: strip page-specific metadata; we re-add it per article
    head = re.sub(r"<title>.*?</title>\n", "", head, flags=re.S)
    head = re.sub(r'<meta name="description"[^>]*>\n', "", head)
    head = re.sub(r'<link rel="canonical"[^>]*>\n', "", head)
    head = re.sub(r'<link rel="alternate"[^>]*>\n', "", head)
    head = re.sub(r'<meta (?:property|name)="(?:og|twitter):[^"]*"[^>]*>\n', "", head)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\n', "", head, flags=re.S)
    # guides are Swedish only: EN toggle goes to the English homepage
    nav = re.sub(r'<button data-lang-btn="en"[^>]*>', '<button data-lang-btn="en" data-lang-href="/en/" aria-pressed="false">', nav)
    # om-oss keeps hidden EN spans in the footer only via data-i18n; fine as-is
    return head, nav, footer


EXTRA_CSS = """
  .guide-meta{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:14px;margin:0 0 28px}
  .guide-meta .eyebrow{margin:0}
  .policy-wrap p.lead{font-size:19px;line-height:1.6;color:var(--navy);margin-bottom:28px}
  .policy-wrap a{color:var(--blue);font-weight:600;text-decoration:underline}
  .policy-wrap table{font-size:15px}
  .guide-list{display:grid;gap:20px;margin-top:36px}
  .guide-card{display:block;padding:28px;background:var(--white);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow-sm);text-decoration:none!important;transition:transform .15s,box-shadow .15s}
  .guide-card:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
  .guide-card h2{margin:6px 0 10px!important;padding:0!important;border:0!important;font-size:22px!important}
  .guide-card p{margin:0;color:var(--muted)}
  .guide-more{margin-top:56px;padding-top:32px;border-top:1px solid var(--line)}
  .guide-more h2{border:0!important;padding-top:0!important;margin-top:0!important}
  .guide-more ul{list-style:none;margin:0;padding:0}
"""


def meta(url, title, desc, ld):
    return f"""<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}" />
<link rel="canonical" href="{SITE}{url}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="Frånvarokollen" />
<meta property="og:locale" content="sv_SE" />
<meta property="og:title" content="{html.escape(title, quote=True)}" />
<meta property="og:description" content="{html.escape(desc, quote=True)}" />
<meta property="og:url" content="{SITE}{url}" />
<meta property="og:image" content="{SITE}/hero-poster.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{html.escape(title, quote=True)}" />
<meta name="twitter:description" content="{html.escape(desc, quote=True)}" />
<meta name="twitter:image" content="{SITE}/hero-poster.jpg" />
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
"""


def crumbs(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def render(head, nav, footer, url, title, desc, ld, body):
    h = head.replace("</style>", EXTRA_CSS + "</style>", 1)
    h = h.replace('<link rel="icon" href="/favicon.png"', meta(url, title, desc, ld) + '<link rel="icon" href="/favicon.png"', 1)
    return h + "<body>\n" + nav + "\n" + body + "\n" + footer


def main():
    head, nav, footer = shell()
    os.makedirs(os.path.join(ROOT, "guider"), exist_ok=True)
    for a in ARTICLES:
        url = f"/guider/{a['slug']}"
        others = [o for o in ARTICLES if o is not a]
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "Article", "@id": f"{SITE}{url}#article", "headline": a["title"], "description": a["description"],
             "inLanguage": "sv-SE", "datePublished": a["date"], "dateModified": a["date"],
             "mainEntityOfPage": f"{SITE}{url}", "image": f"{SITE}/hero-poster.jpg",
             "author": {"@id": f"{SITE}/#organization"}, "publisher": {"@id": f"{SITE}/#organization"},
             "isPartOf": {"@id": f"{SITE}/#website"}},
            crumbs([("Start", "/"), ("Guider", "/guider/"), (a["h1"], url)])]}
        body = f"""<main class="policy-wrap">
  <a href="/guider/" class="back-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>Alla guider</a>
  <article>
    <div class="guide-meta"><span class="eyebrow">{a['eyebrow']}</span><span>{a['read']} läsning</span><span>Uppdaterad <time datetime="{a['date']}">{a['date']}</time></span></div>
    <h1>{a['h1']}</h1>
{a['body']}
  </article>
  <aside class="guide-more">
    <h2>Fler guider</h2>
    <ul>{''.join(f'<li><a href="/guider/{o["slug"]}">{o["h1"]}</a></li>' for o in others)}</ul>
  </aside>
</main>
"""
        open(os.path.join(ROOT, "guider", a["slug"] + ".html"), "w", encoding="utf-8").write(
            render(head, nav, footer, url, a["title"], a["description"], ld, body))
        print(url)

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": f"{SITE}/guider/#webpage", "url": f"{SITE}/guider/", "name": HUB["title"],
         "description": HUB["description"], "inLanguage": "sv-SE", "isPartOf": {"@id": f"{SITE}/#website"}},
        crumbs([("Start", "/"), ("Guider", "/guider/")])]}
    cards = "".join(f"""
    <a class="guide-card" href="/guider/{a['slug']}">
      <span class="eyebrow">{a['eyebrow']}</span>
      <h2>{a['h1']}</h2>
      <p>{a['description']}</p>
    </a>""" for a in ARTICLES)
    body = f"""<main class="policy-wrap">
  <a href="/" class="back-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>Tillbaka till startsidan</a>
  <h1>{HUB['h1']}</h1>
  <p class="lead">Praktiska guider om frånvaro, vikarier och bemanning – skrivna för vikariesamordnare, rektorer och skolledare i svensk skola.</p>
  <div class="guide-list">{cards}
  </div>
</main>
"""
    open(os.path.join(ROOT, "guider", "index.html"), "w", encoding="utf-8").write(
        render(head, nav, footer, "/guider/", HUB["title"], HUB["description"], ld, body))
    print("/guider/")


if __name__ == "__main__":
    main()
