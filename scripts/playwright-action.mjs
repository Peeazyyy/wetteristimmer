// Flexible Playwright helper used to (a) submit the live newsletter form to
// trigger FormSubmit activation, and (b) visit the activation link — both need
// a real browser to pass Cloudflare's challenge.
import { chromium } from 'playwright';

const MODE = process.env.MODE || 'visit';
const URL = process.env.TARGET_URL || 'https://www.wetteristimmer.com/';
const EMAIL = process.env.EMAIL || 'aktivierung@wetteristimmer.com';

const browser = await chromium.launch();
const ctx = await browser.newContext({
  viewport: { width: 1280, height: 900 },
  userAgent:
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
  locale: 'de-DE',
});
const page = await ctx.newPage();

async function dump(tag) {
  const txt = (await page.evaluate(() => document.body ? document.body.innerText : '')).slice(0, 600);
  console.log(`=== ${tag} ===`);
  console.log('URL:', page.url());
  console.log('TITLE:', await page.title());
  console.log('BODY:', txt.replace(/\n+/g, ' | '));
}

try {
  await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(3000);

  if (MODE === 'submit') {
    await page.fill('input[name="email"]', EMAIL);
    await Promise.all([
      page.waitForLoadState('networkidle', { timeout: 60000 }).catch(() => {}),
      page.click('button[type="submit"]'),
    ]);
    await page.waitForTimeout(6000);
    await dump('AFTER SUBMIT');
  } else {
    await page.waitForTimeout(4000);
    await dump('VISITED');
  }
} catch (e) {
  console.log('ERROR:', e.message);
  await dump('ON ERROR');
}

await browser.close();
