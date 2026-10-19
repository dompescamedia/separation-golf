# Put each player's MLB ID into data.json as players[i][9] (0 when there is none).
# mlbam.json is keyed by Baseball-Reference ID, which differs from the Lahman ID for about 500 players
# (Bobby Miller is Lahman millebo05 but Baseball-Reference millebo06), so look up through Lahman's bbrefID.
# Those players also get data["br"] = {player index: Baseball-Reference ID} for card links and WAR.
import json, os, pandas as pd, pylahman
data = json.load(open("data.json"))
ids = json.load(open("mlbam.json"))
pe = pd.read_parquet(os.path.join(os.path.dirname(pylahman.__file__), "data", "People.parquet"))
# Lahman's bbrefID is itself unreliable for some Negro Leagues players (two players claiming one ID, or none),
# so a claimed ID goes to the player whose own Lahman ID it is, else to its only claimant; a player whose
# own ID is claimed by someone else and who has no unique claim of their own gets no Baseball-Reference ID.
claims = {}
for r in pe.itertuples():
    if isinstance(r.bbrefID, str) and r.bbrefID: claims.setdefault(r.bbrefID, []).append(r.playerID)
bref = {}
for b, who in claims.items():
    if b in who: bref[b] = b
    elif len(who) == 1: bref[who[0]] = b
for pid in set(pe.playerID) - set(bref):
    if pid not in claims: bref[pid] = pid
# A missing bbrefID falls back to the Lahman ID, which Baseball-Reference may have since given to a newer player
# (Lahman's 1910 Julián Pérez is perezju03; to Baseball-Reference that is Junior Perez, 2026), so drop any ID
# whose Baseball-Reference seasons (war.json) are all outside the player's own years.
war = json.load(open("war.json"))["seasons"]
def fits(b, p):
    yrs = [x[0] for k in "bp" for x in war.get(b, {}).get(k, [])]
    return not yrs or any(p[1] <= y <= p[2] for y in yrs)
hit, br = 0, {}
for i, p in enumerate(data["players"]):
    while len(p) < 10: p.append(0)
    if p[3].startswith("mlb"): hit += p[9] > 0; continue
    b = bref.get(p[3], "")
    if b and not fits(b, p): b = ""
    if b != p[3]: br[str(i)] = b
    p[9] = ids.get(b, 0) if b else 0; hit += p[9] > 0
data["br"] = br
json.dump(data, open("data.json", "w"), separators=(",", ":"))
print(hit, "of", len(data["players"]), "players have an MLB ID;", len(br), "Baseball-Reference IDs differ from Lahman")
