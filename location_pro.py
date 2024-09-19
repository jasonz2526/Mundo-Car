import os
from pymongo import MongoClient
import cassiopeia as cass
from location import gather_kill_data_master

client = MongoClient('mongodb://localhost:27017')
db = client['league_database']
match_collection = db['matches']


def construct_pro_location_data(champion_name):

    query = {
        'type': 'Pro',
        f'champions.{champion_name}': {'$exists': True}
    }

    projection = {
        '_id': 1,      
        'puuid': 1,
        'region': 1,
        f'champions.{champion_name}.match_ids': 1  
    }

    results = match_collection.find(query, projection)

    for result in results:
        summoner_name, tagline = result['_id'].split('_')
        puuid = result['puuid']
        region = result['region']
        match_ids = result.get('champions', {}).get(champion_name, {}).get('match_ids', [])
        int_match_ids = [int(match_id) for match_id in match_ids]  
        
        if int_match_ids:
            df = gather_kill_data_master(int_match_ids, summoner_name, tagline, champion_name, puuid, region)

            print(f"Processed data for {summoner_name}_{tagline}")
            file_name = f"pro_{champion_name}_location_data.csv"

            if not os.path.isfile(file_name):
                df.to_csv(file_name, mode='a', header=True, index=False)
            else:
                df.to_csv(file_name, mode='a', header=False, index=False)
        else: 
            continue


construct_pro_location_data('Viego')