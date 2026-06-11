// Loads the live Vercel deployment, checks for broken images, failed network
// requests, and console errors, screenshots it, and writes a report.
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const URL = process.env.CHECK_URL || 'https://wetteristimmer.vercel.app/';
const OUT = '_vercelcheck';
fs.mkdirSync(OUT, { recursive: true });

const consoleErrors = [];
const failedRequests = [];
const responses = [];

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await ctx.newPage();

page.on('console', (m) => {
  if (m.type() === 'error') consoleErrors.push(m.text());
});
page.on('requestfailed', (r) => {
  failedRequests.push({ url: r.url(), error: r.failure()?.errorText });
});
page.on('response', (r) => {
  const s = r.status();
  if (s >= 400) responses.push({ url: r.url(), status: s });
});

let mainStatus = null;
let gotoError = null;
try {
  const resp = await page.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });
  mainStatus = resp ? resp.status() : null;
} catch (e) {
  gotoError = e.message;
}
await page.waitForTimeout(3000);

// scroll to trigger any lazy assets
await page.evaluate(async () => {
  for (let y = 0; y < document.body.scrollHeight; y += 800) {
    window.scrollTo(0, y);
    await new Promise((r) => setTimeout(r, 120));
  }
  window.scrollTo(0, 0);
});
await page.waitForTimeout(1500);

const imgReport = await page.evaluate(() =>
  [...document.querySelectorAll('img')].map((i) => ({
    src: i.getAttribute('src'),
    ok: i.complete && i.naturalWidth > 0,
    w: i.naturalWidth,
    h: i.naturalHeight,
  }))
);
const brokenImages = imgReport.filter((i) => !i.ok);

const title = await page.title();
const vercelAnalytics = responses.concat([]).length; // placeholder
const hasInsights = await page.evaluate(() =>
  [...document.scripts].some((s) => s.src.includes('/_vercel/insights/'))
);
const hasSpeed = await page.evaluate(() =>
  [...document.scripts].some((s) => s.src.includes('/_vercel/speed-insights/'))
);

await page.screenshot({ path: path.join(OUT, 'vercel-home.png'), fullPage: true });

const report = {
  url: URL,
  checkedAt: new Date().toISOString(),
  mainStatus,
  gotoError,
  title,
  totalImages: imgReport.length,
  brokenImageCount: brokenImages.length,
  brokenImages,
  failedRequests,
  httpErrorResponses: responses,
  consoleErrors,
  trackingScriptsPresent: { webAnalytics: hasInsights, speedInsights: hasSpeed },
};
fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));

console.log('=== VERCEL CHECK ===');
console.log('status:', mainStatus, '| title:', title);
console.log('images:', imgReport.length, '| broken:', brokenImages.length);
console.log('failed requests:', failedRequests.length, '| http>=400:', responses.length);
console.log('console errors:', consoleErrors.length);

await browser.close();
