import sqlite3
from datetime import datetime

def calculate_cost(db):
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    cur.execute("SELECT divine_equivalent FROM currency_rates WHERE currency_name = ?", ("Orb of Chance",))
    chance_row = cur.fetchone()
    if chance_row is None:
        print("Orb of Chance price not found. Aborting.")
        return
    chance_price = chance_row[0]

    cur.execute("""
        SELECT c.base_item, c.unique_item, c.avg_orbs, c.tier, c.chance_pct, c.destruction_chance,
               u.price_divine AS unique_price, b.price_divine AS base_price
        FROM chance_outcomes c
        JOIN base_prices b ON c.base_item = b.base_item
        JOIN unique_prices u ON c.unique_item = u.unique_item
    """)
    all_data = cur.fetchall()

    results = []
    for data in all_data:
        avg_orbs = data["avg_orbs"]
        chance_pct = data["chance_pct"]
        destruction_chance = data["destruction_chance"] or 0.0
        base_price = data["base_price"]
        unique_price = data["unique_price"]

        if not avg_orbs or not chance_pct or chance_pct == 0:
            continue

        expected_bases = (float(chance_pct.replace("%","")) + float(destruction_chance.replace("%",""))) / float(chance_pct.replace("%",""))
        base_cost = base_price * expected_bases
        orb_cost = avg_orbs * chance_price
        total_cost = base_cost + orb_cost
        profit = unique_price - total_cost
        roi = (profit / total_cost * 100) if total_cost > 0 else 0.0

        results.append((
            data["base_item"],
            data["unique_item"],
            data["tier"],
            avg_orbs,
            round(base_cost, 4),
            round(orb_cost, 4),
            round(total_cost, 4),
            round(unique_price, 4),
            round(profit, 4),
            round(roi, 2),
            datetime.now().isoformat()
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO results (
            base_item, unique_item, tier, avg_orbs,
            base_cost_div, orb_cost_div, total_cost_div,
            ev_div, profit_div, roi_pct, last_calculated
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, results)

    db.commit()
    print(f"Calculated {len(results)} item pairs.")