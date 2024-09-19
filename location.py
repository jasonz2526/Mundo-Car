from pymongo import MongoClient
import pandas as pd
import math, os
import cassiopeia as cass
from cassiopeia import Summoner, Champions, Maps, Tower, Side, Item

client = MongoClient('mongodb://localhost:27017')
db = client['league_database']
match_collection = db['matches']

def distance_to_segment(px, py, x1, y1, x2, y2):
    ABx = x2 - x1
    ABy = y2 - y1
    
    APx = px - x1
    APy = py - y1
    
    BPx = px - x2
    BPy = py - y2
  
    AB_AB = ABx * ABx + ABy * ABy
    AP_AB = APx * ABx + APy * ABy
    BP_AB = BPx * ABx + BPy * ABy

    if AP_AB <= 0:
        closest_x = x1
        closest_y = y1
    elif BP_AB >= 0:
        closest_x = x2
        closest_y = y2
    else:
        k = AP_AB / AB_AB
        closest_x = x1 + k * ABx
        closest_y = y1 + k * ABy

    dx = px - closest_x
    dy = py - closest_y
    return math.sqrt(dx * dx + dy * dy)

def is_within_distance(point, line_points, distance_threshold):
    for i in range(len(line_points) - 1):
        x1, y1 = line_points[i]
        x2, y2 = line_points[i + 1]
        if distance_to_segment(point[0], point[1], x1, y1, x2, y2) <= distance_threshold:
            return True
    return False

def get_kill_location(x, y, side):
    '''x = coordinates['x']
    y = coordinates['y']'''
    map_size = 14500
    adjusted_size = map_size - 1200

    top_lane_points = [
        (1200, 5000),                          
        (1200, 0.8 * adjusted_size),
        (1500, 0.9 * adjusted_size),
        (0.2 * map_size, adjusted_size),     
        (map_size - 5000, adjusted_size)                           
    ]
    
    mid_lane_points = [
        (4000, 4000),                             
        (map_size-4000, map_size-4000)                           
    ]
    
    bot_lane_points = [
        (5000, 1200),                          
        (0.8 * adjusted_size, 1200),
        (0.9 * adjusted_size, 1500),
        (adjusted_size, 0.2 * map_size),     
        (adjusted_size, map_size-5000)                           
    ]
    
    top_river_points = [
        (7250, 7250),
        (5400, 8850),
        (4250, 9350),
        (2500, map_size-2500)                           
    ]
    
    bot_river_points = [
        (map_size-2500, 2500),  
        (10250, 5100),
        (9100, 5600),
        (7250, 7250)                         
    ]

    check_point = (x,y)
    within_distance_top_lane = is_within_distance(check_point, top_lane_points, 500)
    within_distance_top_enclave = distance_between_points(check_point, (1500,13000), 500)
    within_distance_mid_lane = is_within_distance(check_point, mid_lane_points, 575)
    within_distance_bot_lane = is_within_distance(check_point, bot_lane_points, 500)
    within_distance_bot_enclave = distance_between_points(check_point, (13000,1500), 500)
    within_distance_top_river = is_within_distance(check_point, top_river_points, 500)
    within_distance_bot_river = is_within_distance(check_point, bot_river_points, 500)
    within_distance_blue_nexus = distance_between_points(check_point, (0,0), 5200)
    within_distance_red_nexus = distance_between_points(check_point, (map_size, map_size), 5200)
  
    if within_distance_top_lane or within_distance_top_enclave:
        return 'Top'
    elif within_distance_mid_lane:
        return 'Mid'
    elif within_distance_bot_lane or within_distance_bot_enclave:
        return 'Bot'
    elif within_distance_top_river:
        return 'Top River'
    elif within_distance_bot_river:
        return 'Bot River'
    elif within_distance_blue_nexus:
        return 'Own Nexus' if side == 'Blue' else 'Enemy Nexus'
    elif within_distance_red_nexus:
        return 'Own Nexus' if side == 'Red' else 'Enemy Nexus'
    if y > x:
        if y > -x + map_size:
            return 'Enemy Top Jungle' if side == 'Blue' else 'Own Top Jungle'
        else:
            return 'Own Top Jungle' if side == 'Blue' else 'Enemy Top Jungle'
    elif x > y:
        if y > -x + map_size:
            return 'Enemy Bot Jungle' if side == 'Blue' else 'Own Bot Jungle'
        else:
            return 'Own Bot Jungle' if side == 'Blue' else 'Enemy Bot Jungle'
    else:
        return 'NA'
    
def tower_location(x, y, side):
    map_size = 14500
    if y > -x + map_size:
        return 'Opponent' if side == 'Red' else 'Own'
    else:
        return 'Own' if side == 'Red' else 'Opponent'

def distance_between_points(point1, point2, distance_threshold):
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if distance <= distance_threshold:
        return True
    return False

def gather_kill_data_master(matches, summoner_name, tagline, selected_champion, puuid, region):  
    all_dataframes = [] 

    for match_id in matches:
        data = {
            'match_id': [],
            'Time (minutes)': [],
            'Jungle CS': [],
            'XP': [],
            'Gold': [],
            'Position': [],
            'Wards Placed': [],
            'Wards Destroyed': [],
            'Turrets KP': [],
            'Lane Gank': [],
            'Lane Gank Position': [],
            'KP': [],
            'KP Position': [],
            'Dragons': [],
            'Grubs': [],
            'Baron': [],
            'Opponent Jungle CS': [],
            'Opponent XP': [],
            'Opponent Gold': [],
            'Opponent Position': [],
            'Opponent Wards Placed': [],
            'Opponent Wards Destroyed': [],
            'Opponent Turrets KP': [],
            'Opponent Lane Gank': [],
            'Opponent Lane Gank Position': [],
            'Opponent KP': [],
            'Opponent KP Position': [],
            'Opponent Dragons': [],
            'Opponent Grubs': [],
            'Opponent Baron': [],
            #'Grubs Available'
            'Dragon Available': [],  
            'Baron Available': [],   
            'Top Turrets Taken': [],
            'Opponent Top Turrets Taken': [],
            'Mid Turrets Taken': [],
            'Opponent Mid Turrets Taken': [],
            'Bot Turrets Taken': [],
            'Opponent Bot Turrets Taken': [],
            'Nexus Turrets Taken': [],
            'Opponent Nexus Turrets Taken': [],
            'Inhibitors Taken': [],
            'Opponent Inhibitors Taken': [],
            'Win': []
        }

        try:
            match = cass.get_match(id=match_id, region=region)
            summoner = cass.get_summoner(puuid=puuid, region = region)
            timeline = match.timeline
            array_init = [0] * len(timeline.frames)
            text_init = ["N/A"] * len(timeline.frames)

            dragon_respawn_time = 5  
            baron_respawn_time = 6  

            dragon_available = False
            baron_available = False
            next_dragon_spawn = 5  
            next_baron_spawn = 20  

            for participant in match.participants:
                if participant.summoner == summoner:
                    user_participant = participant
                    id = user_participant.id
                    summoner_lane = user_participant.lane
                    summoner_team = user_participant.team
                    user_side = 'Blue' if user_participant.side == Side.blue else 'Red'

            for participant in match.participants:
                if participant.lane == summoner_lane and participant.team != summoner_team:
                    opponent_participant = participant
                    opponent_id = opponent_participant.id
                    opponent_side = 'Blue' if opponent_participant.side == Side.blue else 'Red'
    
            for minute, frame in enumerate(timeline.frames, start=0):
                if minute >= next_dragon_spawn:
                    dragon_available = True
                if minute >= next_baron_spawn:
                    baron_available = True

                participant_frame = frame.participant_frames[id]
                opponent_frame = frame.participant_frames[opponent_id]
                data['match_id'].append(match_id)
                data['Time (minutes)'].append(minute)
                data['Win'].append(user_participant.stats.win)
                data['Jungle CS'].append(participant_frame.neutral_minions_killed)
                data['XP'].append(participant_frame.experience)
                data['Gold'].append(participant_frame.gold_earned)
                data['Position'].append(get_kill_location(participant_frame.position.x, participant_frame.position.y, user_side))
                data['Wards Placed'].append(array_init[minute])
                data['Wards Destroyed'].append(array_init[minute])
                data['Turrets KP'].append(array_init[minute])
                data['Lane Gank'].append(array_init[minute])
                data['Lane Gank Position'].append(text_init[minute])
                data['KP'].append(array_init[minute])
                data['KP Position'].append(text_init[minute])
                data['Dragons'].append(array_init[minute])
                data['Grubs'].append(array_init[minute])
                data['Baron'].append(array_init[minute])
                data['Opponent Jungle CS'].append(opponent_frame.neutral_minions_killed)
                data['Opponent XP'].append(opponent_frame.experience)
                data['Opponent Gold'].append(opponent_frame.gold_earned)
                data['Opponent Position'].append(get_kill_location(opponent_frame.position.x, opponent_frame.position.y, opponent_side))
                data['Opponent Wards Placed'].append(array_init[minute])
                data['Opponent Wards Destroyed'].append(array_init[minute])
                data['Opponent Turrets KP'].append(array_init[minute])
                data['Opponent Lane Gank'].append(array_init[minute])
                data['Opponent Lane Gank Position'].append(text_init[minute])
                data['Opponent KP'].append(array_init[minute])
                data['Opponent KP Position'].append(text_init[minute])
                data['Opponent Dragons'].append(array_init[minute])
                data['Opponent Grubs'].append(array_init[minute])
                data['Opponent Baron'].append(array_init[minute])
                data['Dragon Available'].append(1 if dragon_available else 0)
                data['Baron Available'].append(1 if baron_available else 0)
                data['Top Turrets Taken'].append(array_init[minute])
                data['Opponent Top Turrets Taken'].append(array_init[minute])
                data['Mid Turrets Taken'].append(array_init[minute])
                data['Opponent Mid Turrets Taken'].append(array_init[minute])
                data['Bot Turrets Taken'].append(array_init[minute])
                data['Opponent Bot Turrets Taken'].append(array_init[minute])
                data['Nexus Turrets Taken'].append(array_init[minute])
                data['Opponent Nexus Turrets Taken'].append(array_init[minute])
                data['Inhibitors Taken'].append(array_init[minute])
                data['Opponent Inhibitors Taken'].append(array_init[minute])

            for event in user_participant.timeline.events:
                timedelta_obj = pd.to_timedelta(event.timestamp)
                event_minute = math.ceil(timedelta_obj.total_seconds() / 60)

                if event.type == "ITEM_PURCHASED":
                    #item = Item(id = event.item_id, region = "NA")
                    pass

                elif event.type == "WARD_PLACED":
                    data['Wards Placed'][event_minute] += 1

                elif event.type == "WARD_KILL":
                    data['Wards Destroyed'][event_minute] += 1

                elif event.type == "ELITE_MONSTER_KILL":
                    if event.monster_type == "DRAGON":
                        data['Dragons'][event_minute] += 1
                        dragon_available = False
                        next_dragon_spawn = event_minute + dragon_respawn_time
                        for i in range(event_minute, min(event_minute + dragon_respawn_time, len(data['Dragon Available']))):
                            data['Dragon Available'][i] = 0
                    elif event.monster_type == "HORDE":
                        data['Grubs'][event_minute] += 1
                    elif event.monster_type == "BARON_NASHOR":
                        data['Baron'][event_minute] += 1
                        baron_available = False
                        next_baron_spawn = event_minute + baron_respawn_time
                        for i in range(event_minute, min(event_minute + baron_respawn_time, len(data['Baron Available']))):
                            data['Baron Available'][i] = 0

                elif event.type == "BUILDING_KILL":
                    data['Turrets KP'][event_minute] += 1

                elif event.type == "CHAMPION_KILL" and event.victim_id != user_participant.id:
                    x = event.position.x 
                    y = event.position.y
                    kill_location = get_kill_location(x, y, user_side)
                    if event_minute < 16 and kill_location in ["Top", "Top River", "Mid", "Bot", "Bot River"]:
                        data['Lane Gank'][event_minute] = 1
                    
                        if kill_location == "Top" or kill_location == "Top River":
                            data['Lane Gank Position'][event_minute] = "Top"
                        elif kill_location == "Mid":
                            data['Lane Gank Position'][event_minute] = "Mid"
                        elif kill_location == "Bot" or kill_location == "Bot River":
                            data['Lane Gank Position'][event_minute] = "Bot"

                    data['KP'][event_minute] += 1
                    data['KP Position'][event_minute] = kill_location
                
            for event in opponent_participant.timeline.events:
                timedelta_obj = pd.to_timedelta(event.timestamp)
                event_minute = math.ceil(timedelta_obj.total_seconds() / 60)

                if event.type == "ITEM_PURCHASED":
                    #item = Item(id = event.item_id, region = "NA")
                    pass

                elif event.type == "WARD_PLACED":
                    data['Opponent Wards Placed'][event_minute] += 1

                elif event.type == "WARD_KILL":
                    data['Opponent Wards Destroyed'][event_minute] += 1

                elif event.type == "ELITE_MONSTER_KILL":
                    if event.monster_type == "DRAGON":
                        data['Opponent Dragons'][event_minute] += 1
                        dragon_available = False
                        next_dragon_spawn = event_minute + dragon_respawn_time
                        for i in range(event_minute, min(event_minute + dragon_respawn_time, len(data['Dragon Available']))):
                            data['Dragon Available'][i] = 0
                    elif event.monster_type == "HORDE":
                        data['Opponent Grubs'][event_minute] += 1
                    elif event.monster_type == "BARON_NASHOR":
                        data['Opponent Baron'][event_minute] += 1
                        baron_available = False
                        next_baron_spawn = event_minute + baron_respawn_time
                        for i in range(event_minute, min(event_minute + baron_respawn_time, len(data['Baron Available']))):
                            data['Baron Available'][i] = 0

                elif event.type == "BUILDING_KILL":
                    data['Opponent Turrets KP'][event_minute] += 1

                if event.type == "CHAMPION_KILL" and event.victim_id != opponent_participant.id:
                    x = event.position.x 
                    y = event.position.y
                    kill_location = get_kill_location(x, y, user_side)
                    if event_minute < 16 and kill_location in ["Top", "Top River", "Mid", "Bot", "Bot River"]:
                        data['Opponent Lane Gank'][event_minute] = 1
                        
                        if kill_location == "Top" or kill_location == "Top River":
                            data['Opponent Lane Gank Position'][event_minute] = "Top"
                        elif kill_location == "Mid":
                            data['Opponent Lane Gank Position'][event_minute] = "Mid"
                        elif kill_location == "Bot" or kill_location == "Bot River":
                            data['Opponent Lane Gank Position'][event_minute] = "Bot"

                    data['Opponent KP'][event_minute] += 1
                    data['Opponent KP Position'][event_minute] = kill_location
            
            for frame in timeline.frames:
                for event in frame.events:
                    if event.type == "BUILDING_KILL" and event.building_type == "TOWER_BUILDING":
                        timedelta_obj = pd.to_timedelta(event.timestamp)
                        event_minute = math.ceil(timedelta_obj.total_seconds() / 60)
                        location = tower_location(event.position.x, event.position.y, user_side)
                        if event.lane_type == "TOP_LANE":
                            if location == 'Own':
                                data['Top Turrets Taken'][event_minute] += 1
                            else:
                                data['Opponent Top Turrets Taken'][event_minute] += 1
                        elif event.lane_type == "MID_LANE":
                            if location == 'Own':
                                if event.tower_type == Tower.NEXUS:
                                    data['Nexus Turrets Taken'][event_minute] += 1
                                else:
                                    data['Mid Turrets Taken'][event_minute] += 1
                            else:
                                if event.tower_type == Tower.NEXUS:
                                    data['Opponent Nexus Turrets Taken'][event_minute] += 1
                                else:
                                    data['Opponent Mid Turrets Taken'][event_minute] += 1
                        elif event.lane_type == "BOT_LANE":
                            if location == 'Own':
                                data['Bot Turrets Taken'][event_minute] += 1
                            else:
                                data['Opponent Bot Turrets Taken'][event_minute] += 1

                    elif event.type == "BUILDING_KILL" and event.building_type == "INHIBITOR_BUILDING":
                        timedelta_obj = pd.to_timedelta(event.timestamp)
                        event_minute = math.ceil(timedelta_obj.total_seconds() / 60)
                        location = tower_location(event.position.x, event.position.y, user_side)
                        if location == 'Own':
                            data['Inhibitors Taken'][event_minute] += 1
                        else:
                            data['Opponent Inhibitors Taken'][event_minute] += 1

            match_df = pd.DataFrame(data)
            all_dataframes.append(match_df)

        except AttributeError:
            continue
        except IndexError:
            continue

    combined_df = pd.concat(all_dataframes, ignore_index=True)
    print(combined_df)

    match_data = {}
    for index, row in combined_df.iterrows():
        match_id = str(row['match_id'])
        minute = int(row['Time (minutes)'])

        if match_id not in match_data:
            match_data[match_id] = {}

        row_data = row.drop(labels=['match_id', 'Time (minutes)']).to_dict()

        match_data[match_id][minute] = row_data

    for match_id, match_info in match_data.items():
        for minute, minute_data in match_info.items():
            match_collection.update_one(
                {'_id': f"{summoner_name}_{tagline}"},
                {
                    '$set': {f'match_data.{match_id}.{minute}': minute_data},
                    '$setOnInsert': {'champion': selected_champion}
                },
                upsert=True
            )
    return combined_df