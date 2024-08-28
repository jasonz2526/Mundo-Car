from flask import Flask, jsonify, request
from flask_socketio import SocketIO
import pandas as pd
from flask_cors import CORS
from riot_api import get_puuid, get_matches_with_champion
from data_gathering import calculate_average_diffs
import cassiopeia as cass
import os, json
from pymongo import MongoClient

app = Flask(__name__)
CORS(app) 
socketio = SocketIO(app, cors_allowed_origins="*")

client = MongoClient('mongodb://localhost:27017')
db = client['league_database']
match_collection = db['matches']

CACHE_FILE = 'cache.json'
cacheSwitch = False
hitCount = 5
limit = 10000

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

    '''document_pro = match_collection.find_one({'_id': 'kafkaesk_lay'}) 
    match_data_pro = document_pro['match_data']
    data_pro = pd.DataFrame.from_dict(match_data_pro, orient='index')'''

    match_data_pro = gather_info(champ_name)
    data_pro = pd.DataFrame.from_dict(match_data_pro, orient='index')

    user_diffs = calculate_average_diffs(data_user)
    pro_diffs = calculate_average_diffs(data_pro)

    return {
        'user': user_diffs,
        'pro': pro_diffs
    }

def gather_info(champ_name):
 
    # champ_name = 'Evelynn'
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

def laning_diff(summoner_name, tagline, selected_champion, matches, puuid, region):
    a_summoner = cass.get_summoner(puuid=puuid, region=region)
    match_data = {}

    for match_id in matches:
        try:
            match = cass.get_match(id=match_id, region=region)
            timeline = match.timeline
            
            for participant in match.participants:
                if participant.summoner == a_summoner:
                    id = participant.id
                    summoner_lane = participant.lane
                    summoner_team = participant.team
                    win = participant.stats.win

            opponent_id = None
            for participant in match.participants:
                if participant.lane == summoner_lane and participant.team != summoner_team:
                    opponent_id = participant.id

            cs_diff_5, cs_diff_10, cs_diff_15 = None, None, None
            gold_diff_5, gold_diff_10, gold_diff_15 = None, None, None
            xp_diff_5, xp_diff_10, xp_diff_15 = None, None, None

            for minute, frame in enumerate(timeline.frames, start=1):
                participant_frame = frame.participant_frames[id]
                opponent_frame = frame.participant_frames[opponent_id]
                
                if minute == 5:
                    cs_diff_5 = participant_frame.creep_score - opponent_frame.creep_score
                    gold_diff_5 = participant_frame.gold_earned - opponent_frame.gold_earned
                    xp_diff_5 = participant_frame.experience - opponent_frame.experience
                elif minute == 10:
                    cs_diff_10 = participant_frame.creep_score - opponent_frame.creep_score
                    gold_diff_10 = participant_frame.gold_earned - opponent_frame.gold_earned
                    xp_diff_10 = participant_frame.experience - opponent_frame.experience
                elif minute == 15:
                    cs_diff_15 = participant_frame.creep_score - opponent_frame.creep_score
                    gold_diff_15 = participant_frame.gold_earned - opponent_frame.gold_earned
                    xp_diff_15 = participant_frame.experience - opponent_frame.experience

            match_data[match_id] = {
                'cs_diff_5': cs_diff_5,
                'cs_diff_10': cs_diff_10,
                'cs_diff_15': cs_diff_15,
                'gold_diff_5': gold_diff_5,
                'gold_diff_10': gold_diff_10,
                'gold_diff_15': gold_diff_15,
                'xp_diff_5': xp_diff_5,
                'xp_diff_10': xp_diff_10,
                'xp_diff_15': xp_diff_15,
                'win': win
            }

        except Exception as error:
            print(error)
            continue

    match_collection.update_one(
        {'_id': f"{summoner_name}_{tagline}"},
        {
            '$set': {f'match_data.{match_id}': match_info for match_id, match_info in match_data.items()},
            '$setOnInsert': {'champion': selected_champion}
        },
        upsert=True
    )

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    app.run(debug=True)
    #socketio.run(app, debug=True)

