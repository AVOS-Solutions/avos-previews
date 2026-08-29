// Screenshot tool: Chromium renders pages whose resources are fetched by Node
// through the agent proxy (Chromium's own network path is blocked).
// Usage: node shot.js <jobs.json> <outdir> [concurrency]
// jobs.json: [{"slug":"01-foo","url":"http://..."}]
const { chromium } = require('playwright');
const { ProxyAgent } = require('undici');
const undici = require('undici');
const fs = require('fs');
const path = require('path');

const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const outdir = process.argv[3];
const CONC = parseInt(process.argv[4] || '4', 10);
fs.mkdirSync(outdir, { recursive: true });

const pa = new ProxyAgent(process.env.HTTPS_PROXY || 'http://127.0.0.1:43137');

async function proxyFetch(url, headers) {
  let u = url;
  for (let hop = 0; hop < 8; hop++) {
    const resp = await undici.fetch(u, {
      ...(u.startsWith('https:') ? { dispatcher: pa } : {}),
      headers: {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36',
        'accept': headers['accept'] || '*/*',
        'accept-language': 'de-AT,de;q=0.9,en;q=0.5',
      },
      redirect: 'manual',
      signal: AbortSignal.timeout(25000),
    });
    if ([301, 302, 303, 307, 308].includes(resp.status)) {
      const loc = resp.headers.get('location');
      if (loc) { u = new URL(loc, u).href; continue; }
    }
    return resp;
  }
  throw new Error('too many redirects');
}

async function shootOne(browser, job) {
  const file = path.join(outdir, job.slug + '.jpg');
  if (fs.existsSync(file)) return 'cached';
  const ctx = await browser.newContext({
    viewport: { width: 1280, height: 960 },
    deviceScaleFactor: 1,
    ignoreHTTPSErrors: true,
    locale: 'de-AT',
  });
  try {
    const page = await ctx.newPage();
    await page.route('**/*', async (route) => {
      const req = route.request();
      const u = req.url();
      if (!/^https?:/.test(u)) return route.abort();
      if (/google-analytics|googletagmanager|doubleclick|facebook\.net|hotjar|matomo|cookiebot|usercentrics|consent/i.test(u)) {
        return route.abort();
      }
      try {
        const resp = await proxyFetch(u, req.headers());
        const body = Buffer.from(await resp.arrayBuffer());
        const ct = resp.headers.get('content-type') || 'application/octet-stream';
        await route.fulfill({ status: resp.status, contentType: ct, body });
      } catch (e) {
        try { await route.abort(); } catch (_) {}
      }
    });
    await page.goto(job.url, { timeout: 40000, waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2500);
    // try to close trivial cookie banners
    try {
      for (const sel of ['text=/^(Akzeptieren|Alle akzeptieren|Zustimmen|OK|Verstanden|Einverstanden|Accept)/i']) {
        const el = page.locator(sel).first();
        if (await el.isVisible({ timeout: 500 }).catch(() => false)) {
          await el.click({ timeout: 1000 }).catch(() => {});
          await page.waitForTimeout(600);
        }
      }
    } catch (_) {}
    await page.screenshot({ path: file, type: 'jpeg', quality: 78 });
    return 'ok';
  } finally {
    await ctx.close().catch(() => {});
  }
}

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium',
    args: ['--no-sandbox', '--disable-gpu'],
  });
  let i = 0, ok = 0, fail = 0;
  const results = {};
  async function worker() {
    while (i < jobs.length) {
      const job = jobs[i++];
      try {
        const r = await shootOne(browser, job);
        results[job.slug] = r; ok++;
        console.log(`[${i}/${jobs.length}] ok ${job.slug}`);
      } catch (e) {
        results[job.slug] = 'fail: ' + String(e.message || e).split('\n')[0];
        fail++;
        console.log(`[${i}/${jobs.length}] FAIL ${job.slug}: ${String(e.message || e).split('\n')[0]}`);
      }
    }
  }
  await Promise.all(Array.from({ length: CONC }, worker));
  fs.writeFileSync(path.join(outdir, '_results.json'), JSON.stringify(results, null, 1));
  console.log(`DONE ok=${ok} fail=${fail}`);
  await browser.close();
})();
