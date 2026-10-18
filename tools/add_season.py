# Fold a season pulled by tools/mlb_season.py (raw/<season>/) into data.json and the cards:
# new team-seasons for the teammate graph, a stat row per team on each card, and new players.
import json, sys, collections
SEASON = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
R = f"raw/{SEASON}"; NS = 50
BR = {"AZ": "ARI", "CWS": "CHW", "KC": "KCR", "SD": "SDP", "SF": "SFG", "TB": "TBR", "WSH": "WSN"}
M = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
data = json.load(open("data.json")); P, TN, T, FR = data["players"], data["teamNames"], data["teams"], data["franchises"]
assert not any(t[0] == SEASON for t in T), f"{SEASON} is already in data.json"
teams = {t["id"]: t for t in json.load(open(f"{R}/teams.json"))}
people = {p["id"]: p for p in json.load(open(f"{R}/people.json"))}
# Franchise for each MLB team: the franchise of last season's team with the same name (or same nickname).
prev = {TN[t[1]]: t[3] for t in T if t[0] == SEASON - 1}
def franchise(name):
    if name in prev: return prev[name]
    nick = name.split()[-1]
    hit = [f for n, f in prev.items() if n.split()[-1] == nick or nick in n]
    assert len(hit) == 1, name
    return hit[0]
by_mlb = {p[9]: i for i, p in enumerate(P) if len(p) > 9 and p[9]}
def lines(group):
    raw = json.load(open(f"{R}/{group}.json")); out = []
    for s in raw["splits"]:
        pid = s["player"]["id"]
        if str(pid) in raw["per_team"]: out += [(pid, x) for x in raw["per_team"][str(pid)] if x.get("team")]
        elif s.get("team"): out.append((pid, s))
    return out
hit, pit = lines("hitting"), lines("pitching")
# Players already in the data whose MLB ID is missing or wrong: match on birthday plus name.
by_bday = collections.defaultdict(list)
for i, p in enumerate(P):
    if p[8] and p[2] >= SEASON - 30: by_bday[(p[7], p[8])].append(i)
fixed = []
def norm(x): return "".join(ch for ch in x.lower() if ch.isalpha())
def idx_of(pid):
    if pid in by_mlb: return by_mlb[pid]
    pe = people[pid]; fn, ln = pe.get("useName") or pe.get("firstName", ""), pe.get("useLastName") or pe.get("lastName", "")
    b = pe.get("birthDate", ""); y, m, d = (list(map(int, b.split("-"))) + [0, 0, 0])[:3] if b else (0, 0, 0)
    cand = [i for i in by_bday.get(((y + (1 if m >= 7 else 0)) if y else 0, m * 100 + d), []) if norm(P[i][0].split()[-1]) == norm(ln.split()[-1]) or norm(P[i][0]) == norm(pe["fullName"])]
    if len(cand) == 1:
        i = cand[0]
        if P[i][9]: fixed.append((P[i][0], P[i][9], pid)); by_mlb.pop(P[i][9], None)
        P[i][9] = pid; by_mlb[pid] = i; return i
    P.append([pe["fullName"], SEASON, SEASON, f"mlb{pid}", 0, 0, f"{ln} {fn}", (y + (1 if m >= 7 else 0)) if y else 0, m * 100 + d, pid, 0])
    by_mlb[pid] = len(P) - 1
    return len(P) - 1
games = collections.defaultdict(lambda: collections.defaultdict(int))  # MLB team id -> player idx -> games
cards = [json.load(open(f"cards/{k}.json")) for k in range(NS)]
def card(i):
    return cards[i % NS].setdefault(str(i), {})
def ab(team): return BR.get(teams[team]["abbreviation"], teams[team]["abbreviation"])
def outs(ip):
    w, _, f = str(ip).partition("."); return int(w or 0) * 3 + int(f or 0)
for pid, s in hit:
    i = idx_of(pid); st = s["stat"]; tm = s["team"]["id"]
    games[tm][i] = max(games[tm][i], st.get("gamesPlayed", 0))
    card(i).setdefault("b", []).append([SEASON, ab(tm), st.get("gamesPlayed", 0), st.get("atBats", 0), st.get("runs", 0), st.get("hits", 0), st.get("doubles", 0), st.get("triples", 0), st.get("homeRuns", 0), st.get("rbi", 0), st.get("stolenBases", 0), st.get("baseOnBalls", 0), st.get("strikeOuts", 0), st.get("hitByPitch", 0), st.get("sacFlies", 0)])
for pid, s in pit:
    i = idx_of(pid); st = s["stat"]; tm = s["team"]["id"]
    games[tm][i] = max(games[tm][i], st.get("gamesPitched", st.get("gamesPlayed", 0)))
    card(i).setdefault("p", []).append([SEASON, ab(tm), st.get("wins", 0), st.get("losses", 0), st.get("gamesPitched", 0), st.get("gamesStarted", 0), st.get("saves", 0), outs(st.get("inningsPitched", "0")), st.get("hits", 0), st.get("earnedRuns", 0), st.get("baseOnBalls", 0), st.get("strikeOuts", 0)])
for tm, g in games.items():
    name = teams[tm]["name"]
    if name not in TN: TN.append(name)
    T.append([SEASON, TN.index(name), sorted(g, key=lambda i: -g[i]), franchise(name)])
    for i in g:
        P[i][2] = max(P[i][2], SEASON)
for f in FR:
    if f[1] and f[3] == SEASON - 1: f[3] = SEASON
# Bios for players new this season.
for pid, i in by_mlb.items():
    c = card(i) if i < len(P) else None
    if not c or "bio" in c or pid not in people: continue
    pe = people[pid]; bio = {"pos": pe.get("primaryPosition", {}).get("abbreviation", "")}
    if bio["pos"] == "TWP": bio["pos"] = "P / DH"
    if pe.get("batSide"): bio["bats"] = pe["batSide"]["code"]
    if pe.get("pitchHand"): bio["throws"] = pe["pitchHand"]["code"]
    if pe.get("height"): bio["ht"] = pe["height"]
    if pe.get("weight"): bio["wt"] = pe["weight"]
    if pe.get("birthDate"):
        y, m, d = map(int, pe["birthDate"].split("-")); bio["born"] = f"{M[m-1]} {d}, {y}"
    where = pe.get("birthStateProvince") if pe.get("birthCountry") == "USA" else pe.get("birthCountry")
    place = ", ".join(x for x in [pe.get("birthCity"), where] if x)
    if place: bio["from"] = place
    c["bio"] = bio
for c in (c for sh in cards for c in sh.values()):
    for k in "bp":
        if k in c: c[k].sort(key=lambda r: r[0])
data["v"] = f"lahman-2025+mlb-{SEASON}"
json.dump(data, open("data.json", "w"), separators=(",", ":"))
for k in range(NS): json.dump(cards[k], open(f"cards/{k}.json", "w"), separators=(",", ":"))
new = sum(1 for p in P if p[3].startswith("mlb"))
print("fixed MLB IDs:", fixed)
print(len(games), "teams,", sum(len(g) for g in games.values()), "player-team seasons,", new, "new players,", len(P), "players")
