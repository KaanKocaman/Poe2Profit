import sqlite3 as sql
def initialize_database():
    db = sql.connect("assets\\profit.db")
    cur = db.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    cur.execute("CREATE TABLE IF NOT EXISTS chance_outcomes(base_item," \
                                    "unique_item," \
                                    "chance_pct," \
                                    "avg_orbs," \
                                    "min_ilvl," \
                                    "destruction_chance," \
                                    "tier," \
                                    "weight," \
                                    "wiki_link," \
                                    "PRIMARY KEY(base_item,unique_item))")
    cur.execute("CREATE TABLE IF NOT EXISTS unique_prices(unique_item," \
                                            "price_divine," \
                                            "last_updated," \
                                            "PRIMARY KEY(unique_item))")
    cur.execute("CREATE TABLE IF NOT EXISTS base_prices(base_item," \
                                        "price_divine," \
                                        "last_updated," \
                                        "listing_count," \
                                        "PRIMARY KEY(base_item))")
    cur.execute("CREATE TABLE IF NOT EXISTS currency_rates(currency_name," \
                                            "divine_equivalent," \
                                            "last_updated," \
                                            "PRIMARY KEY(currency_name))")
    cur.execute("CREATE TABLE IF NOT EXISTS results(base_item," \
                                    "unique_item," \
                                    "tier," \
                                    "avg_orbs," \
                                    "base_cost_div," \
                                    "orb_cost_div," \
                                    "total_cost_div," \
                                    "ev_div," \
                                    "profit_div," \
                                    "roi_pct," \
                                    "last_calculated," \
                                    "PRIMARY KEY(base_item, unique_item)," \
                                    "FOREIGN KEY(base_item) REFERENCES base_prices(base_item)," \
                                    "FOREIGN KEY(unique_item) REFERENCES unique_prices(unique_item))")
    return db