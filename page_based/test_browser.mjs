// test_browser.mjs -- the app in a REAL browser.
//
// The other two suites cannot see layout: test_app.mjs runs the app's script
// against a DOM shim, and audit_app.py only reads the markup. This one drives
// Chrome and checks the things that only exist once the CSS is applied --
// where a rail actually sits, whether a box's scrollbar is visible, whether the
// portrait flip really turns the arrows sideways.
//
// Chrome for Testing comes from the Playwright cache; the MCP browser server
// looks for a Google Chrome install that is not present here. Start the app
// first:  python3 -m http.server 8099
//
// Run:  node test_browser.mjs
import { chromium } from '/opt/homebrew/lib/node_modules/openclaw/node_modules/playwright-core/index.mjs';

const EXEC = process.env.HOME +
  '/Library/Caches/ms-playwright/chromium-1243/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing';
const URL = 'http://localhost:8099/index.html';

let pass = 0, fail = 0;
const ok = (n, c, extra='') => { if (c) { pass++; console.log('  PASS  ' + n); }
  else { fail++; console.log('  FAIL  ' + n + (extra ? '  -> ' + extra : '')); } };
const sec = t => console.log('\n' + t);

const browser = await chromium.launch({ executablePath: EXEC, headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 950 } });
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });

await page.goto(URL, { waitUntil: 'load', timeout: 120000 });
// Wait for the data to land and the app to paint a placeholder/stats.
await page.waitForFunction(() => document.getElementById('entryStats') &&
  document.getElementById('entryStats').textContent.length > 0, { timeout: 120000 });

const appErrors = () => errors.filter(e => !/favicon|net::ERR_|Failed to load resource/i.test(e));
sec('Page load');
ok('no uncaught JS errors', appErrors().length === 0, appErrors().slice(0,3).join(' | '));
ok('the three rails are all present',
   await page.locator('#guideRail').count() === 1 &&
   await page.locator('#bmRail').count() === 1 &&
   await page.locator('#chartsPanel').count() === 1);
const openByDefault = await page.evaluate(() =>
  !document.getElementById('guideRail').classList.contains('collapsed') &&
  !document.getElementById('bmRail').classList.contains('collapsed') &&
  !document.getElementById('chartsPanel').classList.contains('collapsed'));
ok('all three rails open by default', openByDefault);

sec('DRASTIC mark');
const brand = page.locator('.header-brand img');
ok('the logo is visible in the header', await brand.count() === 1 && await brand.isVisible());
const nat = await brand.evaluate(el => ({ w: el.naturalWidth, h: el.naturalHeight }));
ok('the logo image actually loaded (not a broken img)', nat.w > 0 && nat.h > 0,
   JSON.stringify(nat));
const box = await brand.boundingBox();
const vw = page.viewportSize().width;
ok('the logo sits at the top right', box && (box.x + box.width) > vw * 0.6,
   box ? 'x=' + Math.round(box.x) + ' w=' + Math.round(box.width) + ' vw=' + vw : 'no box');

sec('Bookmarks rail geometry (landscape)');
const bm = await page.locator('#bmRail').boundingBox();
const guide = await page.locator('#guideRail').boundingBox();
ok('the rail is a vertical column (tall, narrow)', bm.height > 500 && bm.width < 400,
   Math.round(bm.width) + 'x' + Math.round(bm.height));
ok('it stands to the left of the guide rail', bm.x < guide.x,
   'guide.x=' + Math.round(guide.x) + ' bm.x=' + Math.round(bm.x));
ok('the scroll arrows are stacked vertically', await page.evaluate(() => {
  const a = document.getElementById('bmUp').getBoundingClientRect();
  const b = document.getElementById('bmDown').getBoundingClientRect();
  return b.top > a.top && Math.abs(a.x - b.x) < 2 && (b.top - a.top) < a.height + 4;
}));

sec('Bookmarks toggle round trip');
await page.fill('#searchInput', 'passaging');
await page.keyboard.press('Enter');
await page.waitForFunction(() => document.querySelectorAll('.result-entry').length > 0,
  { timeout: 60000 });
const nRes = await page.locator('.result-entry').count();
ok('the search produced result boxes', nRes > 0, nRes + ' boxes');
ok('every box has a bookmark toggle',
   await page.locator('.result-entry [data-bm-toggle]').count() === nRes);
await page.locator('.result-entry [data-bm-toggle]').first().click();
const afterOne = await page.evaluate(() => ({
  n: document.querySelectorAll('.bm-item').length,
  on: document.querySelectorAll('.bm-toggle.on').length,
  txt: (document.querySelector('.bm-item .bm-t') || {}).textContent
}));
ok('clicking the toggle adds a bookmark to the rail', afterOne.n === 1, JSON.stringify(afterOne));
ok('the toggle shows as active', afterOne.on === 1);
ok('the bookmark carries a recognisable label',
   afterOne.txt && afterOne.txt.length > 3, String(afterOne.txt));
await page.locator('.bm-item').first().click();
await page.waitForTimeout(600);
ok('clicking the bookmark activates a box',
   await page.locator('.result-entry.active').count() >= 1);
// Toggle off the bookmarked box specifically (by key), not "whatever is first",
// because jumping re-rendered the list.
const bmKey = await page.evaluate(() => (document.querySelector('.bm-toggle.on')||{}).dataset
  ? document.querySelector('.bm-toggle.on').dataset.bmToggle : null);
await page.locator('[data-bm-toggle="' + bmKey + '"]').first().click();
const afterTwo = await page.evaluate(() => ({
  n: document.querySelectorAll('.bm-item').length,
  on: document.querySelectorAll('.bm-toggle.on').length }));
ok('clicking again removes it', afterTwo.n === 0 && afterTwo.on === 0, JSON.stringify(afterTwo));

sec('Bookmark persistence');
await page.locator('.result-entry [data-bm-toggle]').first().click();
await page.reload({ waitUntil: 'load' });
await page.waitForFunction(() => document.getElementById('entryStats') &&
  document.getElementById('entryStats').textContent.length > 0, { timeout: 120000 });
ok('the bookmark survives a reload',
   await page.locator('.bm-item').count() === 1);

sec('Portrait layout');
await page.click('#layoutToggle');
await page.waitForTimeout(700);
const bmP = await page.locator('#bmRail').boundingBox();
ok('in portrait the rail becomes a wide, short strip',
   bmP.width > 600 && bmP.height < 260,
   Math.round(bmP.width) + 'x' + Math.round(bmP.height));
ok('the arrows turn horizontal (side by side)', await page.evaluate(() => {
  const a = document.getElementById('bmUp').getBoundingClientRect();
  const b = document.getElementById('bmDown').getBoundingClientRect();
  return b.x > a.x && Math.abs(a.y - b.y) < 3;
}));
await page.click('#layoutToggle');
await page.waitForTimeout(700);

sec('Collapsing');
await page.click('#bmToggleBtn');
await page.waitForTimeout(400);
const collapsed = await page.locator('#bmRail').boundingBox();
ok('a collapsed rail is a thin strip, still on screen',
   collapsed.width < 60 && collapsed.height > 300,
   Math.round(collapsed.width) + 'x' + Math.round(collapsed.height));
ok('the collapsed chevron points back (landscape: right)',
   (await page.locator('#bmToggleBtn').textContent()).trim() === '▶');
await page.click('#bmToggleBtn');
await page.waitForTimeout(400);
ok('it re-opens', (await page.locator('#bmRail').boundingBox()).width > 100);

sec('Large boxes: scrolling and Full text');
await page.fill('#searchInput', 'passaging');
await page.keyboard.press('Enter');
await page.waitForFunction(() => document.querySelectorAll('.result-entry').length > 0, { timeout: 60000 });
const boxScroll = await page.evaluate(() => {
  // A box only scrolls if it is clipped, so measure one that actually is:
  // taking the first result can pick a short one whose bar is correctly hidden.
  const boxes = [...document.querySelectorAll('.result-content')];
  const box = boxes.find(b => b.scrollHeight > b.clientHeight + 4);
  if (!box) return { none: true, total: boxes.length };
  const bar = box.parentElement.querySelector('.box-scrollbar');
  return {
    overflows: true,
    barVisible: !!bar && getComputedStyle(bar).display !== 'none',
    overflowY: getComputedStyle(box).overflowY
  };
});
ok('a long box scrolls internally', boxScroll && boxScroll.overflowY !== 'visible',
   JSON.stringify(boxScroll));
ok('the always-visible box scrollbar is shown', boxScroll && boxScroll.barVisible,
   JSON.stringify(boxScroll));

sec('Guide: alphabetical + clickable PDFs');
// Pick a section that actually cites documents -- early sections have none.
const secIdx = await page.evaluate(() => {
  // Must be > 0: every section prints "N citations", including the zeroes.
  const secs = [...document.querySelectorAll('.guide-sec')];
  return secs.findIndex(s => {
    const m = s.textContent.match(/(\d+) citations/);
    return m && Number(m[1]) > 0;
  });
});
ok('a section with citations exists', secIdx >= 0, String(secIdx));
await page.locator('.guide-sec').nth(secIdx).click();
await page.waitForTimeout(500);
const gd = await page.evaluate(() => {
  const names = [...document.querySelectorAll('#guideDetail .gd-doc')]
    .map(e => e.textContent.trim());
  const key = t => t.toLowerCase().replace(/[^a-z0-9]+/g, ' ');
  const sorted = names.slice().sort((a,b) => key(a) < key(b) ? -1 : key(a) > key(b) ? 1 : 0);
  return { names, isSorted: JSON.stringify(names) === JSON.stringify(sorted),
           clickable: document.querySelectorAll('#guideDetail [data-guide-pdf]').length };
});
ok('the guide detail lists its documents', gd.names.length > 0, JSON.stringify(gd.names.slice(0,4)));
ok('the documents are in alphabetical order', gd.isSorted, JSON.stringify(gd.names));
// Most cited documents are NOT held as PDFs, so check across sections rather
// than only the one that was clicked.
const clickable = await page.evaluate(() => {
  let n = 0;
  for (const s of document.querySelectorAll('.guide-sec')) {
    s.click();
    n += document.querySelectorAll('#guideDetail [data-guide-pdf]').length;
  }
  return n;
});
ok('some cited documents are clickable PDF links', clickable > 0, String(clickable));
// Re-open a section that has one, and use it.
const withLink = await page.evaluate(() => {
  const secs = [...document.querySelectorAll('.guide-sec')];
  for (const s of secs) {
    s.click();
    if (document.querySelector('#guideDetail [data-guide-pdf]')) return true;
  }
  return false;
});
ok('a section with a clickable document exists', withLink);
if (withLink) {
  await page.locator('#guideDetail [data-guide-pdf]').first().click();
  await page.waitForTimeout(2500);
  ok('clicking it opens a PDF in the reading area',
     await page.evaluate(() => {
       const l = document.getElementById('pdfSourceLabel');
       const c = document.getElementById('pdfCanvas');
       return l && c && c.width > 0;
     }), await page.locator('#pdfSourceLabel').textContent());
}

sec('Email formatting');
await page.evaluate(() => { kindFilter = ['email']; doSearch(); });
await page.fill('#searchInput', 'call');
await page.keyboard.press('Enter');
await page.waitForFunction(() => document.querySelectorAll('.result-entry').length > 3,
  { timeout: 60000 });
await page.waitForTimeout(800);
const mail = await page.evaluate(() => {
  // Again, measure a card that has the thing under test.
  const cards = [...document.querySelectorAll('.result-entry')];
  const card = cards.find(c => /Subject:\s*\S/.test(
    (c.querySelector('.mail-head') || {}).textContent || '')) || cards[0];
    const t = (card ? card.querySelector('.result-content') : {}).textContent || '';
    const head = (card ? card.querySelector('.mail-head') : {}).textContent || '';
  return {
    // textContent has no newlines between the header fields, so match the
    // label inline rather than with a line anchor.
    subjectInHead: /Subject:\s*\S/.test(head),
    subjectLeakedInBody: /(^|\n)Subject: /.test(t.split('----------')[1] || ''),
    ceLeftover: /(^|\n)Ce: /.test(t)
  };
});
ok('the email card shows Subject in its header block', mail.subjectInHead);
ok('the Subject no longer leaks into the body', !mail.subjectLeakedInBody);
ok('no OCR "Ce:" remains', !mail.ceLeftover);

sec('Consoles');
const realErrors = errors.filter(e => !/favicon|net::ERR_|Failed to load resource/i.test(e));
ok('still no uncaught JS errors at the end', realErrors.length === 0,
   realErrors.slice(0,3).join(' | '));

await browser.close();
console.log('\n' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
