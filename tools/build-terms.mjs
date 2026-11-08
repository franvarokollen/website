// tools/build-terms.mjs
// Builds the static Terms pages from tools/legal/terms.{sv,en}.md:
//   anvandarvillkor.html (Swedish, canonical /anvandarvillkor)
//   terms.html           (English, canonical /terms)
// Run: node tools/build-terms.mjs   (after editing the markdown or bumping VERSION/DATE)
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { renderMarkdown, renderLegalPage } from "./legal/shell.mjs";

const VERSION = "2.0";
const DATE = "2026-11-08";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const d = new Date(DATE + "T12:00:00Z");

const pages = [
  { lang: "sv", out: "anvandarvillkor.html", title: "Användarvillkor för Frånvarokollen",
    date: d.toLocaleDateString("sv-SE", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }),
    langSwitchHref: "/terms", langSwitchLabel: "Read in English" },
  { lang: "en", out: "terms.html", title: "Terms of Service for Frånvarokollen",
    date: d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }),
    langSwitchHref: "/anvandarvillkor", langSwitchLabel: "Läs på svenska" },
];

for (const p of pages) {
  const md = readFileSync(join(root, "tools", "legal", `terms.${p.lang}.md`), "utf8");
  const html = renderLegalPage({
    lang: p.lang, title: p.title, version: VERSION, effectiveDate: p.date,
    bodyHtml: renderMarkdown(md), langSwitchHref: p.langSwitchHref, langSwitchLabel: p.langSwitchLabel,
  });
  writeFileSync(join(root, p.out), html);
  console.log("wrote", p.out);
}
