from flask import Flask, jsonify, request
#import flask_socketio
from flask_socketio import SocketIO
import pandas as pd
from flask_cors import CORS
from riot_api import get_puuid, get_matches_with_champion, get_champ_name
from data_gathering import gather_match_info
import cassiopeia as cass
import os, json, csv, time

app = Flask(__name__)
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*")

CACHE_FILE = 'cache.json'
cacheSwitch = True
hitCount = 50
limit = 5000

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
def api_get_everything():
    api_key = 'RGAPI-28887941-ef83-4b09-869e-a51fd2e2b671' 
    data = request.json
    summoner_name = data.get('summonerName', '').replace(' ', '').lower()
    tagline = data.get('tagline', '').replace(' ', '').lower()
    role = data.get('role')
    region = data.get('region')
    selected_champion = data.get('selectedChampion')
    type = data.get('type')
    
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
            if champ_dict == selected_champion:
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
            champ_list = get_matches_with_champion(selected_champion, summoner, puuid, continent, region, hitCount, limit)

            result = {
                'champion': selected_champion,
                'champList': champ_list
            }

            if cacheSwitch:
                if cache_key not in cache:
                    cache[cache_key] = []
                cache[cache_key].append(result['champion'])
                save_cache_to_file()

            if type == 'Pro':
                csv_folder = 'pro_ids_csvs'
            else:
                csv_folder = "match_ids_csvs"
                
            csv_file_path = os.path.join(csv_folder, f"{summoner_name}_{tagline}_{selected_champion}_match_id_list.csv")
            with open(csv_file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Match ID'])  
                for match_id in result['champList']:
                    writer.writerow([match_id])

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    #gather_match_info(summoner_name, tagline, selected_champion, region, mass_region, api_key, type)

    return jsonify(result), 200

@app.route('/player-stats', methods=['GET'])
def get_player_stats():
    data_normal = pd.read_csv("./match_info_csvs/kitkat_miffy_Kai'Sa_match_info.csv")
    
    bins = [0, 15, 20, 25, 30, 35, 40, float('inf')]
    labels = ['15 and less', '15-20', '20-25', '25-30', '30-35', '35-40', '40 and more']
    data_normal['duration_bucket'] = pd.cut(data_normal['duration'], bins=bins, labels=labels, right=False)

    duration_win_data_normal = data_normal.groupby('duration_bucket', observed=True).agg(
        win_count=('win', 'sum'),
        match_count=('duration', 'size')
    ).reset_index()
    duration_win_data_normal['win_rate'] = (duration_win_data_normal['win_count'] / duration_win_data_normal['match_count']) * 100
    data_normal = duration_win_data_normal.to_dict(orient='records')

    data_pro = pd.read_csv("./pro_match_info_csvs/feedmeiron_0696_Kai'Sa_match_info.csv")
    data_pro['duration_bucket'] = pd.cut(data_pro['duration'], bins=bins, labels=labels, right=False)

    duration_win_data_pro = data_pro.groupby('duration_bucket', observed=True).agg(
        win_count=('win', 'sum'),
        match_count=('duration', 'size')
    ).reset_index()
    duration_win_data_pro['win_rate'] = (duration_win_data_pro['win_count'] / duration_win_data_pro['match_count']) * 100
    data_pro = duration_win_data_pro.to_dict(orient='records')

    return jsonify({'normal': data_normal, 'pro': data_pro})

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    app.run(debug=True)
    #socketio.run(app, debug=True)

