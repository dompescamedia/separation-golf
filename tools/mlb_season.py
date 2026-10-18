# Pull one regular season from the MLB Stats API into raw/<season>/: teams, every player's
# hitting and pitching lines (one split per team for traded players) and bios. Run by the
# 'Pull MLB season' Action; tools/add_season.py folds the files into data.json and the cards.
import json, os, sys, time, urllib.request
SEASON = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
API = "https://statsapi.mlb.com/api/v1/"
def get(path):
    for i in range(5):
        try:
            req = urllib.request.Request(API + path, headers={"User-Agent": "separation-golf data refresh"})
            return json.load(urllib.request.urlopen(req, timeout=60))
        except Exception as e:
            print("retry", path, e); time.sleep(2 + 3 * i)
    raise SystemExit("failed " + path)
out = f"raw/{SEASON}"; os.makedirs(out, exist_ok=True)
teams = get(f"teams?sportId=1&season={SEASON}")["teams"]
json.dump(teams, open(f"{out}/teams.json", "w"), indent=0)
ids = set()
for group in ["hitting", "pitching"]:
    splits, off = [], 0
    while True:
        r = get(f"stats?stats=season&group={group}&gameType=R&season={SEASON}&sportId=1&playerPool=ALL&limit=1000&offset={off}")
        s = r["stats"][0]["splits"] if r.get("stats") else []
        splits += s
        if len(s) < 1000: break
        off += 1000
    # Traded players: ask for their per-team lines too.
    multi = sorted({x["player"]["id"] for x in splits if x.get("numTeams", 1) > 1 or "team" not in x})
    per_team = {}
    for pid in multi:
        r = get(f"people/{pid}/stats?stats=yearByYear&group={group}&gameType=R&sportId=1")
        per_team[pid] = [x for x in r["stats"][0]["splits"] if int(x["season"]) == SEASON] if r.get("stats") else []
    json.dump({"splits": splits, "per_team": per_team}, open(f"{out}/{group}.json", "w"), separators=(",", ":"))
    ids |= {x["player"]["id"] for x in splits}
    print(group, len(splits), "splits,", len(multi), "multi-team")
people = []
ids = sorted(ids)
for i in range(0, len(ids), 100):
    people += get("people?personIds=" + ",".join(map(str, ids[i:i + 100])))["people"]
json.dump(people, open(f"{out}/people.json", "w"), separators=(",", ":"))
print(len(people), "people")
