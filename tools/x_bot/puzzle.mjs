// Reads a day's Daily from the game itself, so the bot always posts the same hole players see.
// Loads index.html from this checkout in headless Chromium and blocks every outside request
// (so the bot never bumps the visit counters).
import { chromium } from "playwright";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("../..", import.meta.url));
const TYPES = { ".html": "text/html", ".json": "application/json", ".js": "text/javascript", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webmanifest": "application/manifest+json" };

function serve() {
  const srv = createServer(async (req, res) => {
    let p = normalize(decodeURIComponent(new URL(req.url, "http://x").pathname));
    if (p.endsWith("/")) p += "index.html";
    try {
      const body = await readFile(join(ROOT, p));
      res.writeHead(200, { "content-type": TYPES[extname(p)] || "application/octet-stream" }).end(body);
    } catch { res.writeHead(404).end(); }
  });
  return new Promise(ok => srv.listen(0, "127.0.0.1", () => ok(srv)));
}

// date: "YYYY-MM-DD" (Eastern). Omit for today.
export async function getDaily(date) {
  const srv = await serve();
  const base = `http://127.0.0.1:${srv.address().port}/`;
  const browser = await chromium.launch(process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {});
  try {
    const page = await browser.newPage();
    await page.route("**/*", r => (r.request().url().startsWith(base) ? r.continue() : r.abort()));
    await page.goto(base);
    await page.waitForFunction(() => typeof P !== "undefined" && P && S.hole, null, { timeout: 60000 });
    return await page.evaluate(d => {
      d = d || etDate();
      startDaily(d);
      const h = S.hole, name = i => P[i][0];
      return { date: d, n: dayNum(d), label: h.meta.label || "", tee: name(h.a), pin: name(h.b), par: h.par, best: h.best, url: BASE_URL };
    }, date || null);
  } finally {
    await browser.close();
    srv.close();
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  console.log(JSON.stringify(await getDaily(process.argv[2]), null, 2));
}
