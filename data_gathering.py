import cassiopeia as cass
import pandas as pd
import fnmatch, os, csv
from riot_api import get_puuid

def get_match_data_adjusted(matches, puuid, region):
    data = {
        'match_id': [],
        'assists': [],
        'baron_kills': [],
        'bounty_level': [],
        'champion_experience': [],
        'consumables_purchased': [],
        'damage_dealt_to_buildings': [],
        'damage_dealt_to_objectives': [],
        'damage_dealt_to_turrets': [],
        'damage_self_mitigated': [],
        'deaths': [],
        'double_kills': [],
        'dragon_kills': [],
        'duration': [],
        'first_blood_assist': [],
        'first_blood_kill': [],
        'first_tower_assist': [],
        'first_tower_kill': [],
        'gold_earned': [],
        'gold_spent': [],
        'inhibitor_kills': [],
        'inhibitor_takedowns': [],
        'inhibitors_lost': [],
        #'items': [],
        #'items_purchased': [],
        'kda': [],
        'killing_sprees': [],
        'kills': [],
        'largest_critical_strike': [],
        'largest_killing_spree': [],
        'largest_multi_kill': [],
        'level': [],
        'longest_time_spent_living': [],
        'magic_damage_dealt': [],
        'magic_damage_dealt_to_champions': [],
        'magic_damage_taken': [],
        'neutral_minions_killed': [],
        'nexus_kills': [],
        'nexus_lost': [],
        'nexus_takedowns': [],
        'objectives_stolen': [],
        'objectives_stolen_assists': [],
        'penta_kills': [],
        'physical_damage_dealt': [],
        'physical_damage_dealt_to_champions': [],
        'physical_damage_taken': [],
        'quadra_kills': [],
        'sight_wards_bought': [],
        'spell_1_casts': [],
        'spell_2_casts': [],
        'spell_3_casts': [],
        'spell_4_casts': [],
        'summoner_spell_1_casts': [],
        'summoner_spell_2_casts': [],
        'time_CCing_others': [],
        'time_played': [],
        'total_damage_dealt': [],
        'total_damage_dealt_to_champions': [],
        'total_damage_shielded_on_teammates': [],
        'total_damage_taken': [],
        'total_heal': [],
        'total_heals_on_teammates': [],
        'total_minions_killed': [],
        'total_time_cc_dealt': [],
        'total_time_spent_dead': [],
        'total_units_healed': [],
        'triple_kills': [],
        'true_damage_dealt': [],
        'true_damage_dealt_to_champions': [],
        'true_damage_taken': [],
        'turret_kills': [],
        'turret_takedowns': [],
        'turrets_lost': [],
        'vision_score': [],
        'vision_wards_bought': [],
        'vision_wards_placed': [],
        'wards_killed': [],
        'wards_placed': [],
        'win': [] 
    }

    for match_id in matches:
        match = cass.get_match(id=match_id, region=region)
        try:
            duration_original = match.duration
            timedelta_obj = pd.to_timedelta(duration_original)
            duration = timedelta_obj.total_seconds() / 60
            for participant in match.participants:
                if participant.summoner.puuid == puuid:
                    stats = participant.stats
                    data['match_id'].append(match_id)
                    
                    standard_duration = 30
                    
                    def adjust_stat(stat):
                        return stat * (standard_duration / duration)
                    
                    # Adjust stats to 30 minutes
                    data['assists'].append(adjust_stat(stats.assists))
                    data['baron_kills'].append(adjust_stat(stats.baron_kills))
                    data['bounty_level'].append(stats.bounty_level)  
                    data['champion_experience'].append(adjust_stat(stats.champion_experience))
                    data['consumables_purchased'].append(adjust_stat(stats.consumables_purchased))
                    data['damage_dealt_to_buildings'].append(adjust_stat(stats.damage_dealt_to_buildings))
                    data['damage_dealt_to_objectives'].append(adjust_stat(stats.damage_dealt_to_objectives))
                    data['damage_dealt_to_turrets'].append(adjust_stat(stats.damage_dealt_to_turrets))
                    data['damage_self_mitigated'].append(adjust_stat(stats.damage_self_mitigated))
                    data['deaths'].append(adjust_stat(stats.deaths))
                    data['double_kills'].append(adjust_stat(stats.double_kills))
                    data['dragon_kills'].append(adjust_stat(stats.dragon_kills))
                    data['duration'].append(duration)
                    data['first_blood_assist'].append(stats.first_blood_assist)
                    data['first_blood_kill'].append(stats.first_blood_kill)
                    data['first_tower_assist'].append(stats.first_tower_assist)
                    data['first_tower_kill'].append(stats.first_tower_kill)
                    data['gold_earned'].append(adjust_stat(stats.gold_earned))
                    data['gold_spent'].append(adjust_stat(stats.gold_spent))
                    data['inhibitor_kills'].append(adjust_stat(stats.inhibitor_kills))
                    data['inhibitor_takedowns'].append(adjust_stat(stats.inhibitor_takedowns))
                    data['inhibitors_lost'].append(adjust_stat(stats.inhibitors_lost))
                    data['kda'].append(stats.kda)  
                    data['killing_sprees'].append(adjust_stat(stats.killing_sprees))
                    data['kills'].append(adjust_stat(stats.kills))
                    data['largest_critical_strike'].append(adjust_stat(stats.largest_critical_strike))
                    data['largest_killing_spree'].append(adjust_stat(stats.largest_killing_spree))
                    data['largest_multi_kill'].append(adjust_stat(stats.largest_multi_kill))
                    data['level'].append(stats.level)  #
                    data['longest_time_spent_living'].append(adjust_stat(stats.longest_time_spent_living))
                    data['magic_damage_dealt'].append(adjust_stat(stats.magic_damage_dealt))
                    data['magic_damage_dealt_to_champions'].append(adjust_stat(stats.magic_damage_dealt_to_champions))
                    data['magic_damage_taken'].append(adjust_stat(stats.magic_damage_taken))
                    data['neutral_minions_killed'].append(adjust_stat(stats.neutral_minions_killed))
                    data['nexus_kills'].append(adjust_stat(stats.nexus_kills))
                    data['nexus_lost'].append(adjust_stat(stats.nexus_lost))
                    data['nexus_takedowns'].append(adjust_stat(stats.nexus_takedowns))
                    data['objectives_stolen'].append(adjust_stat(stats.objectives_stolen))
                    data['objectives_stolen_assists'].append(adjust_stat(stats.objectives_stolen_assists))
                    data['penta_kills'].append(adjust_stat(stats.penta_kills))
                    data['physical_damage_dealt'].append(adjust_stat(stats.physical_damage_dealt))
                    data['physical_damage_dealt_to_champions'].append(adjust_stat(stats.physical_damage_dealt_to_champions))
                    data['physical_damage_taken'].append(adjust_stat(stats.physical_damage_taken))
                    data['quadra_kills'].append(adjust_stat(stats.quadra_kills))
                    data['sight_wards_bought'].append(adjust_stat(stats.sight_wards_bought))
                    data['spell_1_casts'].append(adjust_stat(stats.spell_1_casts))
                    data['spell_2_casts'].append(adjust_stat(stats.spell_2_casts))
                    data['spell_3_casts'].append(adjust_stat(stats.spell_3_casts))
                    data['spell_4_casts'].append(adjust_stat(stats.spell_4_casts))
                    data['summoner_spell_1_casts'].append(adjust_stat(stats.summoner_spell_1_casts))
                    data['summoner_spell_2_casts'].append(adjust_stat(stats.summoner_spell_2_casts))
                    data['time_CCing_others'].append(adjust_stat(stats.time_CCing_others))
                    data['time_played'].append(adjust_stat(stats.time_played))
                    data['total_damage_dealt'].append(adjust_stat(stats.total_damage_dealt))
                    data['total_damage_dealt_to_champions'].append(adjust_stat(stats.total_damage_dealt_to_champions))
                    data['total_damage_shielded_on_teammates'].append(adjust_stat(stats.total_damage_shielded_on_teammates))
                    data['total_damage_taken'].append(adjust_stat(stats.total_damage_taken))
                    data['total_heal'].append(adjust_stat(stats.total_heal))
                    data['total_heals_on_teammates'].append(adjust_stat(stats.total_heals_on_teammates))
                    data['total_minions_killed'].append(adjust_stat(stats.total_minions_killed))
                    data['total_time_cc_dealt'].append(adjust_stat(stats.total_time_cc_dealt))
                    data['total_time_spent_dead'].append(adjust_stat(stats.total_time_spent_dead))
                    data['total_units_healed'].append(adjust_stat(stats.total_units_healed))
                    data['triple_kills'].append(adjust_stat(stats.triple_kills))
                    data['true_damage_dealt'].append(adjust_stat(stats.true_damage_dealt))
                    data['true_damage_dealt_to_champions'].append(adjust_stat(stats.true_damage_dealt_to_champions))
                    data['true_damage_taken'].append(adjust_stat(stats.true_damage_taken))
                    data['turret_kills'].append(adjust_stat(stats.turret_kills))
                    data['turret_takedowns'].append(adjust_stat(stats.turret_takedowns))
                    data['turrets_lost'].append(adjust_stat(stats.turrets_lost))
                    data['vision_score'].append(adjust_stat(stats.vision_score))
                    data['vision_wards_bought'].append(adjust_stat(stats.vision_wards_bought))
                    data['vision_wards_placed'].append(adjust_stat(stats.vision_wards_placed))
                    data['wards_killed'].append(adjust_stat(stats.wards_killed))
                    data['wards_placed'].append(adjust_stat(stats.wards_placed))
                    data['win'].append(stats.win)  
        except:
            continue
    df = pd.DataFrame(data)
    return df         

def read_csv(file_path):
    match_list = []
    name = open(file_path, 'r')
    file = csv.DictReader(name)
    for col in file:
        match_list.append(int(col['Match ID']))
    return match_list

def search_csvs(summoner_name, tagline, selected_champion, type):
    if type == 'Pro':
        directory = '/Users/jasonzhao/Desktop/Jungle-Diff/pro_ids_csvs/'
    else:
        directory = '/Users/jasonzhao/Desktop/Jungle-Diff/match_ids_csvs/'
    search_pattern = f"{summoner_name}_{tagline}_{selected_champion}_*"
    try:
        matching_files = [os.path.join(directory, f) for f in os.listdir(directory) if fnmatch.fnmatch(f.lower(), search_pattern.lower())]
        return matching_files
    except Exception as e:
        print(f"Error: {e}")
        return []

def gather_match_info(summoner_name, tagline, selected_champion, region, mass_region, api_key, type):
    champ_csvs = search_csvs(summoner_name, tagline, selected_champion, type)
    ex_csv = read_csv(champ_csvs[0])
    puuid = get_puuid(summoner_name,tagline,mass_region,api_key)
    ex_data = get_match_data_adjusted(ex_csv,puuid=puuid,region=region)
    if type == 'Pro':
        csv_folder = 'pro_match_info_csvs'
    else:
        csv_folder = 'match_info_csvs'
    csv_filename = f"{summoner_name}_{tagline}_{selected_champion}_match_info.csv"
    csv_file_path = os.path.join(csv_folder, csv_filename)
    ex_data.to_csv(csv_file_path)
