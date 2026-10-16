# Put each player's MLB ID into data.json as players[i][9] (0 when there is none).
import json, sys
data = json.load(open("data.json"))
ids = json.load(open("mlbam.json"))
hit = 0
for p in data["players"]:
    m = ids.get(p[3], 0)
    hit += m > 0
    p[9:] = [m]
json.dump(data, open("data.json", "w"), separators=(",", ":"))
print(hit, "of", len(data["players"]), "players have an MLB ID")
