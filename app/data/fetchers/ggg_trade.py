import requests
import time
import datetime
import re
def fetch_base_prices(db, league, poesessid):
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT base_item FROM chance_outcomes")
    base_names = set(row[0] for row in cursor.fetchall())
    cookies = {"POESESSID": poesessid}
    headers = {
    "User-Agent": "OAuth Poe2Profit/1.0 (contact: https://github.com/KaanKocaman/Poe2Profit)",
    "Content-Type": "application/json"
    }
    CURRENCY_MAP = {
    "regal": "Regal Orb",
    "chaos": "Chaos Orb",
    "divine": "Divine Orb",
    "exalted": "Exalted Orb",
    "chance": "Orb of Chance",
    "vaal": "Vaal Orb",
    "aug": "Orb of Augmentation",
    "transmute": "Orb of Transmutation",
    }
    total = len(base_names)
    current = 0
    for item in base_names.copy():
        current += 1
        print(f"Fetching {item} ({current}/{total})")
        while True:
            payload = {"query":{"status":{"option":"securable"},"type":item,"stats":[{"type":"and","filters":[],"disabled":False}],"filters":{"type_filters":{"filters":{"rarity":{"option":"normal"}},"disabled":False}}},"sort":{"price":"asc"}}

            response = requests.post(
                f"https://www.pathofexile.com/api/trade2/search/poe2/{league}",
                json=payload,
                headers=headers,
                cookies=cookies
            )
            output = response.json()
            print(response.text)
            print(response.status_code)
            response_code = response.status_code
            error_message = response.text
            if response_code == 200:
                query_id = output["id"]
                results = output["result"]

                available = min(5, len(results))
                if available == 0:
                    break

                ids = ",".join(results[:available])
                get_response = requests.get(
                    f'https://www.pathofexile.com/api/trade2/fetch/{ids}?query={query_id}',
                    headers=headers,
                    cookies=cookies
                )
                data = get_response.json()
                for listing in data["result"]:
                    currency_name = CURRENCY_MAP.get(listing["listing"]["price"]["currency"])
                    if currency_name is None:
                        continue 
                    cursor.execute("SELECT divine_equivalent from currency_rates WHERE currency_name = ?", (currency_name,))
                    currency = cursor.fetchone()
                    if currency is None:
                        continue
                    divine_price = listing["listing"]["price"]["amount"] * currency[0]
                    cursor.execute("INSERT OR REPLACE INTO base_prices (base_item, price_divine, last_updated, listing_count) VALUES (?,?,?,?)",
                                (listing["item"]["baseType"], divine_price, datetime.datetime.now().isoformat(), output["total"]))
                db.commit()
                break
            elif response_code==429:
                wait_time = int(re.search(r'(\d+) seconds', error_message).group(1))
                time.sleep(wait_time)
            else:
                break