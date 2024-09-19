import pandas as pd
from openai import OpenAI
from API_KEY import OPENAI_API_KEY
from pymongo import MongoClient

client = OpenAI(
    api_key= OPENAI_API_KEY
)

client = MongoClient('mongodb://localhost:27017/')
db = client['league_database']
match_collection = db['matches']
pro_champion_collection = db['pros']


def get_df(summoner_name, tagline):
    
    document = match_collection.find_one({'_id': f"{summoner_name}_{tagline}"})

    rows = []

    if 'match_data' in document:
        match_data = document['match_data']
        for match_id, match_info in match_data.items():
            for minute, minute_data in match_info.items():
                if isinstance(minute_data, dict):
                    row = {
                        'match_id': match_id,          
                        'Time (minutes)': int(minute)   
                    }
                    row.update({k: v for k, v in minute_data.items() if not k.startswith(('cs_diff', 'gold_diff', 'xp_diff', 'win'))})
                    rows.append(row)

    df = pd.DataFrame(rows)

    cols = ['match_id', 'Time (minutes)'] + [col for col in df.columns if col not in ['match_id', 'Time (minutes)']]
    df = df[cols]
    return df

def calculate_additional_stats(df, summoner_name, tagline, champion_name):
    stats = {}
    total_games = len(df['match_id'].unique())
    grouped_df = df.groupby('match_id')

    def cs_trends_and_comparisons(df):
        cs_loss_games = 0
        cs_diff_total = 0
        cs_trend_count = 0

        for match_id, game_data in df.groupby('match_id'):
            early_game = game_data[game_data['Time (minutes)'] <= 14]
            late_game = game_data[game_data['Time (minutes)'] > 25]

            early_cs_per_min = early_game['Jungle CS'].mean() if not early_game.empty else 0
            late_cs_per_min = late_game['Jungle CS'].mean() if not late_game.empty else 0

            if early_cs_per_min > 7 and late_cs_per_min < 5:
                cs_loss_games += 1

            cs_diff_per_game = (game_data['Jungle CS'].sum() - game_data['Opponent Jungle CS'].sum()) / len(game_data)
            cs_diff_total += cs_diff_per_game
            cs_trend_count += 1

        return cs_loss_games / total_games if total_games > 0 else 0, cs_diff_total / cs_trend_count if cs_trend_count > 0 else 0

    stats['Dragons Taken Per Game'] = grouped_df['Dragons'].sum().mean()
    stats['Baron Taken Per Game'] = grouped_df['Baron'].sum().mean()

    stats['Top Lane Ganks Per Game'] = grouped_df['Lane Gank Position'].transform(lambda x: (x == 'Top').sum()).mean()
    stats['Mid Lane Ganks Per Game'] = grouped_df['Lane Gank Position'].transform(lambda x: (x == 'Mid').sum()).mean()
    stats['Bot Lane Ganks Per Game'] = grouped_df['Lane Gank Position'].transform(lambda x: (x == 'Bot').sum()).mean()


    cs_loss_percentage, average_cs_diff = cs_trends_and_comparisons(df)
    stats['CS Loss Games Percentage'] = cs_loss_percentage
    stats['Average CS Difference'] = average_cs_diff

    stats['Wards Placed Per Game'] = grouped_df['Wards Placed'].sum().mean()
    stats['Wards Destroyed Per Game'] = grouped_df['Wards Destroyed'].sum().mean()

    stats['Jungler KP Per Game'] = grouped_df['KP'].sum().mean()
    stats['Opponent KP Per Game'] = grouped_df['Opponent KP'].sum().mean()
    stats['KP Difference Per Game'] = (grouped_df['KP'].sum() - grouped_df['Opponent KP'].sum()).mean()

    stats['Jungler Dragons Per Game'] = grouped_df['Dragons'].sum().mean()
    stats['Opponent Dragons Per Game'] = grouped_df['Opponent Dragons'].sum().mean()
    stats['Dragon Difference Per Game'] = (grouped_df['Dragons'].sum() - grouped_df['Opponent Dragons'].sum()).mean()

    stats['Jungler Barons Per Game'] = grouped_df['Baron'].sum().mean()
    stats['Opponent Barons Per Game'] = grouped_df['Opponent Baron'].sum().mean()
    stats['Baron Difference Per Game'] = (grouped_df['Baron'].sum() - grouped_df['Opponent Baron'].sum()).mean()

    stats['Jungle CS Difference Per Game'] = grouped_df.apply(
        lambda x: (x['Jungle CS'].sum() - x['Opponent Jungle CS'].sum()) / len(x)
    ,include_groups=False).mean()

    # Advanced Metrics
    def bot_lane_pressure():
        bot_ganks = grouped_df['Lane Gank Position'].transform(lambda x: (x == 'Bot').sum())
        bot_dragons = grouped_df['Dragons'].transform('sum')
        bot_barons = grouped_df['Baron'].transform('sum')
        total_objectives = bot_dragons + bot_barons
        if total_objectives.sum() == 0:
            return float('nan')
        pressure = bot_ganks / total_objectives
        return pressure.mean()


    def bot_lane_pressure_impact():
        gank_position = grouped_df['Lane Gank Position'].transform(lambda x: (x == 'Bot').sum())
        wins = grouped_df['Win'].transform('sum')

        total_bot_ganks = gank_position.sum()
        if total_bot_ganks == 0:
            return float('nan')

        win_rate = wins[gank_position > 0].sum() / total_bot_ganks
        return win_rate

    def gank_efficiency_relative_to_objectives():
        ganks_sum = grouped_df['Lane Gank'].sum().sum()
        dragons_taken_sum = grouped_df['Dragons'].sum().sum()
        barons_taken_sum = grouped_df['Baron'].sum().sum()
        
        if ganks_sum == 0:
            return float('nan')
        
        efficiency = (dragons_taken_sum + barons_taken_sum) / ganks_sum
        return efficiency

    def lane_influence_score():
        def calculate_lane_score(x, lane):
            ganks = (x['Lane Gank Position'] == lane).sum()
            turrets_taken = x[[f'{lane} Turrets Taken']].sum() if f'{lane} Turrets Taken' in x.columns else 0
            return ganks + turrets_taken

        top_lane_score = grouped_df.apply(lambda x: calculate_lane_score(x, 'Top'), include_groups=False).mean()
        mid_lane_score = grouped_df.apply(lambda x: calculate_lane_score(x, 'Mid'), include_groups=False).mean()
        bot_lane_score = grouped_df.apply(lambda x: calculate_lane_score(x, 'Bot'), include_groups=False).mean()

        return {'Top Lane Score': top_lane_score, 'Mid Lane Score': mid_lane_score, 'Bot Lane Score': bot_lane_score}

    def objective_control_impact():
        objective_control = grouped_df.apply(lambda x: (x['Dragons'].sum() + x['Baron'].sum()) / len(x), include_groups=False)
        win_rate = grouped_df['Win'].mean()
        if objective_control.sum() == 0:
            return float('nan')
        impact = win_rate / objective_control
        return impact.mean()

    def snowball_efficiency():
        early_lead_games = grouped_df.apply(lambda x: x['Jungle CS'].mean() > 7, include_groups=False)
        early_lead_wins = grouped_df.apply(lambda x: (x['Jungle CS'].mean() > 7) & (x['Win']), include_groups=False)
        if early_lead_games.sum() == 0:
            return float('nan')
        efficiency = early_lead_wins.sum() / early_lead_games.sum()
        return efficiency.mean()

    def average_time_in_key_areas(area):
        if area == 'enemy jungle':
            key_positions = ['Enemy Top Jungle', 'Enemy Bot Jungle']
        elif area == 'own jungle':
            key_positions = ['Own Top Jungle', 'Own Bot Jungle']
        else:
            raise ValueError("Area must be either 'enemy jungle' or 'own jungle'")

        total_time = grouped_df.apply(lambda x: (x['Position'].isin(key_positions)).sum())

        total_games = len(df['match_id'].unique())

        average_time = total_time / total_games if total_games > 0 else 0
        
        return average_time

    stats['Bot Lane Pressure'] = bot_lane_pressure()
    stats['Bot Lane Pressure Impact on Win Rate'] = bot_lane_pressure_impact()
    stats['Gank Efficiency Relative to Objectives'] = gank_efficiency_relative_to_objectives()
    
    #lane_scores = lane_influence_score()
    #stats.update(lane_scores)

    stats['Objective Control Impact'] = objective_control_impact()
    stats['Snowball Efficiency'] = snowball_efficiency()


    query = {"summoner_name": summoner_name, "tagline": tagline}

    update = {
        "$set": {
            **{f"champions.{champion_name}.stats.{key}": value for key, value in stats.items()}  # Add stats dynamically
        }
    }
    match_collection.update_one(query, update)
    return stats

def extract_key_stats(stats):
    return {
        "Dragons Taken Per Game": stats.get('Dragons Taken Per Game'),
        "Baron Taken Per Game": stats.get('Baron Taken Per Game'),
        "Gank Efficiency Relative to Objectives": stats.get('Gank Efficiency Relative to Objectives'),
        "Objective Control Impact": stats.get('Objective Control Impact'),
        "Snowball Efficiency": stats.get('Snowball Efficiency'),
        "Average CS Difference": stats.get('Average CS Difference')
    }

'''pro_data_summary = extract_key_stats(pro_stats)
user_data_summary = extract_key_stats(user_stats)

print("Pro Stats:")
for stat, value in pro_stats.items():
    print(f"{stat}: {value}")

print("\nUser Stats:")
for stat, value in user_stats.items():
    print(f"{stat}: {value}")
'

key_metrics_info = (
    "Definitions:\n"
    "1. **Snowball Efficiency**: The effectiveness of leveraging early game leads into later game advantages. High efficiency indicates better utilization of early leads to secure objectives and victories.\n"
    "2. **Objective Control Impact**: Measures how well control of objectives (Dragons and Baron) impacts win rate. A higher score suggests a stronger correlation between objectives and winning.\n"
    "3. **Gank Efficiency Relative to Objectives**: Evaluates the effectiveness of ganks based on the number of objectives taken. A higher efficiency means better conversion of ganks into objectives.\n"
    "4. **Average CS Difference**: The average difference in jungle CS between the player and their opponent. A higher difference indicates better farm control.\n"
)

def generate_advice(prompt):
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an expert on League of Legends jungle gameplay."},
                  {"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    return chat_completion

prompt = (
    f"Given the following data for a pro player and a user in League of Legends, "
    f"provide actionable advice to the user on how to improve their gameplay based on the most impactful stats.\n\n"
    f"Definitions:\n"
    f"{key_metrics_info}\n\n"
    f"Pro Player Data:\n"
    f"Dragons Taken Per Game: {pro_data_summary['Dragons Taken Per Game']}\n"
    f"Baron Taken Per Game: {pro_data_summary['Baron Taken Per Game']}\n"
    f"Gank Efficiency Relative to Objectives: {pro_data_summary['Gank Efficiency Relative to Objectives']}\n"
    f"Objective Control Impact: {pro_data_summary['Objective Control Impact']}\n"
    f"Snowball Efficiency: {pro_data_summary['Snowball Efficiency']}\n"
    f"Average CS Difference: {pro_data_summary['Average CS Difference']}\n\n"
    f"User Data:\n"
    f"Dragons Taken Per Game: {user_data_summary['Dragons Taken Per Game']}\n"
    f"Baron Taken Per Game: {user_data_summary['Baron Taken Per Game']}\n"
    f"Gank Efficiency Relative to Objectives: {user_data_summary['Gank Efficiency Relative to Objectives']}\n"
    f"Objective Control Impact: {user_data_summary['Objective Control Impact']}\n"
    f"Snowball Efficiency: {user_data_summary['Snowball Efficiency']}\n"
    f"Average CS Difference: {user_data_summary['Average CS Difference']}\n\n"
    f"Advice:"
)

response = generate_advice(prompt)
'''