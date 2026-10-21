// Finds recent X posts about today's tee and pin players and drafts a reply for each.
// It never replies on its own: X bans automated replies to people who did not mention or opt in to the account.
// Output is a Markdown list with one-click "reply" links that open X with the draft filled in, for Dom to edit and send by hand.
import { appendFile } from "node:fs/promises";
import { getDaily } from "./puzzle.mjs";
import { canSearch, search } from "./x.mjs";

const d = await getDaily(process.argv[2]);
const MAX = +(process.env.X_SEARCH_MAX || 20);
const filters = "-is:retweet -is:reply -is:nullcast lang:en";
const query = `("${d.tee}" OR "${d.pin}") ${filters}`;
const jumps = d.best - 1;

const drafts = who => [
  `Fun one: ${d.tee} to ${d.pin} is only ${jumps} teammate${jumps === 1 ? "" : "s"} apart. Today's Separation Golf hole is finding the path ⛳ ${d.url}`,
  `If you like ${who}, today's Separation Golf is ${d.tee} → ${d.pin} through shared rosters. Par ${d.par} ⛳ ${d.url}`,
];

const out = [`## Reply ideas for Daily #${d.n}: ${d.tee} → ${d.pin}`, "", `Search: \`${query}\``, ""];
if (!canSearch()) {
  out.push("_No X_BEARER_TOKEN set, so no search ran. Drafts you can use anywhere:_", "", ...drafts(d.pin).map(t => `- ${t}`));
} else {
  const posts = (await search(query, MAX)).sort((a, b) => (b.public_metrics?.like_count || 0) - (a.public_metrics?.like_count || 0));
  if (!posts.length) out.push("_No recent posts matched._");
  for (const p of posts) {
    const who = p.text.includes(d.tee) ? d.tee : d.pin;
    const m = p.public_metrics || {};
    const url = `https://x.com/${p.user?.username || "i"}/status/${p.id}`;
    out.push(`### @${p.user?.username} · ${m.like_count || 0} likes · ${m.reply_count || 0} replies`, "", "> " + p.text.replace(/\n+/g, " "), "", `[Open post](${url})`);
    for (const t of drafts(who)) {
      out.push(`- ${t}  \n  [Reply with this](https://x.com/intent/post?in_reply_to=${p.id}&text=${encodeURIComponent(t)})`);
    }
    out.push("");
  }
}
const md = out.join("\n") + "\n";
console.log(md);
if (process.env.GITHUB_STEP_SUMMARY) await appendFile(process.env.GITHUB_STEP_SUMMARY, md);
