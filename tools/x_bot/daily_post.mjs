// Posts today's Daily hole to X. Without the X_* secrets it prints the post instead (dry run).
import { getDaily } from "./puzzle.mjs";
import { canPost, post } from "./x.mjs";

const d = await getDaily(process.argv[2]);
// A link costs more per API post ($0.20 vs $0.015 as of Oct 2026); set X_NO_LINK=1 to leave it to the bio.
const link = process.env.X_NO_LINK ? "" : d.url;
const text = [
  `⛳ Separation Golf · Daily #${d.n}`,
  d.label,
  `${d.tee} → ${d.pin}`,
  `Par ${d.par}. Get there through teammates in as few strokes as you can.`,
  link,
].filter(Boolean).join("\n");

console.log(text + "\n");
if (!canPost() || process.env.DRY_RUN) { console.log("(dry run: nothing posted)"); process.exit(0); }
const r = await post(text);
console.log(`Posted: https://x.com/i/web/status/${r.data.id}`);
