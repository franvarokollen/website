// ============================================================
// functions/terms.js  — Cloudflare Pages Function
// Route: /terms
// Fetches the published Terms of Service from the Skolkollen API,
// renders body_en as English markdown, returns a server-rendered HTML page
// that is chrome-identical to the site's static legal pages.
// ============================================================

import { renderMarkdown, renderLegalPage, fallbackPage } from "./_lib/legal.js";

const LEGAL_API  = "https://www.skolkollen.com/api/legal?slug=terms-of-service";
const CACHE_TTL  = 3600; // 1 hour
const CACHE_KEY  = new Request("https://legal-cache.internal/en", { method: "GET" });

export async function onRequestGet(context) {
  const cfCache = caches.default;

  // 1. Try Cloudflare cache
  const cached = await cfCache.match(CACHE_KEY);
  if (cached) return cached;

  // 2. Fetch upstream
  let doc = null;
  try {
    const upstream = await fetch(LEGAL_API, {
      headers: { "Accept": "application/json", "User-Agent": "FVK-Website/1.0" },
    });
    if (upstream.ok) {
      const data = await upstream.json();
      // API returns { doc: { ... } }
      doc = data && (data.doc || data);
    }
  } catch (_) {
    // network failure — fall through to fallback
  }

  // 3a. No usable document — return on-brand fallback (HTTP 200, always resolves)
  if (!doc || !doc.body_en) {
    return new Response(fallbackPage("en"), {
      status: 200,
      headers: { "Content-Type": "text/html; charset=utf-8" },
    });
  }

  // 3b. Render the page
  const version  = String(doc.version || "—");
  const docTitle = doc.title || "Terms of Service";
  const effectiveDate = doc.effective_date
    ? new Date(doc.effective_date).toLocaleDateString("en-GB", {
        day: "numeric", month: "long", year: "numeric",
      })
    : "—";

  const bodyHtml = renderMarkdown(doc.body_en);
  const pageHtml = renderLegalPage({
    lang:            "en",
    title:           docTitle,
    version,
    effectiveDate,
    bodyHtml,
    langSwitchHref:  "/anvandarvillkor",
    langSwitchLabel: "Läs på svenska",
  });

  const response = new Response(pageHtml, {
    status: 200,
    headers: {
      "Content-Type":  "text/html; charset=utf-8",
      "Cache-Control": `public, max-age=${CACHE_TTL}, s-maxage=${CACHE_TTL}`,
    },
  });

  // Store in CF edge cache (non-blocking)
  context.waitUntil(cfCache.put(CACHE_KEY, response.clone()));

  return response;
}
