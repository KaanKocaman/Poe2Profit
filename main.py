from app.data.database import initialize_database, save_poesessid
from app.ui.main_window import launch_ui
db = initialize_database()
cur = db.cursor()
cur.execute("SELECT value FROM app_config WHERE key='poesessid'")
id_exists = cur.fetchone()
if id_exists == None:
    poesessid = input("Enter your poesessid:")
    id = save_poesessid(db, poesessid)
    id_exists = (poesessid,)
launch_ui(db, 'Fate of the Vaal', id_exists[0])