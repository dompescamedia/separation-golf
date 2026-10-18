# Put Baseball-Reference career WAR (from war.json) on each player's card as "war".
# Match by Baseball-Reference ID, then MLB ID, then name + first season.
import json, glob
data = json.load(open("data.json")); P = data["players"]
w = json.load(open("war.json"))
def pid_of(p):
    if p[3] in w["bref"]: return p[3]
    if p[9] and str(p[9]) in w["mlbpid"]: return w["mlbpid"][str(p[9])]
    return w["namepid"].get(f"{p[0]}|{p[1]}")
def season_war(rows, src):
    # Line each card row up with Baseball-Reference's season rows: same year and team, else same stint order in that year.
    out = []
    for r in rows or []:
        yr = [x for x in src if x[0] == r[0]]
        same = [x for x in yr if x[1] == r[1]]
        if same: out.append(round(sum(x[3] for x in same), 1)); continue
        k = [q[1] for q in rows if q[0] == r[0]].index(r[1])
        yr.sort(key=lambda x: x[2])
        out.append(yr[k][3] if k < len(yr) and len([q for q in rows if q[0] == r[0]]) == len(yr) else None)
    return out
def war(p):
    if p[3] in w["bref"]: return w["bref"][p[3]]
    if p[9] and str(p[9]) in w["mlb"]: return w["mlb"][str(p[9])]
    return w["name"].get(f"{p[0]}|{p[1]}")
hit = 0
for f in glob.glob("cards/*.json"):
    cards = json.load(open(f))
    for k, c in cards.items():
        v = war(P[int(k)])
        if v is None: c.pop("war", None)
        else: c["war"] = v; hit += 1
        sz = w["seasons"].get(pid_of(P[int(k)]) or "", {})
        for kind in "bp":
            c.pop(kind + "w", None)
            if c.get(kind) and sz.get(kind):
                sw = season_war(c[kind], sz[kind])
                if any(x is not None for x in sw): c[kind + "w"] = sw
    json.dump(cards, open(f, "w"), separators=(",", ":"))
for p in P:
    v = war(p)
    while len(p) < 11: p.append(0)
    p[10] = round(v * 10) if v is not None else 0
json.dump(data, open("data.json", "w"), separators=(",", ":"))
print(hit, "of", len(P), "cards have career WAR")
