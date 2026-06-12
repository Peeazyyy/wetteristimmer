# Vercel Deployment

Statische Seite (kein Build-Schritt). Alle Dateien liegen in `site/`.

## Projekt importieren
1. https://vercel.com/new → Repo `Peeazyyy/wetteristimmer` importieren
2. Framework Preset: **Other**, **Root Directory beim Default belassen** (Repo-Root)
3. Deploy

Die `vercel.json` im Repo-Root zeigt Vercel über `outputDirectory: "site"` auf den
Unterordner und regelt Clean-URLs + langes Caching für Bilder/Fonts. Es ist daher
**kein** manuelles Setzen des Root Directory nötig.

Alternative (auch ok): Root Directory im Dashboard auf `site` stellen — dann wird
die `vercel.json` im Root ignoriert, die Seite funktioniert aber trotzdem.

## Domain
- In Vercel: Project → Settings → **Domains** → `wetteristimmer.com` (und optional `www`) hinzufügen
- Vercel zeigt dir dort die passenden DNS-Einträge an (A-Record auf `76.76.21.21`
  bzw. die von Vercel genannte IP, und CNAME `cname.vercel-dns.com` für `www`)
- Die GitHub-Pages-Dateien `site/CNAME` und `site/.nojekyll` stören Vercel nicht,
  werden aber nicht gebraucht — bei Bedarf entfernbar.

## Tracking (Web Analytics)
Das Web-Analytics-Script ist in `site/index.html` eingebunden
(`/_vercel/insights/script.js`). Es liefert Daten, sobald im Vercel-Dashboard
aktiviert: Project → **Analytics** → *Enable*. Danach stellt Vercel die Route
automatisch bereit.

Speed Insights ist im Free-Plan nicht verfügbar und daher bewusst nicht
eingebunden (würde sonst dauerhaft 404 liefern). Bei einem Upgrade kann das
Snippet `/_vercel/speed-insights/script.js` analog ergänzt werden.
