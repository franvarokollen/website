// ============================================================
// Frånvarokollen Marketing Site — Cloudflare Worker entry
// Routes /anvandarvillkor and /terms to SSR legal pages.
// Everything else passes through to static assets.
// ============================================================

// ▼ Change this one constant if the upstream URL ever moves.
// Portal endpoint is the query form (api/legal.js reads ?slug=), returning { doc: {...} }.
const LEGAL_API = "https://www.skolkollen.com/api/legal?slug=terms-of-service";

const CACHE_TTL = 3600; // 1 hour, used for both Cache-Control and the CF cache

// ── Tiny safe Markdown → HTML renderer ──────────────────────
// Covers: headings (#–####), paragraphs, unordered lists (- ),
// blockquotes (> ), bold (**…**), inline links ([text](url)).
// Source text is HTML-escaped before any pattern is applied.
function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderMarkdown(md) {
  // Normalise line endings
  const lines = md.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");

  const html = [];
  let inList = false;
  let inBlockquote = false;

  const closeList = () => { if (inList) { html.push("</ul>"); inList = false; } };
  const closeBlockquote = () => { if (inBlockquote) { html.push("</blockquote>"); inBlockquote = false; } };

  // Inline formatting applied after HTML escaping
  const inline = (raw) => {
    let s = escapeHtml(raw);
    // bold **…**
    s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    // inline link [text](url) — only allow https:// or mailto: hrefs
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+|mailto:[^)]+)\)/g, '<a href="$2">$1</a>');
    return s;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Blank line
    if (line.trim() === "") {
      closeList();
      closeBlockquote();
      continue;
    }

    // Headings
    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      closeList();
      closeBlockquote();
      const level = heading[1].length;
      html.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }

    // Unordered list item
    const listItem = line.match(/^[-*]\s+(.+)$/);
    if (listItem) {
      closeBlockquote();
      if (!inList) { html.push("<ul>"); inList = true; }
      html.push(`<li>${inline(listItem[1])}</li>`);
      continue;
    }

    // Blockquote
    const bq = line.match(/^>\s?(.*)$/);
    if (bq) {
      closeList();
      if (!inBlockquote) { html.push("<blockquote>"); inBlockquote = true; }
      html.push(`<p>${inline(bq[1])}</p>`);
      continue;
    }

    // Plain paragraph
    closeList();
    closeBlockquote();
    html.push(`<p>${inline(line)}</p>`);
  }

  closeList();
  closeBlockquote();
  return html.join("\n");
}

// ── Page template ────────────────────────────────────────────
function buildPage({ lang, title, version, effectiveDate, bodyHtml, langSwitchHref, langSwitchLabel }) {
  const metaLine = lang === "sv"
    ? `Version ${escapeHtml(version)} &middot; Senast uppdaterad ${escapeHtml(effectiveDate)}`
    : `Version ${escapeHtml(version)} &middot; Last updated ${escapeHtml(effectiveDate)}`;

  // Favicon inline SVG (matches index.html)
  const favicon = `data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20320%20320%22%3E%3Crect%20width%3D%22320%22%20height%3D%22320%22%20rx%3D%2252%22%20fill%3D%22%23F6F4EF%22%2F%3E%3Cg%20transform%3D%22translate(-72%2C-28)%20scale(1.16)%22%3E%3Cpath%20fill%3D%22%230e70f4%22%20d%3D%22m%20246.56165%2C187.85079%20c%20-1.65%2C-0.42834%20-7.9725%2C-0.83204%20-14.05%2C-0.89712%20-11.41915%2C-0.12226%20-13.45%2C-0.78551%20-13.45%2C-4.39255%200%2C-1.03083%202.41394%2C-4.42833%205.36432%2C-7.55%202.95038%2C-3.12167%205.91762%2C-6.7376%206.59387%2C-8.03541%201.14026%2C-2.1883%200.80318%2C-2.77428%20-4.64182%2C-8.06939%20-10.16508%2C-9.88524%20-28.58112%2C-21.01578%20-41.44129%2C-25.04686%20-11.65675%2C-3.65386%20-14.87508%2C-2.33126%20-14.87508%2C6.11307%200%2C6.1745%20-0.98838%2C6.55752%20-3.00391%2C9.16559%20-0.96208%2C1.24492%20-3.373%2C3.81393%20-4.46371%2C4.7902%20-1.55276%2C1.38986%20-11.58965%2C1.90704%20-36.44806%2C1.90704%20-27.04712%2C0%20-28.12543%2C-0.22334%20-32.555646%2C-6.74298%20l%20-2.528678%2C-3.72129%20V%20116.83536%2088.29963%20l%202.528678%2C-3.721284%20c%204.497186%2C-6.618207%205.162656%2C-6.742985%2035.961506%2C-6.742985%2025.51076%2C0%2027.88153%2C0.148985%2031.46544%2C1.977361%205.81629%2C2.967247%208.2515%2C7.07298%208.99294%2C15.161983%200.45162%2C4.927085%201.19431%2C7.447965%202.61195%2C8.865615%202.00413%2C2.00412%2013.94309%2C7.36065%2024.93949%2C11.18933%2015.22425%2C5.30072%2037.81004%2C19.3314%2049.22028%2C30.5765%205.0202%2C4.94754%205.49144%2C4.86377%2013.63787%2C-2.42444%203.6692%2C-3.28265%205.67176%2C-4.34635%208.18262%2C-4.34635%202.56066%2C0%203.49524%2C0.51694%204.06781%2C2.25%200.87922%2C2.66126%200.70095%2C20.77358%20-0.35678%2C36.25%20l%20-0.7518%2C11%20-11%2C0.14711%20c%20-6.05%2C0.0809%20-12.35%2C-0.20335%20-14%2C-0.63168%20z%22%2F%3E%3Cpath%20fill%3D%22%23e4223d%22%20d%3D%22m%20242.06165%2C246.50414%20c%20-10.34393%2C-4.83591%20-11.48206%2C-8.21984%20-11.49219%2C-34.16878%20l%20-0.008%2C-20%2011%2C0.18362%20c%206.05%2C0.101%2015.28171%2C0.47833%2020.5149%2C0.83852%208.95234%2C0.61618%209.63228%2C0.52537%2011.5%2C-1.53574%201.60399%2C-1.77007%202.08645%2C-4.10122%202.51299%2C-12.14223%200.38364%2C-7.23223%200.93016%2C-10.20599%202%2C-10.88257%200.80966%2C-0.51204%205.81607%2C-0.93787%2011.12536%2C-0.94629%20l%209.65326%2C0.92272%205.96916%2C1.68494%204.48395%2C5.90604%20-0.0884%2C8.56367%20c%20-0.0599%2C5.80074%20-0.0427%2C50.75817%20-1.74588%2C54.05172%20-1.70678%2C3.30055%20-6.51421%2C6.85561%20-9.27068%2C6.85561%20-1.12014%2C0%20-2.31473%2C0.45%20-2.65465%2C1%20-0.91311%2C1.47744%20-50.28511%2C1.17178%20-53.5%2C-0.33122%20z%22%2F%3E%3C%2Fg%3E%3C%2Fsvg%3E`;

  // Brand logo SVG (simplified inline for the nav)
  const logoSvg = `<svg class="brand-logo" viewBox="0 0 784 248" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path fill="#0F71F6" d="M241 4c-39 0-57 2-66 8-11 7-13 14-13 61v47l3 4c5 7 8 8 35 8h28l6-6c4-4 7-9 7-13 0-6-2-7-14-8l-14-1v-69l64 1c61 1 64 1 67 6 2 3 3 17 3 65v60l-4 1c-3 1-4-1-4-8 0-9-2-14-9-17-11-4-36-17-50-26-18-12-43-21-60-21l-7 1 7 8c11 13 16 23 16 31 0 5-3 8-14 9l-14 1v22c0 21 1 23 7 28 8 7 57 8 64 1 3-3 4-10 4-55 0-36 1-51 4-52 3-2 3 11 3 55 0 49 1 57 6 62 4 4 16 5 55 5 49 0 50 0 55-6l5-6V72c0-53-1-61-6-66-6-6-22-7-110-7z"/><path fill="#E71E3C" d="M231 213c-10-5-11-9-12-35v-19l12 1c7 0 16 1 21 1 9 1 10 0 12-2 2-2 2-5 3-12 0-8 1-11 2-11 1-1 6-1 11-1l10 1 6 2 4 6v63c0 4-1 8-4 10-3 3-14 4-54 4-24 0-11 0-11-8z"/></svg>`;

  return `<!doctype html>
<html lang="${lang}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>${escapeHtml(title)} — Frånvarokollen</title>
<meta name="description" content="${escapeHtml(title)} — Frånvarokollen" />
<link rel="icon" type="image/svg+xml" href="${favicon}" />
<meta name="theme-color" content="#12325A" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root{
    --navy:#0D1E36;
    --navy-deep:#081526;
    --blue:#2563EB;
    --red:#DC2626;
    --cream:#F8FAFC;
    --cream-deep:#F1F5F9;
    --ink:#0F172A;
    --muted:#64748B;
    --line:#E2E8F0;
    --white:#ffffff;
    --shadow:0 4px 20px rgba(15,23,42,0.09),0 1px 4px rgba(15,23,42,0.05);
    --shadow-sm:0 2px 10px rgba(15,23,42,0.07),0 1px 2px rgba(15,23,42,0.04);
    --radius:12px;
    --radius-sm:8px;
  }
  *{box-sizing:border-box}
  html{scroll-behavior:smooth}
  body{
    margin:0;
    font-family:'Plus Jakarta Sans',system-ui,sans-serif;
    font-weight:400;
    color:var(--ink);
    background:var(--white);
    line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }
  a{color:var(--blue);text-decoration:none}
  a:hover{text-decoration:underline}
  img,svg{display:block;max-width:100%}

  /* nav */
  .nav{
    position:sticky;top:0;z-index:50;
    background:rgba(246,244,239,0.92);
    backdrop-filter:blur(10px);
    -webkit-backdrop-filter:blur(10px);
    border-bottom:1px solid var(--line);
  }
  .nav-inner{display:flex;align-items:center;justify-content:space-between;height:72px;max-width:1200px;margin:0 auto;padding:0 24px}
  .brand{display:flex;align-items:center;gap:12px;font-weight:800;color:var(--navy);text-decoration:none}
  .brand:hover{text-decoration:none}
  .brand-logo{height:36px;width:auto;display:block}
  .nav-back{font-size:14px;font-weight:600;color:var(--muted);display:flex;align-items:center;gap:6px}
  .nav-back:hover{color:var(--navy);text-decoration:none}
  .nav-back svg{width:16px;height:16px}

  /* article */
  .legal-wrap{max-width:780px;margin:0 auto;padding:56px 24px 96px}
  .legal-header{margin-bottom:40px;padding-bottom:32px;border-bottom:1px solid var(--line)}
  .legal-header h1{
    font-family:'Plus Jakarta Sans',sans-serif;
    font-weight:800;letter-spacing:-0.02em;
    font-size:clamp(28px,4vw,42px);
    color:var(--navy);line-height:1.15;margin:0 0 12px;
  }
  .legal-meta{
    font-size:13px;color:var(--muted);
    font-family:'JetBrains Mono',monospace;
    font-weight:600;letter-spacing:0.04em;
  }
  .lang-switch{
    display:inline-flex;align-items:center;gap:8px;
    margin-top:14px;
    font-size:13px;font-weight:600;
    color:var(--blue);
  }
  .lang-switch svg{width:14px;height:14px}

  /* markdown body */
  .legal-body{color:var(--ink);font-size:16px;line-height:1.75}
  .legal-body h1{font-size:28px;color:var(--navy);font-weight:800;letter-spacing:-0.02em;margin:48px 0 16px}
  .legal-body h2{font-size:22px;color:var(--navy);font-weight:800;letter-spacing:-0.02em;margin:40px 0 14px}
  .legal-body h3{font-size:18px;color:var(--navy);font-weight:700;margin:32px 0 12px}
  .legal-body h4{font-size:15px;color:var(--navy);font-weight:700;margin:24px 0 10px}
  .legal-body p{margin:0 0 16px}
  .legal-body ul{margin:0 0 16px;padding-left:24px}
  .legal-body li{margin-bottom:8px}
  .legal-body blockquote{
    margin:0 0 16px;padding:16px 20px;
    border-left:3px solid var(--blue);
    background:var(--cream);
    border-radius:0 var(--radius-sm) var(--radius-sm) 0;
    color:var(--muted);
  }
  .legal-body blockquote p{margin:0}
  .legal-body strong{color:var(--navy);font-weight:700}
  .legal-body a{color:var(--blue)}
  .legal-body a:hover{text-decoration:underline}

  /* footer */
  .footer{
    background:#060F1C;
    color:rgba(255,255,255,0.6);
    padding:40px 0 28px;
    border-top:1px solid rgba(255,255,255,0.06);
  }
  .footer-inner{max-width:1200px;margin:0 auto;padding:0 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
  .footer a{font-size:13px;color:rgba(255,255,255,0.55);margin-left:20px;transition:color .15s}
  .footer a:hover{color:#fff;text-decoration:none}
  .footer-copy{font-size:13px}
  .footer-links{display:flex;flex-wrap:wrap;align-items:center}

  @media(max-width:600px){
    .legal-wrap{padding:36px 16px 64px}
    .footer-inner{flex-direction:column;align-items:flex-start}
    .footer-links a{margin-left:0;margin-right:16px}
  }
</style>
</head>
<body>

<header class="nav">
  <nav class="nav-inner">
    <a href="/" class="brand" aria-label="Frånvarokollen hem">
      ${logoSvg}
    </a>
    <a href="/" class="nav-back">
      <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 12L6 8l4-4"/></svg>
      ${lang === "sv" ? "Tillbaka" : "Back"}
    </a>
  </nav>
</header>

<main>
  <div class="legal-wrap">
    <div class="legal-header">
      <h1>${escapeHtml(title)}</h1>
      <div class="legal-meta">${metaLine}</div>
      <a href="${escapeHtml(langSwitchHref)}" class="lang-switch">
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6"/><path d="M8 2a9 9 0 0 1 0 12M8 2a9 9 0 0 0 0 12M2 8h12"/></svg>
        ${escapeHtml(langSwitchLabel)}
      </a>
    </div>
    <article class="legal-body">
      ${bodyHtml}
    </article>
  </div>
</main>

<footer class="footer">
  <div class="footer-inner">
    <span class="footer-copy">&copy; 2026 Fr&aring;nvarokollen Sverige AB &middot; Org.nr: 559585-6450</span>
    <nav class="footer-links">
      <a href="/anvandarvillkor">Anv&auml;ndarvillkor</a>
      <a href="/terms">Terms (EN)</a>
      <a href="#">Integritetspolicy</a>
    </nav>
  </div>
</footer>

</body>
</html>`;
}

// ── Fallback page (no content, but always resolves) ──────────
function buildFallbackPage(lang) {
  const isSv = lang === "sv";
  const title = isSv ? "Användarvillkor" : "Terms of Service";
  const msg = isSv
    ? "Dokumentet är tillfälligt otillgängligt. Försök igen om en stund."
    : "This document is temporarily unavailable. Please try again shortly.";
  return `<!doctype html>
<html lang="${lang}">
<head>
<meta charset="utf-8"/>
<title>${escapeHtml(title)} — Frånvarokollen</title>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>
  body{font-family:system-ui,sans-serif;max-width:600px;margin:80px auto;padding:0 24px;color:#0F172A}
  h1{font-size:28px;font-weight:800;color:#0D1E36;margin-bottom:16px}
  p{color:#64748B;font-size:16px;line-height:1.6}
  a{color:#2563EB}
</style>
</head>
<body>
<h1>${escapeHtml(title)}</h1>
<p>${escapeHtml(msg)}</p>
<p><a href="/">&larr; ${isSv ? "Till startsidan" : "Back to home"}</a></p>
</body>
</html>`;
}

// ── Main fetch handler ───────────────────────────────────────
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, "") || "/"; // strip trailing slash

    const isSv = path === "/anvandarvillkor";
    const isEn = path === "/terms";

    if (!isSv && !isEn) {
      // Pass through to static assets
      return env.ASSETS.fetch(request);
    }

    const lang = isSv ? "sv" : "en";
    const cacheKey = new Request(`https://legal-cache.internal/${lang}`, { method: "GET" });
    const cfCache = caches.default;

    // 1. Try CF cache first
    const cached = await cfCache.match(cacheKey);
    if (cached) return cached;

    // 2. Fetch upstream
    let data = null;
    try {
      const upstream = await fetch(LEGAL_API, {
        headers: { "Accept": "application/json", "User-Agent": "FVK-Website/1.0" },
        cf: { cacheTtl: 0 }, // bypass CF's own edge cache for the API request
      });
      if (upstream.ok) {
        data = await upstream.json();
      }
    } catch (_) {
      // network failure — fall through to fallback
    }

    // Portal wraps the record as { doc: {...} }; tolerate a bare object too.
    const doc = data && (data.doc || data);

    if (!doc || (!doc.body_sv && !doc.body_en)) {
      // 3a. Upstream failed or returned nothing usable — serve fallback
      // (always HTTP 200; legal pages must resolve)
      return new Response(buildFallbackPage(lang), {
        status: 200,
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }

    // 3b. Build the page
    const rawBody = isSv ? doc.body_sv : doc.body_en;
    const docTitle = doc.title || (isSv ? "Användarvillkor" : "Terms of Service");
    const version = String(doc.version || "—");
    const effectiveDate = doc.effective_date
      ? new Date(doc.effective_date).toLocaleDateString(isSv ? "sv-SE" : "en-GB", { day: "numeric", month: "long", year: "numeric" })
      : "—";

    const bodyHtml = renderMarkdown(rawBody || "");

    const pageHtml = buildPage({
      lang,
      title: docTitle,
      version,
      effectiveDate,
      bodyHtml,
      langSwitchHref: isSv ? "/terms" : "/anvandarvillkor",
      langSwitchLabel: isSv ? "Read in English" : "Läs på svenska",
    });

    const response = new Response(pageHtml, {
      status: 200,
      headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": `public, max-age=${CACHE_TTL}, s-maxage=${CACHE_TTL}`,
      },
    });

    // Store in CF cache (non-blocking)
    ctx.waitUntil(cfCache.put(cacheKey, response.clone()));

    return response;
  },
};
