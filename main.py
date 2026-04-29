from app.data.parsers.chance_csv import load_chance_csv
from app.data.database import initialize_database
from app.data.fetchers.poe2scout import fetch_unique_prices
db = initialize_database()
load_chance_csv(db, 'assets\\outcomes.csv')
fetch_unique_prices(db, 'Fate_Of_The_Vaal')