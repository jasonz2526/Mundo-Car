import pandas as pd
import openai
from openai import OpenAI
import os
from API_KEY import OPENAI_API_KEY

client = OpenAI(
    api_key= OPENAI_API_KEY
)

pro_data = pd.read_csv('./WIP - ML/pro_final_fr.csv')
user_data = pd.read_csv('./WIP - ML/ex_final_fr.csv')

print("Pro Data Sample:")
print(pro_data.head())
print("User Data Sample:")
print(user_data.head())

action_columns = [
    'Baron Control', 'Defending Inhibitor', 'Defending Turret', 'Destroying Wards', 
    'Dragon Control', 'Farming', 'Gank Bot', 'Gank Mid', 'Gank Top', 'Grub Control', 
    'Inhibitor Destroy', 'Placing Wards', 'Turret Destroy'
]

def define_action(row):
    if row['Jungle CS'] > row['Opponent Jungle CS']:
        return 'Farming'
    if row['Lane Gank'] == 1:
        return f'Gank {row["Lane Gank Position"]}'
    if row['Dragons'] > row['Opponent Dragons']:
        return 'Dragon Control'
    if row['Baron'] > row['Opponent Baron']:
        return 'Baron Control'
    if row['Grubs'] > row['Opponent Grubs']:
        return 'Grub Control'
    if row['Wards Placed'] > row['Opponent Wards Placed']:
        return 'Placing Wards'
    if row['Wards Destroyed'] > row['Opponent Wards Destroyed']:
        return 'Destroying Wards'
    if row['Turrets KP'] > 0:
        return f'Turret Destroy {row["Lane Gank Position"]}'
    if row['Inhibitors Taken'] > 0:
        return 'Inhibitor Destroy'
    if row['Opponent Turrets KP'] > 0:
        return 'Defending Turret'
    if row['Opponent Inhibitors Taken'] > 0:
        return 'Defending Inhibitor'
    return f'Moving {row["Position"]}'

def generate_advice(prompt):
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an expert on League of Legends jungle gameplay."},
                  {"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150
    )
    return chat_completion

pro_data['action'] = pro_data.apply(define_action, axis=1)
user_data['action'] = user_data.apply(define_action, axis=1)

print("Pro Data Actions:")
print(pro_data[['Position', 'Jungle CS', 'Opponent Jungle CS', 'Lane Gank', 'Lane Gank Position', 'Dragons', 'Baron', 'Grubs', 'Wards Placed', 'Wards Destroyed', 'Turrets KP', 'Inhibitors Taken', 'Opponent Turrets KP', 'Opponent Inhibitors Taken', 'action']].head())

pro_sample = pro_data.iloc[0]
user_sample = user_data.iloc[0]

prompt = (
    f"Given the following data for a pro player and a user in League of Legends, "
    f"provide advice to the user on how to improve their gameplay.\n\n"
    f"Pro Player Data: {pro_sample.to_dict()}\n"
    f"User Data: {user_sample.to_dict()}\n"
    f"Advice:"
)

advice = generate_advice(prompt)
print("Generated Advice:")
print(advice)
