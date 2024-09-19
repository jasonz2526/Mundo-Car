from flask import Flask, jsonify, request
from flask_socketio import SocketIO
import pandas as pd
from flask_cors import CORS
from riot_api import get_puuid, get_matches_with_champion
from data_gathering import calculate_average_diffs, laning_diff
from location import gather_kill_data_master
from simplified import calculate_additional_stats
import cassiopeia as cass
import os, json
from pymongo import MongoClient
from API_KEY import API_KEY

app = Flask(__name__)
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*")

client = MongoClient('mongodb://localhost:27017')
db = client['league_database']
match_collection = db['matches']
pro_champion_collection = db['pros']

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
    api_key = API_KEY
    data = request.json
    summoner_name = data.get('summonerName', '').replace(' ', '').lower()
    tagline = data.get('tagline', '').replace(' ', '').lower()
    role = data.get('role')
    region = data.get('region')
    selected_champion = data.get('selectedChampion')
    type = data.get('type')
    mass_region, continent = get_region_data(region)

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
            champ_list = get_matches_with_champion(selected_champion, role, summoner, puuid, continent, region, hitCount, limit)
            if champ_list == []:
                return jsonify({'incorrect region'}), 500

            result = {
                'champion': selected_champion,
                'champList': champ_list
            }

            if cacheSwitch:
                if cache_key not in cache:
                    cache[cache_key] = []
                cache[cache_key].append(result['champion'])
                save_cache_to_file()

            summoner_data = {
                '_id': f"{summoner_name}_{tagline}", 
                'puuid': puuid,
                'summoner_name': summoner_name,
                'tagline': tagline,
                'region': region,
                'type': type
            }

            champion_data = {
                f'champions.{selected_champion}': {
                    'match_ids': champ_list,
                    'role': role
                }   
            }

            update_data = {**summoner_data, **champion_data}

            match_collection.update_one(
                {'_id': summoner_data['_id']},
                {'$set': update_data},
                upsert=True
            )

            #gather_match_info(summoner_name, tagline, selected_champion, region, mass_region, api_key, type)
            laning_diff(summoner_name, tagline, selected_champion, champ_list, puuid, region)
            df = gather_kill_data_master(champ_list, summoner_name, tagline, selected_champion, puuid, region)
            calculate_additional_stats(df, summoner_name, tagline, selected_champion)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    message = "Your data has been processed!"
    return message

@app.route('/player-stats', methods=['GET'])
def get_player_stats():
    '''data_normal = pd.read_csv("./match_info_csvs/kitkat_miffy_Kai'Sa_match_info.csv")
    
    bins = [0, 15, 20, 25, 30, 35, 40, float('inf')]
    labels = ['15 and less', '15-20', '20-25', '25-30', '30-35', '35-40', '40 and more']
    data_normal['duration_bucket'] = pd.cut(data_normal['duration'], bins=bins, labels=labels, right=False)

    duration_win_data_normal = data_normal.groupby('duration_bucket', observed=True).agg(
        win_count=('win', 'sum'),
        match_count=('duration', 'size')
    ).reset_index()
    duration_win_data_normal['win_rate'] = (duration_win_data_normal['win_count'] / duration_win_data_normal['match_count']) * 100
    data_normal = duration_win_data_normal.to_dict(orient='records')'''

    summoner_name = request.args.get('summonerName')
    tagline = request.args.get('tagline')
    champ_name = request.args.get('selectedChampion')
    user_id =  f"{summoner_name}_{tagline}"

    document_user = match_collection.find_one({'_id': user_id}) 
    match_data_user = document_user['match_data']
    data_user = pd.DataFrame.from_dict(match_data_user, orient='index')

    match_data_pro = gather_info(champ_name)
    data_pro = pd.DataFrame.from_dict(match_data_pro, orient='index')

    user_diffs = calculate_average_diffs(data_user)
    pro_diffs = calculate_average_diffs(data_pro)

    stats = get_advanced_stats(summoner_name, tagline, champ_name)
    pro_stats = get_pro_gank_stats(champ_name)

    return {
        'user': user_diffs,
        'pro': pro_diffs,
        'stats': stats,
        'pro_stats': pro_stats
    }

def gather_info(champ_name):
    query = {'type': 'Pro', f'champions.{champ_name}': {'$exists': True}}
    documents = match_collection.find(query)

    combined_matches = {}

    for document in documents:
        match_data = document['match_data']
        combined_matches.update(match_data)

    return combined_matches

def get_region_data(region):
    region_map = {
        "NA": ('americas', 'AMERICAS'),
        "BR": ('americas', 'AMERICAS'),
        "KR": ('asia', 'ASIA'),
        "JP": ('asia', 'ASIA'),
        "EUW": ('europe', 'EUROPE'),
        "EUNE": ('europe', 'EUROPE')
    }

    return region_map.get(region, (None, None))

def get_advanced_stats(summoner_name, tagline, champion_name):
    document = match_collection.find_one(
        {"_id": f"{summoner_name}_{tagline}", f"champions.{champion_name}": {"$exists": True}}
    )

    if document:
        champion_data = document['champions'].get(champion_name, {})
        stats = champion_data['stats']

        return {
            'Top Lane Ganks Per Game': stats.get('Top Lane Ganks Per Game'),
            'Mid Lane Ganks Per Game': stats.get('Mid Lane Ganks Per Game'),
            'Bot Lane Ganks Per Game': stats.get('Bot Lane Ganks Per Game')
        }
      
    else:
        return f"No data found for summoner {summoner_name} with champion {champion_name}."
    
def get_pro_gank_stats(champion_name):
    query = {"_id": champion_name}
    
    result = pro_champion_collection.find_one(query)
    
    if result:
        gank_stats = {
            'Top Lane Ganks Per Game': result['aggregated_stats'].get('Top Lane Ganks Per Game'),
            'Mid Lane Ganks Per Game': result['aggregated_stats'].get('Mid Lane Ganks Per Game'),
            'Bot Lane Ganks Per Game': result['aggregated_stats'].get('Bot Lane Ganks Per Game'),
        }
        return gank_stats
    else:
        return f"Champion {champion_name} not found."

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    app.run(debug=True)
    #socketio.run(app, debug=True)    