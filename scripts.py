from app import save_cache_to_file
import cassiopeia as cass
import json, os
from pymongo import MongoClient

save_cache_to_file

client = MongoClient('mongodb://localhost:27017')
db = client['league_database']
match_collection = db['matches']
pro_champion_collection = db['pros']


'''na_champs = cass.get_champions(region = "NA")
champ_splash_dict = {}
count = 0

for champ in na_champs:
    champ_name = champ.name
    champ_splash_dict[champ_name] = []
    for skin in champ.skins:
        try:
            champ_splash_dict[champ_name].append(skin.splash_url)
        except AttributeError:
            continue
    
SPLASH_ARTS_FILE = 'splash_arts.json'

def save_splash_arts_to_file():
    with open(SPLASH_ARTS_FILE, 'w') as f:
        json.dump(champ_splash_dict, f)

def load_splash_arts_from_file():
    if os.path.exists(SPLASH_ARTS_FILE):
        with open(SPLASH_ARTS_FILE, 'r') as f:
            return json.load(f)
    return {}

save_splash_arts_to_file()
load_splash_arts_from_file()'''

'''
pipeline = [
    {
        "$match": {
            "type": "Pro",
            "champions.Evelynn": { "$exists": True }  # Ensure Evelynn is a champion
        }
    },
    {
        "$project": {
            "match_infos": { "$objectToArray": "$match_data" }  # Convert match_infos to an array
        }
    },
    {
        "$unwind": "$match_infos"  # Unwind the match_infos array
    },
    {
        "$group": {
            "_id": None,
            "combined_matches": {
                "$push": "$match_infos.v"  # Push match data into an array
            }
        }
    }
]

result = match_collection.aggregate(pipeline)

for results in result:
    print(results.get('combined_matches', []))
'''

'''
all_matches = match_collection.find()

match_list = list(all_matches)
for match in match_list:
    match['_id'] = str(match['_id'])

with open('matches.json', 'w') as json_file:
    json.dump(match_list, json_file, indent=4)'''
