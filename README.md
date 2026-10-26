# Poe2Profit

A desktop profit calculator for **Orb of Chance crafting in Path of Exile 2**.

Using an Orb of Chance on a normal base item can turn it into a unique, but most attempts destroy the base instead. Poe2Profit pulls live prices for every chanceable base/unique pair and works out whether chancing it is worth it, so you can sort by profit or ROI instead of guessing.

## Features

- Live prices for unique items and currency from [poe2scout.com](https://poe2scout.com)
- Normal base item prices from the cheapest listings on the official Path of Exile 2 trade site
- For each base → unique pair, it estimates:
  - **Base cost**: base price × the number of bases you expect to destroy before hitting the unique
  - **Orb cost**: average Orbs of Chance needed × the Orb of Chance price
  - **Profit** and **ROI %** against the unique's market price
- Dark PyQt6 table with search, tier filter, minimum ROI filter, and profit/loss toggles
- Resumable refresh: bases priced within the last hour are skipped, so a crashed or interrupted refresh picks up where it left off

All prices are in Divine Orbs.

## Requirements

- Python 3 (developed on Python 3.14, on Windows)
- A Path of Exile account and its `POESESSID` cookie (see [below](#poesessid))

## Setup

```bash
git clone https://github.com/KaanKocaman/Poe2Profit.git
cd Poe2Profit
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux, activate the virtual environment with `source .venv/bin/activate` instead.

## POESESSID

The official trade API only answers logged-in requests, so Poe2Profit needs your `POESESSID` session cookie to look up base item prices.

**How to get it**

1. Log in at [pathofexile.com](https://www.pathofexile.com).
2. Open your browser's developer tools (`F12`).
3. Go to **Application** (Chrome/Edge) or **Storage** (Firefox) → **Cookies** → `https://www.pathofexile.com`.
4. Copy the value of `POESESSID`.

**How it's used**

- On first launch, the app asks for it in the terminal and saves it in the local database, `assets/profit.db`.
- It is only sent as a cookie to `www.pathofexile.com` when fetching base prices.
- `assets/profit.db` is in `.gitignore`, so it won't be committed.

> [!WARNING]
> Treat your POESESSID like a password: anyone who has it is logged in as you. Never share it or commit it. If you think it has leaked, log out of pathofexile.com to invalidate it.

**Changing it**

Sessions expire. To enter a new one, delete `assets/profit.db` and start the app again. This also clears cached prices, so run a refresh afterwards.

## Usage

Run the app from the project root (it uses paths relative to that folder):

```bash
python main.py
```

1. Paste your POESESSID when prompted (first run only).
2. Click **⟳ Refresh** to fetch prices and calculate results. Fetching base prices is rate limited by the trade API, so a full refresh can take up to about two hours. Leave the app open until it finishes.
3. Filter and sort the table:
   - **Search** by base or unique name
   - **Tier**: T1, T2, or T3
   - **Min ROI**: hide pairs under a return threshold
   - **Profitable / Loss**: show only one side

### League

The league is set in `main.py`:

```python
launch_ui(db, 'Fate of the Vaal', id_exists[0])
```

Change `'Fate of the Vaal'` to the league you play in.

### Contact info in requests

GGG asks API clients to include contact info in their User-Agent. By default Poe2Profit sends this repo's URL. To send your own email instead, set an environment variable before running:

```bash
set POE2PROFIT_CONTACT=you@example.com
```

(Use `export` instead of `set` on macOS/Linux.)

## Project structure

```
main.py                     Entry point: opens the database, asks for POESESSID, launches the UI
app/
  config.py                 User-Agent / contact settings
  data/
    database.py             SQLite schema and POESESSID storage
    calculator.py           Cost, profit, and ROI calculation
    fetchers/
      poe2scout.py          Unique prices and currency rates
      ggg_trade.py          Base item prices from the official trade API
    parsers/
      chance_csv.py         Loads assets/outcomes.csv into the database
  ui/
    main_window.py          PyQt6 interface
assets/
  outcomes.csv              Chance odds per base/unique pair (chance %, average orbs, destruction chance, tier)
  profit.db                 Local database, created on first run (not committed)
```

## Disclaimer

Poe2Profit is a fan project and is not affiliated with or endorsed by Grinding Gear Games. Prices are market snapshots and the odds are estimates, so results are a guide, not a guarantee.
