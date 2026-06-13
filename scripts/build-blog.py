# -*- coding: utf-8 -*-
"""Builds the /blog section: 5 articles + index, with JSON-LD schema, meta/OG,
FAQs, breadcrumbs, internal links. Also refreshes sitemap.xml. German copy,
original text, no em-dashes in prose."""
import os, json, html, glob, datetime

BASE = "https://www.wetteristimmer.com"
TODAY = "2026-06-13"
os.makedirs("site/blog", exist_ok=True)

FOOTER = '''<div class="footerwrap">
<footer class="pad fs-1">
  <a class="color4 cl space bolfont fs-1" href="/">Das Wetter</a>
    <nav class="footermenu fs-1">
        <a class="cl bolfont space color2 fs-1" href="/blog">Journal</a>
        <a class="cl bolfont space color2 fs-1" href="/pages/about">About</a>
        <a class="cl bolfont space color2 fs-1" href="/pages/verkaufsstellen">Verkaufsstellen</a>
        <a class="cl bolfont space color2 fs-1" href="/pages/impressum">Impressum</a>
        <a class="cl bolfont space color2 fs-1" href="/pages/uber-uns">Datenschutz</a>
        <a class="cl bolfont space color2 fs-1" href="/pages/agbs">AGBs</a>
    </nav>
</footer>
</div>'''

def head(title, desc, slug, image, og_type="article"):
    canon = f"{BASE}/blog/{slug}" if slug else f"{BASE}/blog"
    img = f"{BASE}{image}"
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{img}">
<meta property="og:site_name" content="Das Wetter">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{img}">
<link href="/assets/css/fonts.css" rel="stylesheet" type="text/css" media="all">
<link href="/assets/css/variables.css" rel="stylesheet" type="text/css" media="all">
<link href="/assets/css/application.css" rel="stylesheet" type="text/css" media="all">
<link href="/assets/css/rebuild.css" rel="stylesheet" type="text/css" media="all">
</head>
<body>
<div class="subpage pad">
  <header class="subhead">
    <a class="color3 cl bolfont" href="/">Das Wetter</a>
    <span class="color2 bolfont space">Journal</span>
  </header>
'''

def article_schema(a):
    blogposting = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": a["title"],
        "description": a["desc"],
        "image": f"{BASE}{a['hero']}",
        "datePublished": TODAY,
        "dateModified": TODAY,
        "author": {"@type": "Organization", "name": "Das Wetter", "url": BASE},
        "publisher": {
            "@type": "Organization",
            "name": "Das Wetter",
            "logo": {"@type": "ImageObject", "url": f"{BASE}/assets/img/cover-38.webp"},
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{BASE}/blog/{a['slug']}"},
        "articleSection": a["kicker"],
        "inLanguage": "de",
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Start", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Journal", "item": BASE + "/blog"},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": f"{BASE}/blog/{a['slug']}"},
        ],
    }
    faqpage = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": ans}}
            for q, ans in a["faqs"]
        ],
    }
    out = ""
    for obj in (blogposting, breadcrumb, faqpage):
        out += '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>\n'
    return out

def render_article(a, others):
    faq_html = "\n".join(
        f"    <details><summary>{html.escape(q)}</summary><p>{html.escape(ans)}</p></details>"
        for q, ans in a["faqs"]
    )
    rel = [x for x in others if x["slug"] != a["slug"]][:3]
    rel_html = "\n".join(
        f'''      <a class="blogcard" href="/blog/{r['slug']}">
        <img src="{r['hero']}" alt="{html.escape(r['title'])}" loading="lazy">
        <span class="kicker">{r['kicker']}</span>
        <h3>{html.escape(r['title'])}</h3>
      </a>''' for r in rel
    )
    s = head(a["title"] + " | Das Wetter", a["desc"], a["slug"], a["hero"])
    s += article_schema(a)
    s += f'''  <nav class="breadcrumb"><a href="/">Start</a> / <a href="/blog">Journal</a> / {html.escape(a['title'])}</nav>
  <article class="article">
    <div class="kicker">{a['kicker']}</div>
    <h1>{html.escape(a['title'])}</h1>
    <div class="meta">{a['date_label']} · Lesezeit {a['read']} Min · Das Wetter</div>
    <img class="hero" src="{a['hero']}" alt="{html.escape(a['hero_alt'])}">
{a['body']}
    <section class="faq">
      <h2>Häufige Fragen</h2>
{faq_html}
    </section>
    <section class="related">
      <h2>Weiterlesen</h2>
      <div class="bloglist">
{rel_html}
      </div>
    </section>
  </article>
</div>
{FOOTER}
</body>
</html>'''
    open(f"site/blog/{a['slug']}.html", "w").write(s)

# ---------------- content ----------------
def P(*ps): return "\n".join(f"    <p>{x}</p>" for x in ps)

articles = []

articles.append(dict(
 slug="songtexte-schreiben", kicker="Text", read=7, date_label="13. Juni 2026",
 title="Songtexte schreiben: der große Guide für eigene Texte",
 desc="Wie entsteht ein guter Songtext? Aufbau, Reim, Rhythmus und Bildsprache, plus praktische Tipps zum Anfangen und Überarbeiten.",
 hero="/assets/img/blog-songtexte-hero.webp", hero_alt="Schreibtisch mit Notizbuch, Stift und Gitarre",
 inline="/assets/img/blog-songtexte-inline.webp", inline_alt="Hände schreiben Songtext in ein Notizbuch",
 body=(
  P("Ein guter Songtext bleibt im Kopf, lange nachdem die Musik verklungen ist. Er erzählt in wenigen Zeilen, wofür ein Roman hundert Seiten braucht. Genau das macht das Schreiben so reizvoll und am Anfang auch so einschüchternd. Die gute Nachricht: Songtexte folgen Mustern, die sich lernen lassen. Wer sie versteht, kommt vom leeren Blatt schneller zur ersten fertigen Strophe.")
  + '\n    <h2>Mit einer klaren Idee starten</h2>\n'
  + P("Bevor du an Reime denkst, brauchst du einen Kern. Das kann ein Gefühl sein, ein Bild, ein Satz, den jemand gesagt hat. Schreibe diesen Kern in einem einzigen Satz auf. Wenn du dein Thema nicht in einem Satz fassen kannst, ist es meist noch zu groß. Ein guter Song handelt selten von der Liebe an sich, sondern von einem bestimmten Moment, einem bestimmten Abend, einer bestimmten Tür, die ins Schloss fällt.")
  + '\n    <h2>Die Struktur verstehen</h2>\n'
  + P("Die meisten Songs nutzen wenige Bausteine. Die Strophe bringt die Geschichte voran und liefert Details. Der Refrain fasst das Gefühl zusammen und wiederholt sich, deshalb sollte er die stärkste Zeile enthalten. Die Bridge bricht das Muster auf, oft kurz vor dem letzten Refrain, und gibt dem Stück eine Wendung. Ein bewährter Ablauf ist Strophe, Refrain, Strophe, Refrain, Bridge, Refrain. Du musst dich nicht daran halten, aber es ist ein sicheres Gerüst für den Anfang.")
  + f'\n    <img class="inline" src="/assets/img/blog-songtexte-inline.webp" alt="Hände schreiben Songtext in ein Notizbuch" loading="lazy">\n'
  + '\n    <h2>Reim und Rhythmus</h2>\n'
  + P("Reime sind ein Werkzeug, kein Gesetz. Sie geben einem Text Halt und machen Zeilen merkbar, doch ein erzwungener Reim fällt sofort auf. Wenn du zwischen einem schönen Reim und einer ehrlichen Aussage wählen musst, wähle die Aussage. Wichtiger als der Reim ist der Rhythmus. Sprich deine Zeilen laut aus und klopfe den Takt mit. Spürst du, wo die Betonung liegt, schreibst du Zeilen, die sich von selbst singen lassen.")
  + '\n    <h2>Bilder statt Floskeln</h2>\n'
  + P("Konkrete Bilder wirken stärker als abstrakte Begriffe. Statt zu sagen, dass jemand traurig ist, zeige die kalte Kaffeetasse, das Licht, das niemand ausgemacht hat, den Bus, der ohne dich abfährt. Solche Details lassen Hörerinnen und Hörer ihre eigene Geschichte hineinlesen. Vermeide Wendungen, die du schon hundertmal gehört hast. Wo dir eine Floskel in die Feder kommt, frage dich, was in deinem eigenen Leben dafür steht.")
  + '\n    <h2>Überarbeiten gehört dazu</h2>\n'
  + P("Der erste Entwurf darf schlecht sein. Sein einziger Zweck ist, überhaupt zu existieren. Die eigentliche Arbeit beginnt danach. Lies den Text am nächsten Tag mit frischem Blick, streiche jede Zeile, die nichts Neues sagt, und prüfe, ob jeder Reim wirklich nötig ist. Lege den Text dann beiseite und sing ihn. Stellen, an denen du stolperst, sind Stellen, die noch Arbeit brauchen. Mit jeder Runde wird der Song dichter.")
 ),
 faqs=[
  ("Wie fange ich an, wenn ich keine Idee habe?", "Sammle kleine Beobachtungen aus deinem Alltag in einem Notizbuch. Ein einziger ehrlicher Satz reicht oft als Startpunkt für eine ganze Strophe."),
  ("Muss sich ein Songtext reimen?", "Nein. Reime helfen beim Merken, sind aber kein Muss. Rhythmus und klare Bilder sind wichtiger als ein perfekter Reim."),
  ("Wie finde ich ein gutes Thema?", "Schränke es ein. Statt über ein großes Gefühl zu schreiben, wähle einen konkreten Moment, der dieses Gefühl auslöst."),
  ("Wie lang sollte ein Refrain sein?", "Kurz genug, um ihn nach einmal Hören mitsingen zu können. Zwei bis vier Zeilen mit einer starken Hauptzeile genügen meist."),
 ],
))

articles.append(dict(
 slug="vinyl-revival", kicker="Musik", read=6, date_label="13. Juni 2026",
 title="Vinyl-Revival 2026: warum Schallplatten wieder boomen",
 desc="Vinyl ist zurück und verkauft sich besser als seit Jahrzehnten. Woher der Boom kommt, was den Reiz ausmacht und wie der Einstieg gelingt.",
 hero="/assets/img/blog-vinyl-hero.webp", hero_alt="Plattenspieler mit drehender Schallplatte",
 inline="/assets/img/blog-vinyl-inline.webp", inline_alt="Hände blättern durch Schallplatten im Plattenladen",
 body=(
  P("Eigentlich sollte die Schallplatte längst verschwunden sein. Stattdessen füllt sie wieder Regale, Plattenläden öffnen neu und junge Hörerinnen und Hörer kaufen Alben, die sie auch streamen könnten. Das Vinyl-Revival ist kein nostalgischer Zufall, sondern eine Reaktion auf die Art, wie wir heute Musik konsumieren.")
  + '\n    <h2>Warum gerade jetzt</h2>\n'
  + P("Streaming hat Musik grenzenlos verfügbar gemacht. Alles ist da, sofort, kostenlos im Hintergrund. Gerade diese Beliebigkeit erzeugt den Wunsch nach dem Gegenteil. Eine Platte ist begrenzt, sie kostet Geld, sie nimmt Platz weg. Genau das macht sie wertvoll. Wer ein Album auflegt, entscheidet sich bewusst für diese eine Sache und gegen die endlose Auswahl.")
  + '\n    <h2>Der Mythos vom besseren Klang</h2>\n'
  + P("Über kaum etwas wird so gestritten wie über den Klang. Technisch lässt sich nicht pauschal sagen, dass Vinyl besser klingt als eine gute digitale Aufnahme. Es klingt anders. Die leichte Wärme, das sanfte Rauschen, kleine Unregelmäßigkeiten gehören zum Charakter dazu. Viele empfinden das als lebendiger. Wichtiger als die Messwerte ist, dass man bewusster hinhört.")
  + f'\n    <img class="inline" src="/assets/img/blog-vinyl-inline.webp" alt="Hände blättern durch Schallplatten im Plattenladen" loading="lazy">\n'
  + '\n    <h2>Das Ritual zählt</h2>\n'
  + P("Eine Platte zu hören ist eine kleine Handlung. Die Hülle aus dem Regal ziehen, die Scheibe auflegen, den Arm absenken, das Cover in die Hand nehmen und die Texte mitlesen. Diese Schritte verlangsamen das Hören. Man überspringt keine Lieder, sondern lässt die Seite laufen, so wie das Album gedacht war. Genau dieses Ritual fehlt vielen beim Streamen.")
  + '\n    <h2>Sammeln als Hobby</h2>\n'
  + P("Für viele wird aus dem Hören ein Sammeln. Eine Platte erinnert an den Tag, an dem man sie gefunden hat, an den Laden, an die Person, die sie empfohlen hat. Ein Regal voller Schallplatten erzählt eine Geschichte, die eine Playlist nicht erzählen kann. Dazu kommt das Stöbern selbst, das Wühlen in Kisten, der Fund, mit dem man nicht gerechnet hat.")
  + '\n    <h2>So gelingt der Einstieg</h2>\n'
  + P("Du brauchst weniger, als du denkst. Wichtig sind ein solider Plattenspieler mit gutem Tonabnehmer, ein Verstärker und Boxen oder ein Modell mit eingebauten Lautsprechern. Spare nicht an der Nadel, denn sie berührt die Rille direkt. Lagere Platten stehend, halte sie am Rand und nutze eine einfache Bürste gegen Staub. Beginne mit Alben, die du wirklich liebst, dann wird jede Platte zu einem kleinen Ereignis.")
 ),
 faqs=[
  ("Klingt Vinyl wirklich besser?", "Nicht messbar besser, aber anders. Viele schätzen die warme Färbung und das bewusste Hören. Der Eindruck ist auch eine Frage des Geschmacks."),
  ("Was kostet der Einstieg?", "Ein guter Einsteiger-Plattenspieler mit Verstärker und Boxen ist ab etwa 200 bis 300 Euro zu haben. Bei der Nadel sollte man nicht sparen."),
  ("Wie pflege ich meine Platten?", "Stehend lagern, nur am Rand anfassen und vor dem Abspielen mit einer Antistatikbürste reinigen. So bleiben Rillen und Klang lange gut."),
  ("Lohnt sich ein gebrauchter Plattenspieler?", "Ja, wenn Tonarm und Antrieb in Ordnung sind und die Nadel getauscht werden kann. Eine alte, abgenutzte Nadel kann Platten beschädigen."),
 ],
))

articles.append(dict(
 slug="poetry-slam-einstieg", kicker="Bühne", read=6, date_label="13. Juni 2026",
 title="Poetry Slam: dein Einstieg in die Bühnenpoesie",
 desc="Was ist ein Poetry Slam, welche Regeln gelten und wie schreibst du deinen ersten Text? Ein praktischer Guide für die Bühne.",
 hero="/assets/img/blog-poetry-hero.webp", hero_alt="Person am Mikrofon auf einer kleinen Bühne im Spotlight",
 inline="/assets/img/blog-poetry-inline.webp", inline_alt="Mikrofon und Notizbuch auf einem Barhocker",
 body=(
  P("Ein Poetry Slam ist ein Dichtwettstreit auf offener Bühne. Menschen tragen eigene Texte vor, das Publikum entscheidet, und am Ende gewinnt nicht die feinste Sprache, sondern der stärkste Moment. Kaum eine Bühne ist so offen für Anfänger, denn hier zählt die eigene Stimme mehr als jede Ausbildung.")
  + '\n    <h2>Was einen Slam ausmacht</h2>\n'
  + P("Auf einem Slam treten mehrere Personen nacheinander an. Jede trägt einen selbst geschriebenen Text vor, meist innerhalb weniger Minuten. Das Publikum bewertet, oft per Applaus oder über kleine Jurygruppen aus dem Saal. Die Stimmung ist eher Konzert als Lesung. Es wird gelacht, gejubelt und mitgefiebert.")
  + '\n    <h2>Die wichtigsten Regeln</h2>\n'
  + P("Drei Grundregeln gelten fast überall. Der Text muss von dir selbst stammen. Du hast ein Zeitlimit, meist um die fünf bis sechs Minuten. Du darfst keine Requisiten und keine Kostüme nutzen, nur Text und Stimme. Diese Schlichtheit ist gewollt, denn sie stellt die Sprache in den Mittelpunkt.")
  + f'\n    <img class="inline" src="/assets/img/blog-poetry-inline.webp" alt="Mikrofon und Notizbuch auf einem Barhocker" loading="lazy">\n'
  + '\n    <h2>Den ersten Text schreiben</h2>\n'
  + P("Schreibe über etwas, das dich wirklich bewegt. Slamtexte funktionieren, wenn sie ehrlich sind, ob lustig oder ernst. Beginne mit einem starken Einstieg, der sofort Aufmerksamkeit holt, und arbeite auf eine Pointe oder eine Wendung am Ende hin. Lies laut, während du schreibst, denn ein Slamtext lebt vom Klang und nicht nur vom Sinn.")
  + '\n    <h2>Auftreten und Vortrag</h2>\n'
  + P("Der Vortrag entscheidet so viel wie der Text. Sprich langsamer, als es sich anfühlt, mache Pausen und lass Pointen wirken. Schau ins Publikum, statt nur auf dein Blatt. Lampenfieber gehört dazu und legt sich mit jedem Auftritt. Es hilft, den Text vorher so oft zu üben, dass du ihn fast auswendig kannst.")
  + '\n    <h2>Wo du Slams findest</h2>\n'
  + P("In fast jeder größeren Stadt gibt es regelmäßige Slams, oft in Kulturzentren, Theatern oder Kneipen. Viele bieten eine offene Liste, in die du dich am Abend einträgst. Geh zuerst als Gast hin, sieh dir ein paar Abende an und melde dich dann an, wenn du dich bereit fühlst. Der erste Auftritt ist immer der schwerste und danach willst du meistens wieder.")
 ),
 faqs=[
  ("Wie lang darf mein Text sein?", "Meist gelten fünf bis sechs Minuten. Die genaue Zeit nennt die Veranstaltung vorher. Halte dich daran, sonst gibt es oft Punktabzug."),
  ("Brauche ich Bühnenerfahrung?", "Nein. Slams leben von neuen Stimmen. Viele Bühnen haben offene Listen, in die sich jede und jeder eintragen kann."),
  ("Worüber soll ich schreiben?", "Über etwas, das dich ehrlich beschäftigt. Persönliche, konkrete Texte berühren das Publikum stärker als allgemeine Themen."),
  ("Wie werde ich bewertet?", "Das Publikum entscheidet, oft per Applaus oder durch zufällig gewählte Jurygruppen aus dem Saal. Der Spaß steht über der Wertung."),
 ],
))

articles.append(dict(
 slug="neue-musik-entdecken", kicker="Musik", read=6, date_label="13. Juni 2026",
 title="Neue Musik entdecken: so findest du deinen nächsten Lieblingssong",
 desc="Immer dieselben Lieder? So entkommst du der Wiederholung und findest abseits der Charts Musik, die wirklich zu dir passt.",
 hero="/assets/img/blog-musik-hero.webp", hero_alt="Junge Person mit Kopfhörern hört Musik",
 inline="/assets/img/blog-musik-inline.webp", inline_alt="Kleines Konzert in einem intimen Club",
 body=(
  P("Nie war so viel Musik verfügbar, und nie war es so leicht, trotzdem immer dasselbe zu hören. Algorithmen schlagen vor, was dem ähnelt, was du schon kennst. Das ist bequem, führt aber in einen engen Kreis. Wer wirklich Neues finden will, braucht ein paar bewusste Gewohnheiten.")
  + '\n    <h2>Warum Entdecken schwerfällt</h2>\n'
  + P("Empfehlungssysteme sind darauf ausgelegt, dich bei der Stange zu halten, nicht dich zu überraschen. Sie spielen sicher und bleiben nah an deinem Geschmack. Dadurch verpasst du genau die Musik, die dich verändern könnte, weil sie zu weit weg von deinem bisherigen Hören liegt.")
  + '\n    <h2>Playlists und Algorithmen klug nutzen</h2>\n'
  + P("Du musst die Maschinen nicht meiden, sondern lenken. Höre gezielt in kuratierte Playlists hinein, die von Menschen zusammengestellt sind, nicht nur in automatische Mixe. Speichere einzelne Lieder, die dich treffen, und verfolge, wer sie gemacht hat. Wenn ein Algorithmus dir etwas Ungewohntes zeigt, gib ihm eine echte Chance, statt sofort weiterzuspringen.")
  + f'\n    <img class="inline" src="/assets/img/blog-musik-inline.webp" alt="Kleines Konzert in einem intimen Club" loading="lazy">\n'
  + '\n    <h2>Menschen statt Maschinen</h2>\n'
  + P("Die besten Empfehlungen kommen noch immer von Menschen. Frage Freundinnen und Freunde, was sie gerade hören. Lies Musikmagazine und Blogs, die ihre Funde begründen. Höre Radiosendungen mit echten Moderatorinnen und Moderatoren, die Musik einordnen. Eine Empfehlung mit Geschichte bleibt eher hängen als ein anonymer Vorschlag.")
  + '\n    <h2>Live ist der beste Filter</h2>\n'
  + P("Geh auf kleine Konzerte, auch wenn du die Namen nicht kennst. In einem vollen kleinen Club hörst du Musik mit dem ganzen Körper, und Vorbands sind eine ideale Entdeckungsquelle. Wer einmal live von einer unbekannten Band begeistert wurde, hört danach anders zu. Lokale Bühnen sind oft günstiger, als man denkt.")
  + '\n    <h2>Ein einfaches System</h2>\n'
  + P("Lege dir eine Sammelliste an, in die jeder neue Fund wandert. Nimm dir einmal pro Woche Zeit, gezielt etwas Unbekanntes zu hören, ganz bewusst und ohne Nebenbeschäftigung. Notiere, was bleibt. Nach wenigen Wochen hast du eine Liste, die nur dir gehört, und ein Gehör, das offener geworden ist.")
 ),
 faqs=[
  ("Wie finde ich Musik abseits der Charts?", "Nutze von Menschen kuratierte Playlists, Musikblogs und Radiosendungen und geh auf kleine Konzerte. Persönliche Empfehlungen führen am weitesten."),
  ("Sind Algorithmen gut oder schlecht?", "Beides. Sie sind bequem, halten dich aber nah an Bekanntem. Nutze sie bewusst und gib ungewohnten Vorschlägen eine echte Chance."),
  ("Wie baue ich eine gute Playlist?", "Sammle nur Lieder, die dich wirklich treffen, und ordne sie nach Stimmung statt nach Genre. Lieber kurz und stark als lang und beliebig."),
  ("Wo finde ich kleine Konzerte?", "In lokalen Clubs, Kulturzentren und über Veranstaltungskalender deiner Stadt. Vorbands sind oft die beste Entdeckungsquelle."),
 ],
))

articles.append(dict(
 slug="gegenwartslyrik-verstehen", kicker="Text", read=6, date_label="13. Juni 2026",
 title="Gegenwartslyrik verstehen: wie junge deutsche Lyrik heute klingt",
 desc="Lyrik gilt als schwer, ist aber lebendiger denn je. Was Gegenwartslyrik ausmacht, wie man Gedichte liest und wo man neue Stimmen findet.",
 hero="/assets/img/blog-lyrik-hero.webp", hero_alt="Aufgeschlagener Gedichtband auf einem Tisch",
 inline="/assets/img/blog-lyrik-inline.webp", inline_alt="Stapel schmaler Gedichtbände",
 body=(
  P("Lyrik hat einen Ruf, der ihr unrecht tut. Viele denken an verstaubte Schulgedichte und schwere Deutung. Dabei ist die deutschsprachige Lyrik der Gegenwart so offen, direkt und vielfältig wie lange nicht. Sie spricht von Heute, in einer Sprache von Heute.")
  + '\n    <h2>Was Gegenwartslyrik ist</h2>\n'
  + P("Gegenwartslyrik meint Gedichte, die in unserer Zeit entstehen. Sie reimt sich oft nicht und folgt selten festen Formen. Stattdessen arbeitet sie mit Bildern, Brüchen und genauem Blick auf den Alltag. Themen sind Identität, Herkunft, Klima, Liebe, Stadt und Netz, also genau das, was junge Menschen beschäftigt.")
  + '\n    <h2>Wie sie klingt</h2>\n'
  + P("Viele Gedichte heute klingen wie gesprochene Sprache, nur verdichtet. Eine Zeile kann lapidar beginnen und mit einem Bild enden, das lange nachhallt. Die Form ist frei, doch nicht beliebig. Wo eine Zeile umbricht, entsteht eine kleine Pause, ein Atem, der zur Bedeutung gehört. Genau dieses Spiel mit Pausen unterscheidet Lyrik von Prosa.")
  + f'\n    <img class="inline" src="/assets/img/blog-lyrik-inline.webp" alt="Stapel schmaler Gedichtbände" loading="lazy">\n'
  + '\n    <h2>Lesen lernen</h2>\n'
  + P("Ein Gedicht muss man nicht sofort verstehen. Lies es zuerst laut, ohne nach der Bedeutung zu suchen, und achte nur auf den Klang. Lies es dann ein zweites Mal und frage dich, welches Bild hängenbleibt. Erst danach lohnt die Frage, was es sagen könnte. Oft gibt es nicht die eine richtige Deutung, sondern mehrere, die nebeneinander stehen dürfen.")
  + '\n    <h2>Lyrik und Pop liegen nah beieinander</h2>\n'
  + P("Die Grenze zwischen Liedtext und Gedicht ist durchlässiger, als die Schule glauben macht. Viele Rap- und Songtexte arbeiten mit denselben Mitteln wie Lyrik, mit Reim, Rhythmus, Bild und Wiederholung. Wer Texte mag, die etwas wagen, ist von Pop zur Lyrik nur einen kleinen Schritt entfernt.")
  + '\n    <h2>Selbst anfangen</h2>\n'
  + P("Du brauchst keine Erlaubnis, um Gedichte zu lesen oder zu schreiben. Beginne mit schmalen Bänden aktueller Stimmen und lies in kleinen Dosen, ein paar Gedichte am Abend. Schreibe selbst eine Beobachtung in drei Zeilen auf, ohne Anspruch. Lyrik ist keine Geheimwissenschaft, sondern eine Art, genauer hinzusehen.")
 ),
 faqs=[
  ("Muss sich Lyrik reimen?", "Nein. Gegenwartslyrik verzichtet meist auf Reim und feste Formen und arbeitet stattdessen mit Bildern, Rhythmus und Zeilenumbrüchen."),
  ("Wie lese ich ein Gedicht richtig?", "Lies es erst laut und achte auf den Klang. Frage dann, welches Bild bleibt. Es gibt oft mehr als eine gültige Deutung."),
  ("Wo finde ich neue Lyrik?", "In schmalen Gedichtbänden aktueller Verlage, in Literaturzeitschriften und bei Lesungen. Auch Magazine für Text und Musik stellen neue Stimmen vor."),
  ("Ist Rap auch Lyrik?", "Im weiteren Sinn ja. Rap nutzt Reim, Rhythmus und Bildsprache wie Lyrik. Die Grenze zwischen Liedtext und Gedicht ist fließend."),
 ],
))

for a in articles:
    render_article(a, articles)

# ---------------- blog index ----------------
cards = "\n".join(
 f'''      <a class="blogcard" href="/blog/{a['slug']}">
        <img src="{a['hero']}" alt="{html.escape(a['title'])}" loading="lazy">
        <span class="kicker">{a['kicker']}</span>
        <h3>{html.escape(a['title'])}</h3>
        <p>{html.escape(a['desc'])}</p>
      </a>''' for a in articles
)
index_schema = {
 "@context": "https://schema.org", "@type": "Blog", "name": "Das Wetter Journal",
 "url": BASE + "/blog", "inLanguage": "de",
 "publisher": {"@type": "Organization", "name": "Das Wetter", "url": BASE},
 "blogPost": [
   {"@type": "BlogPosting", "headline": a["title"], "url": f"{BASE}/blog/{a['slug']}",
    "datePublished": TODAY, "image": f"{BASE}{a['hero']}"} for a in articles
 ],
}
idx = head("Journal | Das Wetter", "Texte über Musik, Lyrik und alles dazwischen. Das Journal von Das Wetter, dem Magazin für Text und Musik.", "", articles[0]["hero"], og_type="website")
idx += '<script type="application/ld+json">' + json.dumps(index_schema, ensure_ascii=False) + '</script>\n'
idx += f'''  <nav class="breadcrumb"><a href="/">Start</a> / Journal</nav>
  <div class="blogwrap">
    <h1 class="bolfont" style="font-size:34px;margin-bottom:6px">Journal</h1>
    <p class="fs-1" style="color:#555;margin-bottom:26px">Texte über Musik, Lyrik und alles dazwischen.</p>
    <div class="bloglist">
{cards}
    </div>
  </div>
</div>
{FOOTER}
</body>
</html>'''
open("site/blog.html", "w").write(idx)

# ---------------- sitemap ----------------
today = datetime.date.today().isoformat()
urls = [("/", "1.0"), ("/blog", "0.9")]
for a in articles:
    urls.append((f"/blog/{a['slug']}", "0.8"))
for f in sorted(glob.glob("site/products/*.html")):
    urls.append(("/products/" + os.path.basename(f)[:-5], "0.7"))
urls.append(("/zitat", "0.3"))
items = "\n".join(
 f"  <url>\n    <loc>{BASE}{p}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>{pr}</priority>\n  </url>"
 for p, pr in urls)
open("site/sitemap.xml", "w").write(
 '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
 + items + "\n</urlset>\n")

print("articles:", len(articles), "| sitemap urls:", len(urls))
print("done")
