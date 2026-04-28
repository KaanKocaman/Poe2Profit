import pandas as pd

def load_chance_csv(db, filepath):
    mapped_dict = {'baseItem': 'base_item',    #Map the values from csv to match with database
                   'name': 'unique_item', 
                   'chance': 'chance_pct', 
                   'averageOrbs': 'avg_orbs', 
                   'minILvl': 'min_ilvl', 
                   'destructionChance': 'destruction_chance', 
                   'tier': 'tier', 
                   'weight': 'weight', 
                   'poeWikiLink': 'wiki_link'}
    
    df = pd.read_csv(filepath)
    df = df.rename(columns=mapped_dict) #rename the columns
    df = df.drop(columns=['baseItemDisambiguation','disambiguation']) #remove unnecessary columns

    df.to_sql(name='chance_outcomes', con=db, if_exists='replace') #add to database
    db.commit()
