from app.data.parsers.chance_csv import load_chance_csv
from app.data.database import initialize_database, save_poesessid
from app.data.fetchers.poe2scout import fetch_unique_prices, fetch_currency_prices
from app.data.fetchers.ggg_trade import fetch_base_prices
db = initialize_database()
cur = db.cursor()
cur.execute("SELECT value FROM app_config WHERE key='poesessid'")
id_exists = cur.fetchone()
if id_exists == None:
    poesessid = input("Enter your poesessid:")
    id = save_poesessid(db, poesessid)
#load_chance_csv(db, 'assets\\outcomes.csv')
#fetch_unique_prices(db, 'Fate_Of_The_Vaal')
#fetch_currency_prices(db, 'Fate_Of_The_Vaal')
fetch_base_prices(db,'Fate%20of%20the%20Vaal', id_exists[0])