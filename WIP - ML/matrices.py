import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import openai
from API_KEY import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY
# Load data
pro_data = pd.read_csv('./WIP - ML/pro_final_fr.csv')
user_data = pd.read_csv('./WIP - ML/ex_final_fr.csv')

# Define action categories
action_columns = [
    'Baron Control', 'Defending Inhibitor', 'Defending Turret', 'Destroying Wards', 
    'Dragon Control', 'Farming', 'Gank Bot', 'Gank Mid', 'Gank Top', 'Grub Control', 
    'Inhibitor Destroy', 'Placing Wards', 'Turret Destroy'
]

# Additional conditions for more detailed actions
def define_action(row):
    # Farm vs gank
    if row['Jungle CS'] > row['Opponent Jungle CS']:
        return 'Farming'
    if row['Lane Gank'] == 1:
        return f'Gank {row["Lane Gank Position"]}'
    
    # Objective control
    if row['Dragons'] > row['Opponent Dragons']:
        return 'Dragon Control'
    if row['Baron'] > row['Opponent Baron']:
        return 'Baron Control'
    if row['Grubs'] > row['Opponent Grubs']:
        return 'Grub Control'

    # Warding
    if row['Wards Placed'] > row['Opponent Wards Placed']:
        return 'Placing Wards'
    if row['Wards Destroyed'] > row['Opponent Wards Destroyed']:
        return 'Destroying Wards'

    # Taking turrets and inhibitors
    if row['Turrets KP'] > 0:
        return f'Turret Destroy {row["Lane Gank Position"]}'
    if row['Inhibitors Taken'] > 0:
        return 'Inhibitor Destroy'

    # Defending from enemy objectives
    if row['Opponent Turrets KP'] > 0:
        return 'Defending Turret'
    if row['Opponent Inhibitors Taken'] > 0:
        return 'Defending Inhibitor'

    # Otherwise, movement and positioning
    return f'Moving {row["Position"]}'

# Apply action definitions
pro_data['action'] = pro_data.apply(define_action, axis=1)
user_data['action'] = user_data.apply(define_action, axis=1)

# Print a sample of actions to verify they are defined correctly
print("Pro Data Actions:")
print(pro_data[['Position', 'Jungle CS', 'Opponent Jungle CS', 'Lane Gank', 'Lane Gank Position', 'Dragons', 'Baron', 'Grubs', 'Wards Placed', 'Wards Destroyed', 'Turrets KP', 'Inhibitors Taken', 'Opponent Turrets KP', 'Opponent Inhibitors Taken', 'action']].head())

# Transition matrix function
def build_transition_matrix(df, position_col, action_col):
    transitions = pd.crosstab(df[position_col], df[action_col].shift(1), rownames=['From'], colnames=['To'])
    return transitions

def generate_advice(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Add position category
pro_data['position_category'] = pro_data['Position'].apply(lambda x: 'Enemy Side' if 'Enemy' in x else 'Own Side')
user_data['position_category'] = user_data['Position'].apply(lambda x: 'Enemy Side' if 'Enemy' in x else 'Own Side')

# Function to analyze each match independently
# Function to analyze each match independently
def analyze_match(match_df):
    # Create transition matrices for the match
    match_transition_matrix = build_transition_matrix(match_df, 'position_category', 'action')
    
    # Define game phases
    def define_game_phase(row):
        if row['Time (minutes)'] <= 14:
            return 'Early'
        elif 14 < row['Time (minutes)'] <= 25:
            return 'Mid'
        else:
            return 'Late'

    # Add game phase to data
    match_df['Game Phase'] = match_df.apply(define_game_phase, axis=1)

    # Ensure all action columns are present
    for col in action_columns:
        if col not in match_df.columns:
            match_df[col] = 0

    # Decision logic for pro gameplay vs user decisions
    def decision_advice(pro_row, user_row):
        prompt = (
            f"Given the following data for a pro player and a user in League of Legends, "
            f"provide advice to the user on how to improve their gameplay. "
            f"Pro Player Data: {pro_row.to_dict()}\n"
            f"User Data: {user_row.to_dict()}\n"
            f"Advice:"
        )
        api_advice = generate_advice(prompt)
        return [api_advice]

    # Apply decision-making model
    def analyze_game(match_df_pro, match_df_user):
        comparison_results = []
        
        for idx, pro_row in match_df_pro.iterrows():
            if idx < len(match_df_user):  # Ensure we are within bounds of user data
                user_row = match_df_user.iloc[idx]
                advice = decision_advice(pro_row, user_row)
                comparison_results.append(advice)
        
        return comparison_results

    # Run analysis for the match
    match_advice = analyze_game(match_df[pro_data['match_id'] == match_df['match_id'].iloc[0]], 
                                match_df[user_data['match_id'] == match_df['match_id'].iloc[0]])

    return match_transition_matrix, match_advice

# Group by match_id and analyze each match
def analyze_all_matches(pro_data, user_data):
    all_advice = []
    all_transition_matrices = []

    for match_id in pro_data['match_id'].unique():
        pro_match_data = pro_data[pro_data['match_id'] == match_id]
        user_match_data = user_data[user_data['match_id'] == match_id]
        
        if not user_match_data.empty:
            transition_matrix, match_advice = analyze_match(pro_match_data)
            all_advice.extend(match_advice)
            all_transition_matrices.append(transition_matrix)
    
    return all_advice, all_transition_matrices


# Run analysis for all matches
comparison_advice, transition_matrices = analyze_all_matches(pro_data, user_data)

# Print a few examples of advice
print("Advice Examples:")
for idx, advice in enumerate(comparison_advice[:5]):  # First 5 comparisons
    print(f"Minute {idx + 1}: {advice}")

# ------------ Visualization ------------
'''
def visualize_comparisons(pro_data, user_data, phase='Early'):
    print(f"Visualizing for phase: {phase}")
    
    pro_phase_data = pro_data[pro_data['Game Phase'] == phase]
    user_phase_data = user_data[user_data['Game Phase'] == phase]
    
    if pro_phase_data.empty and user_phase_data.empty:
        print(f"No data available for the {phase} phase.")
        return
    
    plt.figure(figsize=(14, 8))
    has_data = False
    
    for action in action_columns:
        if action in pro_data.columns and action in user_data.columns:
            if not pro_phase_data.empty:
                sns.lineplot(x='Time (minutes)', y=action, data=pro_phase_data, label=f'Pro {action}')
                has_data = True
            if not user_phase_data.empty:
                sns.lineplot(x='Time (minutes)', y=action, data=user_phase_data, label=f'User {action}')
                has_data = True
    
    if has_data:
        plt.title(f'Pro vs. User Actions Comparison in {phase} Phase')
        plt.xlabel('Time (minutes)')
        plt.ylabel('Action Count')
        plt.legend()
        plt.show()
    else:
        print(f"No data available to plot for the {phase} phase.")

# Function to summarize actions with debug info
def summarize_actions(pro_data, user_data):
    pro_summary = pro_data.groupby('Game Phase')[action_columns].sum().reset_index()
    user_summary = user_data.groupby('Game Phase')[action_columns].sum().reset_index()

    print("Pro Summary:")
    print(pro_summary)
    print("User Summary:")
    print(user_summary)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    phases = ['Early', 'Mid', 'Late']
    
    for i, phase in enumerate(phases):
        pro_phase = pro_summary[pro_summary['Game Phase'] == phase]
        user_phase = user_summary[user_summary['Game Phase'] == phase]
        
        if pro_phase.empty or user_phase.empty:
            print(f"No data available for the {phase} phase.")
            continue
        
        actions = pro_phase[action_columns].values.flatten()
        user_actions = user_phase[action_columns].values.flatten()
        
        axes[i].bar(action_columns, actions, label='Pro', alpha=0.6)
        axes[i].bar(action_columns, user_actions, label='User', alpha=0.6)
        axes[i].set_title(f'Actions in {phase} Phase')
        axes[i].set_xticklabels(action_columns, rotation=90)
        axes[i].legend()
    
    plt.tight_layout()
    plt.show()

# Visualize comparisons for different phases
visualize_comparisons(pro_data, user_data, phase='Early')
visualize_comparisons(pro_data, user_data, phase='Mid')
visualize_comparisons(pro_data, user_data, phase='Late')

# Summarize actions
summarize_actions(pro_data, user_data)
'''
