# Bild-Generierung – To-do (Higgsfield)

Alle Bilder werden neu generiert (eigene KI-Motive, passend zur Rolle des
Original-Bildes auf der Seite). Maße/Ratios stammen aus `_snapshot/images.json`.

## Slideshow (Hero, 1920×1080, 15 Slides)
- [x] slide-01 … slide-15 — Promo-Slides zur Ausgabe #38

## Produktgrid (Höhe 270px, Ratio = Original)
- [x] cover-38 (691×1024) — Das Wetter #38 / auch Abo-Karten (web2-Variante)
- [x] cover-37 (690×1024) — Das Wetter #37
- [x] cover-36 (759×1024) — Das Wetter #36
- [x] cover-34 (759×1024) — Das Wetter #34
- [x] cover-abo (691×1024) — Abo-Karte (4 Produkte teilen sich dieses Bild)
- [x] hoodie-classic (595×595) — Hoodie »Classic«
- [x] gotbag (1024×1024) — DAS WETTER X GOTBAG Bauchtasche
- [x] shirt-pink (1024×1002) — Shirt »Classic« Pink/Rot
- [x] shirt-schwarz (1024×1024) — Shirt »Classic« Schwarz
- [x] shirt-weiss (1024×1024) — Shirt »Classic« Weiß
- [x] cap-logo (1024×1024) — Cap »Logo«
- [x] cap-eknbw (768×1024) — Cap »Es kann nur besser werden«
- [x] bundle-37-36 (819×1024) — Bundle #37+#36
- [x] buch-palo-santo (624×1024) — Roman „Palo Santo“
- [x] buch-text-musik (738×1024) — „Das Wetter – Buch für Text und Musik“
- [x] cover-33 (659×973) — Das Wetter #33
- [x] cover-32 (660×971) — Das Wetter #32

## Ablauf
1. Original ansehen (`_snapshot/images/`) → Beschreibung notieren
2. Higgsfield `generate_image` mit eigener Beschreibung, passende Ratio
3. Ergebnis-URLs in `scripts/generated-images.json`
4. CI lädt die Dateien nach `site/assets/img/` und committet
5. `site/index.html`: Platzhalter → `<img>`
