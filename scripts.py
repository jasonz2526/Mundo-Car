from app import save_cache_to_file
import cassiopeia as cass
import json, os

save_cache_to_file

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