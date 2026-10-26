import requests
from datetime import datetime
from app.config import USER_AGENT

def fetch_unique_prices(db, league):
    cursor = db.cursor()
    
    # Get chanceable names from database
    cursor.execute("SELECT unique_item FROM chance_outcomes")
    chanceable_names = set(row[0] for row in cursor.fetchall())
    
    headers = {"User-Agent": USER_AGENT}
    urls = [
        f"https://poe2scout.com/api/poe2/Leagues/{league}/Uniques/ByCategory?Category=armour&Page=1&PerPage=250&ReferenceCurrency=divine",
        f"https://poe2scout.com/api/poe2/Leagues/{league}/Uniques/ByCategory?Category=accessory&Page=1&PerPage=100&ReferenceCurrency=divine",
        f"https://poe2scout.com/api/poe2/Leagues/{league}/Uniques/ByCategory?Category=weapon&Page=1&PerPage=100&ReferenceCurrency=divine",
        f"https://poe2scout.com/api/poe2/Leagues/{league}/Uniques/ByCategory?Category=flask&Page=1&PerPage=25&ReferenceCurrency=divine"]

    for url in urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            output = response.json()
            for item in output['Items']:
                if item['Name'] in chanceable_names:
                    cursor.execute(
                        "INSERT OR REPLACE INTO unique_prices (unique_item, price_divine, last_updated) VALUES (?, ?, ?)",
                        (item['Name'], item['CurrentPrice'], datetime.now().isoformat())
                    )
    db.commit()
def fetch_currency_prices(db, league):
    cursor = db.cursor()
    headers = {"User-Agent": USER_AGENT}
    urls = [f'https://poe2scout.com/api/poe2/Leagues/{league}/Currencies/ByCategory?Category=currency&Page=1&PerPage=50&ReferenceCurrency=divine']
    for url in urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            output = response.json()
            for item in output['Items']:
                cursor.execute("INSERT OR REPLACE INTO currency_rates (currency_name, divine_equivalent, last_updated) VALUES(?, ?, ?)",
                              (item['Text'], item['CurrentPrice'], datetime.now().isoformat())
                )
    db.commit()
                          
