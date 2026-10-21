"""Set or clear one hand-picked Daily in index.html's DAILY_SET.

Usage: set_daily.py "YYYY-MM-DD teeID pinID"   (IDs as shown on admin.html)
       set_daily.py "YYYY-MM-DD clear"          (go back to the generated pick)
Only future Eastern dates are allowed, so nobody's in-progress Daily changes under them.
"""
import datetime, json, re, sys, zoneinfo

parts = sys.argv[1].split()
date = parts[0]
datetime.date.fromisoformat(date)
today = datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York")).date().isoformat()
if date <= today:
    sys.exit(f"{date} is today or earlier (Eastern is {today}); only future Dailies can change.")

html = open("index.html", encoding="utf-8").read()
m = re.search(r"const DAILY_SET=(\{.*?\});", html, re.S)
ds = json.loads(m.group(1))
if parts[1:] == ["clear"]:
    ds.pop(date, None)
else:
    tee, pin = parts[1:3]
    ids = {p[3] for p in json.load(open("data.json"))["players"]}
    bad = [x for x in (tee, pin) if x not in ids]
    if bad:
        sys.exit(f"Unknown player ID: {', '.join(bad)}")
    if tee == pin:
        sys.exit("Tee and pin are the same player.")
    ds[date] = [tee, pin]

items = [f'"{d}":["{a}","{b}"]' for d, (a, b) in sorted(ds.items())]
lines = [",".join(items[i:i + 3]) for i in range(0, len(items), 3)]
html = html[:m.start(1)] + "{" + ",\n  ".join(lines) + "}" + html[m.end(1):]
open("index.html", "w", encoding="utf-8").write(html)
print(f"DAILY_SET[{date}] =", ds.get(date, "generated"))
