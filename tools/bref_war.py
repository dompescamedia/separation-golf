# Career WAR from Baseball-Reference's public WAR files (batting + pitching), written to war.json.
# Keys are Baseball-Reference player IDs; "mlb" maps MLB IDs as a fallback for matching.
import csv, io, json, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (separation-golf data refresh; github.com/dompescamedia/separation-golf)"}
def get(name):
    req = urllib.request.Request("https://www.baseball-reference.com/data/" + name, headers=UA)
    return urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")
by_id, by_mlb, rows = {}, {}, 0
name_of, first = {}, {}
for f in ["war_daily_bat.txt", "war_daily_pitch.txt"]:
    for r in csv.DictReader(io.StringIO(get(f))):
        try: w = float(r.get("WAR") or 0)
        except ValueError: continue
        pid, mid = r.get("player_ID"), r.get("mlb_ID")
        rows += 1
        if pid:
            by_id[pid] = by_id.get(pid, 0) + w
            name_of[pid] = r.get("name_common", "")
            y = int(r["year_ID"]) if (r.get("year_ID") or "").isdigit() else 9999
            first[pid] = min(first.get(pid, 9999), y)
        if mid and mid.isdigit(): by_mlb[mid] = by_mlb.get(mid, 0) + w
out = {"bref": {k: round(v, 1) for k, v in by_id.items()}, "mlb": {k: round(v, 1) for k, v in by_mlb.items()},
       # name|first season, a last-resort match when the IDs differ (e.g. sabatc.01 vs sabatcc01)
       "name": {f"{name_of[k]}|{first[k]}": round(v, 1) for k, v in by_id.items()}}
json.dump(out, open("war.json", "w"), separators=(",", ":"), sort_keys=True)
print(rows, "rows,", len(by_id), "players")
