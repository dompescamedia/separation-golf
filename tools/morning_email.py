"""Email Dom yesterday's Separation Golf numbers from the anonymous abacus counters.

Needs repo secrets SMTP_USER (the Gmail address) and SMTP_PASS (a Gmail app password).
MAIL_TO defaults to SMTP_USER. Without the secrets it prints the email instead (dry run).
Counter keys number Dailies from Oct 15 (key 1); players see that day as Daily #25.
"""
import datetime, json, os, smtplib, urllib.request, urllib.error, zoneinfo
from concurrent.futures import ThreadPoolExecutor
from email.message import EmailMessage

AB = "https://abacus.jasoncameron.dev/get/dompesca-sepgolf/"
START = datetime.date(2026, 10, 15)
MIX = ["eagle", "birdie", "par", "bogey", "double", "triple+"]
MODES = [("daily", "Daily"), ("d9", "Daily 9"), ("endless", "Endless"), ("custom", "Custom"), ("range", "Range"),
         ("run", "Team history run"), ("archive", "Archive"), ("challenge", "Challenge")]

def get(k):
    try:
        with urllib.request.urlopen(AB + k, timeout=20) as r:
            return json.load(r).get("value", 0) or 0
    except urllib.error.HTTPError as e:
        return 0 if e.code == 404 else None
    except Exception:
        return None

today = datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York")).date()
y = today - datetime.timedelta(days=1)
n = (y - START).days + 1
week = [y - datetime.timedelta(days=i) for i in range(6, -1, -1)]
keys = ["players", f"daily-{n}-started", f"daily-{n}-holed", f"daily-{n}-gaveup", f"daily-{n}-hint", f"daily-{n}-back",
        *[f"daily-{n}-r{i}" for i in range(6)], f"d9-{y}-started", f"d9-{y}-done", *[f"d9-{y}-s{k}" for k in range(16)],
        *[f"{p}-{y}" for p in ("new", "back", "plays", "chal-made", "chal-played", "from-share")],
        *[f"mode-{m}-{y}" for m, _ in MODES], *[f"visitors-{d}" for d in week]]
with ThreadPoolExecutor(6) as ex:
    V = dict(zip(keys, ex.map(get, keys)))
f = lambda k: "?" if V[k] is None else f"{V[k]:,}"

mix = [V[f"daily-{n}-r{i}"] or 0 for i in range(6)]
avg = sum(c * (i - 2) for i, c in enumerate(mix)) / sum(mix) if sum(mix) else None
s9 = [V[f"d9-{y}-s{k}"] or 0 for k in range(16)]
avg9 = sum(c * (k - 5) for k, c in enumerate(s9)) / sum(s9) if sum(s9) else None
sg = lambda x: "n/a" if x is None else f"{x:+.1f}"
started = V[f"daily-{n}-started"] or 0
rate = f"{round(100 * (V[f'daily-{n}-holed'] or 0) / started)}%" if started else "n/a"

lines = [
    f"Separation Golf, {y:%A %b %-d} (Daily #{n + 24})", "",
    f"Visitors: {f(f'visitors-{y}')}  (new {f(f'new-{y}')}, came back {f(f'back-{y}')})",
    f"Games played: {f(f'plays-{y}')}",
    f"Devices ever: {f('players')}", "",
    "THE DAILY",
    f"Started {f(f'daily-{n}-started')} · holed {f(f'daily-{n}-holed')} ({rate}) · gave up {f(f'daily-{n}-gaveup')}",
    f"Average vs par: {sg(avg)}   " + ", ".join(f"{m} {c}" for m, c in zip(MIX, mix)),
    f"Used a hint: {f(f'daily-{n}-hint')} · used back: {f(f'daily-{n}-back')}", "",
    "DAILY 9",
    f"Started {f(f'd9-{y}-started')} · finished {f(f'd9-{y}-done')} · average vs par {sg(avg9)}", "",
    "BY MODE", "  ".join(f"{l} {f(f'mode-{m}-{y}')}" for m, l in MODES), "",
    f"Challenge links sent {f(f'chal-made-{y}')}, played {f(f'chal-played-{y}')} · visits from shared results {f(f'from-share-{y}')}", "",
    "VISITORS, LAST 7 DAYS", "  ".join(f"{d:%a} {f(f'visitors-{d}')}" for d in week), "",
    "Everything else (upcoming holes, X post, most-picked players): https://separationgolf.com/admin.html",
]
body = "\n".join(lines)
subject = f"Separation Golf: {f(f'visitors-{y}')} visitors, {f(f'daily-{n}-holed')} holed the Daily ({y:%b %-d})"
print(subject + "\n\n" + body)

user, pw = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS")
if not (user and pw):
    print("\n(dry run: add SMTP_USER and SMTP_PASS secrets to send)")
    raise SystemExit
msg = EmailMessage()
msg["Subject"], msg["From"], msg["To"] = subject, user, os.environ.get("MAIL_TO") or user
msg.set_content(body)
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(user, pw.replace(" ", ""))
    s.send_message(msg)
print("\nSent to", msg["To"])
