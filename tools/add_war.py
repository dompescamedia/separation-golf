# Put Baseball-Reference career WAR (from war.json) on each player's card as "war".
# Match by Baseball-Reference ID, then MLB ID, then name + first season.
import json, glob
data = json.load(open("data.json")); P = data["players"]
w = json.load(open("war.json"))
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
    json.dump(cards, open(f, "w"), separators=(",", ":"))
for p in P:
    v = war(p)
    while len(p) < 11: p.append(0)
    p[10] = round(v * 10) if v is not None else 0
json.dump(data, open("data.json", "w"), separators=(",", ":"))
print(hit, "of", len(P), "cards have career WAR")
