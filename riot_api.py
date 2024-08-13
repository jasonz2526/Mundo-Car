import requests
from flask import jsonify
import cassiopeia as cass
import pandas as pd
import flask_socketio 

cass.set_riot_api_key('RGAPI-28887941-ef83-4b09-869e-a51fd2e2b671')

def get_puuid(summoner_name, tagline, mass_region, api_key):
    api_url = (
        "https://" + 
        mass_region +
        ".api.riotgames.com/riot/account/v1/accounts/by-riot-id/" +
        summoner_name +
        "/" +
        tagline +
        "?api_key=" +
        api_key
    )
    
    print(api_url)
    
    resp = requests.get(api_url)
    player_info = resp.json()
    
    if 'puuid' in player_info:
        return player_info['puuid']
    elif 'status' in player_info and player_info['status']['status_code'] == 404:
        return jsonify({
            'error': 'Summoner not found.'
        }), 404
    else:
        return jsonify({
            'error': 'Unknown error occurred.'
        }), 500
    
def get_champ_name(region, champion_name):
    if(region == "NA" or region == "EUNE" or region == "EUW" or region == "BR"):
        return champion_name
    na_champs = cass.get_champions(region = "NA")
    for champ in na_champs:
        if(champ.name == champion_name):
            id = champ.id 
    regional_champ = cass.get_champions(region = region)
    for champ in regional_champ:
        if(champ.id == id):
            regional_name = champ.name
    return regional_name

def get_matches_with_champion(champion_name, summoner, puuid, continent, region, num, limit):
    match_history = cass.get_match_history(continent=continent, puuid=puuid)
    match_list = []
    regional_name = get_champ_name(region, champion_name)
    
    hit_count = 0
    total_count = 0
    for match in match_history:
        total_count += 1
        try:
            queue_type = match.queue.id
            if (match.participants and match.is_remake == False and 
                (queue_type in [420, 440, 490])): #Proper Queues for Analysis
                if hit_count == num:
                    break
                if total_count == limit:
                    return None
                for participant in match.participants:
                    if participant.summoner == summoner and participant.champion.name == regional_name:
                        match_list.append(match.id)
                        hit_count += 1
                        #emit('progress', (hit_count / num) * 100)
                        print((hit_count / num) * 100)
                        flask_socketio.emit('progress', {'progress': (hit_count / num) * 100}, namespace='/')
        except AttributeError:
            continue
        except IndexError:
            continue
        except:
            continue
    return match_list