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

## Tracking (Web Analytics + Speed Insights)
Die Tracking-Scripts sind bereits in `site/index.html` eingebunden
(`/_vercel/insights/script.js` und `/_vercel/speed-insights/script.js`).
Sie liefern erst Daten, sobald es im Vercel-Dashboard aktiviert ist:
1. Project → **Analytics** → *Enable* (Web Analytics)
2. Project → **Speed Insights** → *Enable*

Danach werden die `/_vercel/*`-Routen automatisch von Vercel bereitgestellt
und die bereits eingebauten Scripts beginnen zu senden.
