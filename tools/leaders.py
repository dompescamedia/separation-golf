# Mark league leaders on the cards, like Baseball-Reference's bold: for each season and league,
# who led in each stat shown (rate stats need a qualifying total). Writes c.lb / c.lp = {year: [stat keys]}.
# Needs the pylahman package (for each team-season's league and games) and raw/<season>/teams.json for newer seasons.
import json, glob, os, collections, pandas as pd, pylahman
NS = 50
T = pd.read_parquet(os.path.join(os.path.dirname(pylahman.__file__), "data", "Teams.parquet"))
lg, tg = {}, collections.defaultdict(int)
for r in T.itertuples():
    l = r.lgID if isinstance(r.lgID, str) else "NA"
    lg[(int(r.yearID), r.teamIDBR)] = l; tg[(int(r.yearID), l)] = max(tg[(int(r.yearID), l)], int(r.G or 0))
BR = {"AZ": "ARI", "CWS": "CHW", "KC": "KCR", "SD": "SDP", "SF": "SFG", "TB": "TBR", "WSH": "WSN"}
for f in glob.glob("raw/*/teams.json"):
    y = int(f.split("/")[1])
    for t in json.load(open(f)):
        l = {103: "AL", 104: "NL"}.get(t.get("league", {}).get("id"), "NA")
        lg[(y, BR.get(t["abbreviation"], t["abbreviation"]))] = l; tg[(y, l)] = 162
cards = [json.load(open(f"cards/{k}.json")) for k in range(NS)]
B = {"g": 2, "ab": 3, "r": 4, "h": 5, "2b": 6, "3b": 7, "hr": 8, "rbi": 9, "sb": 10, "bb": 11, "so": 12}
PI = {"w": 2, "l": 3, "g": 4, "gs": 5, "sv": 6, "ip": 7, "h": 8, "bb": 10, "so": 11}
def seasons(c, kind):
    # (year, league) -> summed row + WAR, per player
    out = {}
    for j, r in enumerate(c.get(kind, [])):
        k = (r[0], lg.get((r[0], r[1]), "?"))
        s = out.setdefault(k, [0] * 15 + [None])
        for x in range(2, len(r)): s[x] += r[x]
        w = (c.get(kind + "w") or [None] * 99)[j]
        if w is not None: s[15] = (s[15] or 0) + w
    return out
def bat_vals(s, G):
    v = {k: s[i] for k, i in B.items()}
    ab, h, bb, hbp, sf = s[3], s[5], s[11], s[13], s[14]; pa = ab + bb + hbp + sf
    if pa >= 3.1 * G and ab:
        v["avg"] = h / ab; v["slg"] = (h + s[6] + 2 * s[7] + 3 * s[8]) / ab
        if pa: v["obp"] = (h + bb + hbp) / pa
    if s[15] is not None: v["war"] = s[15]
    return v
def pit_vals(s, G):
    v = {k: s[i] for k, i in PI.items()}
    if s[7] >= 3 * G and s[7]: v["era"] = -s[9] * 27 / s[7]; v["whip"] = -(s[8] + s[10]) * 3 / s[7]  # lower is better
    if s[15] is not None: v["war"] = s[15]
    return v
for kind, fn in [("b", bat_vals), ("p", pit_vals)]:
    best = collections.defaultdict(lambda: -1e18); vals = []
    for sh in cards:
        for pid, c in sh.items():
            c.pop("l" + kind, None)
            for (y, l), s in seasons(c, kind).items():
                if l in ("?", "NA"): continue
                v = fn(s, tg.get((y, l), 0) or 154); vals.append((c, y, l, v))
                for st, x in v.items(): best[(y, l, st)] = max(best[(y, l, st)], x)
    n = 0
    for c, y, l, v in vals:
        led = [st for st, x in v.items() if x == best[(y, l, st)] and (x > 0 if st not in ("era", "whip") else True)]
        if led: c.setdefault("l" + kind, {}).setdefault(str(y), []).extend(led); n += len(led)
    print(kind, n, "league-leading stats marked")
for k in range(NS): json.dump(cards[k], open(f"cards/{k}.json", "w"), separators=(",", ":"))
