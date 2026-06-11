// Captures a snapshot of wetter-magazin.com (HTML, CSS, image metadata,
// products.json, full-page screenshots) and, if a rebuild exists in site/,
// screenshots the rebuild too so both can be compared.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import http from 'http';

const OUT = '_snapshot';
const BASE = 'https://wetter-magazin.com';

const PAGES = [
  ['home', '/'],
  ['hefte', '/collections/hefte'],
  ['about', '/pages/about'],
];

for (const d of ['html', 'assets', 'shots']) {
  fs.mkdirSync(path.join(OUT, d), { recursive: true });
}

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  userAgent:
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
  locale: 'de-DE',
});
const page = await ctx.newPage();

const assetUrls = new Set();
page.on('response', (res) => {
  const url = res.url();
  const ct = (res.headers()['content-type'] || '').toLowerCase();
  if (ct.includes('text/css') || /\.css(\?|$)/.test(url)) assetUrls.add(url);
  if (/\.(woff2?|ttf|otf)(\?|$)/.test(url)) assetUrls.add(url);
});

// dump geometry + computed styles of key elements for layout comparison
async function dumpLayout(pg, file) {
  const data = await pg.evaluate(() => {
    const sels = [
      'body', '.Index', '.IndexHeader', '.HeaderBasic', '.HeaderTop',
      '.ausgaben a', '.title', '.menubutton', '.logowrap', '.logo', '.logo svg',
      '#shopify-section-AktuelleAusgabe', '.StartAktuelleAusgabe',
      '.StartAktuelleAusgabe .text', '.slideshow', '.slick-list',
      '.StartContentGrid', '.StartContentGrid img', '.newsletterwrapper',
      '.newsletterinput', '.newsletter__submit', '#shopify-section-StartCollection',
      '.IndexGrid', '.IndexItem', '.IndexItem img', '.ProductCardInfo',
      '.footerwrap', 'footer', '.footermenu a',
    ];
    const out = { scroll: { w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight } };
    for (const s of sels) {
      const el = document.querySelector(s);
      if (!el) { out[s] = null; continue; }
      const r = el.getBoundingClientRect();
      const c = getComputedStyle(el);
      out[s] = {
        rect: { x: Math.round(r.x), y: Math.round(r.y + scrollY), w: Math.round(r.width), h: Math.round(r.height) },
        position: c.position, display: c.display, color: c.color,
        background: c.backgroundColor, fontSize: c.fontSize, fontFamily: c.fontFamily.slice(0, 40),
        zIndex: c.zIndex,
      };
    }
    return out;
  });
  fs.writeFileSync(file, JSON.stringify(data, null, 1));
}

const imageReport = [];
for (const [name, p] of PAGES) {
  try {
    await page.goto(BASE + p, { waitUntil: 'networkidle', timeout: 90000 });
  } catch (e) {
    console.log(`goto ${p}: ${e.message}`);
  }
  await page.waitForTimeout(2500);
  // scroll through the page so lazy-loaded content appears
  await page.evaluate(async () => {
    for (let y = 0; y < document.body.scrollHeight; y += 700) {
      window.scrollTo(0, y);
      await new Promise((r) => setTimeout(r, 150));
    }
    window.scrollTo(0, 0);
  });
  await page.waitForTimeout(1500);

  fs.writeFileSync(path.join(OUT, 'html', `${name}.html`), await page.content());
  await page.screenshot({
    path: path.join(OUT, 'shots', `original-${name}.png`),
    fullPage: true,
  });
  if (name === 'home') await dumpLayout(page, path.join(OUT, 'layout-original.json'));

  const imgs = await page.evaluate(() =>
    [...document.querySelectorAll('img')].map((i) => ({
      src: i.currentSrc || i.src,
      alt: i.alt,
      width: i.naturalWidth,
      height: i.naturalHeight,
      class: i.className,
    }))
  );
  imageReport.push({ page: name, images: imgs });
}
fs.writeFileSync(path.join(OUT, 'images.json'), JSON.stringify(imageReport, null, 2));

// download every referenced image so the originals can be reviewed offline
fs.mkdirSync(path.join(OUT, 'images'), { recursive: true });
const seen = new Set();
for (const pg of imageReport) {
  for (const im of pg.images) {
    if (!im.src || im.src.startsWith('data:')) continue;
    const u = im.src.startsWith('//') ? 'https:' + im.src : im.src;
    const fn = (u.split('/').pop() || 'img').split('?')[0].slice(0, 120);
    if (seen.has(fn)) continue;
    seen.add(fn);
    try {
      const resp = await ctx.request.get(u);
      fs.writeFileSync(path.join(OUT, 'images', fn), Buffer.from(await resp.body()));
    } catch (e) {
      console.log(`image ${u}: ${e.message}`);
    }
  }
}

// download stylesheets / fonts seen on the network
for (const u of assetUrls) {
  try {
    const r = await ctx.request.get(u);
    const fn = (u.split('/').pop() || 'asset').split('?')[0].slice(0, 120);
    fs.writeFileSync(path.join(OUT, 'assets', fn), Buffer.from(await r.body()));
  } catch (e) {
    console.log(`asset ${u}: ${e.message}`);
  }
}

// Shopify product data (titles, prices, image alts)
try {
  const r = await ctx.request.get(`${BASE}/products.json?limit=250`);
  fs.writeFileSync(path.join(OUT, 'products.json'), await r.text());
} catch (e) {
  console.log(`products.json: ${e.message}`);
}

// screenshot the rebuild, if present
if (fs.existsSync('site/index.html')) {
  const server = http
    .createServer((req, res) => {
      const clean = req.url.split('?')[0];
      let f = path.join('site', clean === '/' ? 'index.html' : clean.slice(1));
      if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
      if (fs.existsSync(f) && fs.statSync(f).isFile()) {
        const mime =
          {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'text/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp',
            '.woff2': 'font/woff2',
          }[path.extname(f)] || 'application/octet-stream';
        res.setHeader('content-type', mime);
        res.end(fs.readFileSync(f));
      } else {
        res.statusCode = 404;
        res.end('not found');
      }
    })
    .listen(8788);

  const rebuildPages = [['home', '/']];
  for (const [name, p] of [
    ...rebuildPages,
    ...(fs.existsSync('site/collections/hefte/index.html') ? [['hefte', '/collections/hefte/']] : []),
    ...(fs.existsSync('site/pages/about/index.html') ? [['about', '/pages/about/']] : []),
  ]) {
    const rp = await ctx.newPage();
    await rp.goto(`http://localhost:8788${p}`, { waitUntil: 'networkidle', timeout: 30000 });
    await rp.waitForTimeout(1000);
    await rp.screenshot({
      path: path.join(OUT, 'shots', `rebuild-${name}.png`),
      fullPage: true,
    });
    if (name === 'home') await dumpLayout(rp, path.join(OUT, 'layout-rebuild.json'));
    await rp.close();
  }
  server.close();
}

await browser.close();
console.log('snapshot complete');
