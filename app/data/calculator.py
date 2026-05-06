def calculate_cost(db):
    cur = db.cursor()
    cur.execute("SELECT divine_equivalent FROM currency_rates WHERE currency_name = (?)", ("Orb of Chance"))
    chance_price = cur.fetchone()
    cur.execute("SELECT avg_orbs FROM ")