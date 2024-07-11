from flask import Flask, jsonify, request
import pandas as pd
from flask_cors import CORS
from riot_api import get_puuid, get_matches_with_champion, get_champ_name
import cassiopeia as cass
import os, json, csv

app = Flask(__name__)
CORS(app) 

CACHE_FILE = 'cache.json'

def save_cache_to_file():
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def load_cache_from_file():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

cache = load_cache_from_file()

@app.route('/api/get_everything', methods=['POST'])
def api_get_puuid():
    api_key = 'RGAPI-28887941-ef83-4b09-869e-a51fd2e2b671' 
    data = request.json
    summoner_name = data.get('summonerName')
    tagline = data.get('tagline')
    role = data.get('role')
    region = data.get('region')
    selected_champion = data.get('selectedChampion')['value']
    
    if(region == "NA" or region == "BR"):
        mass_region = 'americas'
        continent = 'AMERICAS'
    elif(region == "KR" or region == "JP"):
        mass_region = 'asia'
        continent = 'ASIA'
    elif(region == "EUW" or region == "EUNE"):
        mass_region = 'europe'
        continent = 'EUROPE'

    cache_key = f"{summoner_name}#{tagline}"

    if cache_key in cache:
        champions = cache[cache_key]
        for champ_dict in champions:
            if champ_dict.get('champion') == selected_champion:
                print(f"Cache hit for {cache_key} and champion {selected_champion}")
                result = champ_dict
                should_fetch_data = False
                break
        else:
            print(f"Cache miss for {cache_key} and champion {selected_champion}")
            should_fetch_data = True
    else:
        print(f"Cache miss for {cache_key}")
        should_fetch_data = True

    if should_fetch_data:
        try:
            puuid = get_puuid(summoner_name, tagline, mass_region, api_key)
            summoner = cass.get_summoner(puuid=puuid, region=region)
            champ_list = get_matches_with_champion(selected_champion, summoner, puuid, continent, region, 50)

            result = {
                'champion': selected_champion,
                'champList': champ_list
            }
            if cache_key not in cache:
                cache[cache_key] = []
            cache[cache_key].append(result['champion'])
            save_cache_to_file()

            csv_file_path = f"{summoner_name}_{tagline}_{selected_champion}_match_id_list.csv"
            with open(csv_file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Match ID'])  # Replace with actual column names if necessary
                for match_id in result['champList']:
                    writer.writerow([match_id])

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify(result), 200


@app.route('/player-stats', methods=['GET'])
def get_player_stats():
    data = pd.read_csv('more_info.csv')

    data['Duration'] = data['Duration'].round()
    duration_win_data = data.groupby('Duration').agg(
        win_count=('Win', 'sum'),
        match_count=('Duration', 'size')
    ).reset_index()

    duration_win_data['win_rate'] = (duration_win_data['win_count'] / duration_win_data['match_count']) * 100
    duration_win_data['radius'] = (duration_win_data['match_count'] ** 0.5) * 2

    data = duration_win_data.to_dict(orient='records')
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)