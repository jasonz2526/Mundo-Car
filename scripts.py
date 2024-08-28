from app import save_cache_to_file
import cassiopeia as cass
import json, os
from pymongo import MongoClient
#save_cache_to_file

client = MongoClient('mongodb://localhost:27017')
db = client['league_database']
match_collection = db['matches']


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
champ_name = "Evelynn"
query = {'type': 'Pro', f'champions.{champ_name}': {'$exists': True}}
documents = match_collection.find(query)

# Step 2: Combine the match data into a single dictionary
combined_matches = {}

for document in documents:
    match_data = document['match_data']
    combined_matches.update(match_data)

# Now, `combined_matches` will contain the combined match data in the desired format
print(combined_matches)