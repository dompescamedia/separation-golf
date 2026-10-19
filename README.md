# Separation Golf

Separation Golf is a daily baseball puzzle. Connect any two big leaguers by jumping teammate to teammate. Fewest jumps wins: eagle the shortest route, or bogey your way there. Daily hole, Daily 9, Endless and Custom modes, with every MLB roster since 1871.

Play: https://separationgolf.com/

## How it's built

- `index.html` is the whole game (HTML, CSS and JavaScript in one file). It runs in the browser with no server.
- `data.json` holds every player and team-season roster. `cards/*.json` hold the stats for the baseball cards.
- `scripts/build.py` and `scripts/build_stats.py` rebuild those files from the [Lahman Baseball Database](https://sabr.org/lahman-database/) (via the `pylahman` Python package).
- The site is served by GitHub Pages straight from the `main` branch.
- Player headshots load from MLB's image server by MLB ID. `.github/workflows/mlbam-ids.yml` refreshes `mlbam.json` (Baseball-Reference ID to MLB ID, from the Chadwick Bureau register), and `tools/add_mlbam.py` writes those IDs into `data.json`. Run it again after rebuilding `data.json`.
