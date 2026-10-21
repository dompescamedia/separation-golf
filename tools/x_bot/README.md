# X bot

- `daily_post.mjs` posts the day's Daily hole (`.github/workflows/x-daily-post.yml`, 13:00 UTC).
- `reply_ideas.mjs` searches recent posts about the day's tee and pin and lists draft replies with one-click links. Dom sends them by hand. It never replies itself, because X bans automated replies to accounts that did not mention or opt in to the bot (`.github/workflows/x-reply-ideas.yml`, results on the run's Summary page).
- `puzzle.mjs` loads `index.html` from the checkout in headless Chromium so the bot posts exactly what the game shows. Outside requests are blocked so the bot never bumps the play counters.

Secrets (Settings > Secrets and variables > Actions, never in the repo): `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET` (posting), `X_BEARER_TOKEN` (search). Without them each script prints instead of calling X.

Optional variables: `X_NO_LINK=1` drops the link from the daily post (API posts with a link cost more); `X_SEARCH_MAX` caps posts read per search (default 20; each one is billed as a read).

Local run: `cd tools/x_bot && npm install && node daily_post.mjs [YYYY-MM-DD]`.
