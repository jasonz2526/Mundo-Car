import requests
from flask import jsonify
import cassiopeia as cass
import pandas as pd

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

def get_matches_with_champion(champion_name, summoner, puuid, continent, region, num):
    match_history = cass.get_match_history(continent=continent, puuid=puuid)
    match_list = []
    regional_name = get_champ_name(region, champion_name)
    
    count = 0
    for match in match_history:
        try:
            if (match.participants and match.is_remake == False and 
                (match.queue.id == 420 or match.queue.id == 440 or match.queue.id == 490)): #Proper Queues for Analysis
                if count == num:
                    break
                for participant in match.participants:
                    if participant.summoner == summoner and participant.champion.name == regional_name:
                            match_list.append(match.id)
                            count += 1
        except AttributeError:
            continue
        except IndexError:
            continue
    return match_list