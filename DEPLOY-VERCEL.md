# Vercel Deployment

Statische Seite (kein Build-Schritt). Alle Dateien liegen in `site/`.

## Projekt importieren
1. https://vercel.com/new → Repo `Peeazyyy/wetteristimmer` importieren
2. **Root Directory** auf **`site`** setzen (wichtig — die Seite liegt im Unterordner)
3. Framework Preset: **Other** (kein Build-Command, kein Output-Directory nötig)
4. Deploy

Die `site/vercel.json` regelt Clean-URLs und langes Caching für Bilder/Fonts.

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
