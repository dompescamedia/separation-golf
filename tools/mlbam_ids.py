# Build mlbam.json: Baseball-Reference player ID -> MLB player ID, from the Chadwick Bureau register.
import csv, io, json, urllib.request
BASE = "https://raw.githubusercontent.com/chadwickbureau/register/master/data/people-{}.csv"
out = {}
for c in "0123456789abcdef":
    with urllib.request.urlopen(BASE.format(c)) as r:
        for row in csv.DictReader(io.TextIOWrapper(r, encoding="utf-8")):
            if row.get("key_bbref") and row.get("key_mlbam"):
                out[row["key_bbref"]] = int(row["key_mlbam"])
json.dump(out, open("mlbam.json", "w"), separators=(",", ":"), sort_keys=True)
print(len(out), "players matched")
