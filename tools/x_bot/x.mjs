// Minimal X API v2 client: post as the account (OAuth 1.0a user context) and recent search (app bearer token).
// Keys come from environment variables only (GitHub Actions secrets). Never commit them.
import { createHmac, randomBytes } from "node:crypto";

const API = "https://api.x.com/2";
const enc = s => encodeURIComponent(s).replace(/[!'()*]/g, c => "%" + c.charCodeAt(0).toString(16).toUpperCase());

export const canPost = () => ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"].every(k => process.env[k]);
export const canSearch = () => !!process.env.X_BEARER_TOKEN;

function oauthHeader(method, url) {
  const e = process.env;
  const o = {
    oauth_consumer_key: e.X_API_KEY, oauth_nonce: randomBytes(16).toString("hex"),
    oauth_signature_method: "HMAC-SHA1", oauth_timestamp: String(Math.floor(Date.now() / 1000)),
    oauth_token: e.X_ACCESS_TOKEN, oauth_version: "1.0",
  };
  // JSON bodies are not part of the signature, so only the oauth_* params are signed.
  const params = Object.keys(o).sort().map(k => `${enc(k)}=${enc(o[k])}`).join("&");
  const base = [method, enc(url), enc(params)].join("&");
  o.oauth_signature = createHmac("sha1", `${enc(e.X_API_SECRET)}&${enc(e.X_ACCESS_SECRET)}`).update(base).digest("base64");
  return "OAuth " + Object.keys(o).sort().map(k => `${enc(k)}="${enc(o[k])}"`).join(", ");
}

async function check(res) {
  const body = await res.text();
  if (!res.ok) throw new Error(`X API ${res.status}: ${body}`);
  return JSON.parse(body);
}

export async function post(text, replyTo) {
  const url = `${API}/tweets`;
  const body = { text };
  if (replyTo) body.reply = { in_reply_to_tweet_id: replyTo };
  return check(await fetch(url, { method: "POST", headers: { authorization: oauthHeader("POST", url), "content-type": "application/json" }, body: JSON.stringify(body) }));
}

// Each post returned is billed as a read, so keep max small.
export async function search(query, max = 10) {
  const q = new URLSearchParams({
    query, max_results: String(Math.max(10, Math.min(100, max))), sort_order: "relevancy",
    "tweet.fields": "public_metrics,created_at,author_id", expansions: "author_id", "user.fields": "username,name",
  });
  const j = await check(await fetch(`${API}/tweets/search/recent?${q}`, { headers: { authorization: `Bearer ${process.env.X_BEARER_TOKEN}` } }));
  const users = new Map((j.includes?.users || []).map(u => [u.id, u]));
  return (j.data || []).map(t => ({ ...t, user: users.get(t.author_id) }));
}
