from app.data.parsers.chance_csv import load_chance_csv
from app.data.database import initialize_database

db = initialize_database()
load_chance_csv(db, 'assets\\outcomes.csv')