import requests
import time
import datetime
def fetch_base_prices(db, league):
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT base_item FROM chance_outcomes")
    base_names = set(row[0] for row in cursor.fetchall())
    headers = {
    "User-Agent": "Poe2Profit/1.0 https://github.com/KaanKocaman/Poe2Profit",
    "Content-Type": "application/json"
    }
    for item in base_names:
        payload = {
            "query": {
                "status": {"option": "online"},
                "filters": {
                    "type_filters": {
                        "filters": {
                            "rarity": {"option": "normal"},
                        }
                    }
                },
                "type": f"{item}"
            },
            "sort": {"price": "asc"}
        }

        response = requests.post(
            f"https://www.pathofexile.com/api/trade2/search/{league}",
            json=payload,
            headers=headers
        )
        output = response.json()
        query_id = output["id"]
        results = output["result"]

        available = min(5, len(results))
        if available == 0:
            time.sleep(1)
            continue

        ids = ",".join(results[:available])
        time.sleep(1)
        get_response = requests.get(
            f'https://www.pathofexile.com/api/trade2/fetch/{ids}?query={query_id}',
            headers=headers
        )
        time.sleep(1)
        data = get_response.json()
        for listing in data["result"]:
            currency = cursor.fetchone(cursor.execute(f"SELECT divine_equivalent from currency_rates WHERE currency_name = {listing["listing"]["price"]["currency"]}"))
            cursor.execute("INSERT OR REPLACE INTO base_prices (base_item, price_divine, last_updated, listing_count) VALUES (?,?,?,?)",
                           (listing["item"]["baseType"], currency, datetime.datetime.now().isoformat(), output["Total"]))
        db.commit()