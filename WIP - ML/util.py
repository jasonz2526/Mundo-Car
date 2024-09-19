import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import torch
import numpy as np

categorical_columns = [
    'Position', 'Lane Gank Position', 'KP Position', 'Opponent Position',
    'Opponent Lane Gank Position', 'Opponent KP Position'
]

def preprocess_data(data, encoder=None, scaler=None, training=True):
    data[categorical_columns] = data[categorical_columns].astype(str)

    if encoder is None and training:
        encoder = OneHotEncoder(sparse_output=False)
        encoded_cats = encoder.fit_transform(data[categorical_columns])
    else:
        encoded_cats = encoder.transform(data[categorical_columns])

    encoded_df = pd.DataFrame(encoded_cats, columns=encoder.get_feature_names_out(categorical_columns))
    data = pd.concat([data.drop(columns=categorical_columns), encoded_df], axis=1)

    lagged_features = ['Gold', 'XP', 'Jungle CS']
    for feature in lagged_features:
        for lag in range(1, 4):
            data[f'{feature}_lag_{lag}'] = data[feature].shift(lag)

    relative_features = ['Gold', 'XP', 'Jungle CS', 'Wards Placed', 'Wards Destroyed']
    for feature in relative_features:
        data[f'Relative_{feature}'] = data[feature] - data[f'Opponent {feature}']

    data.fillna(0, inplace=True)

    if scaler is None and training:
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(data.drop(columns=['match_id', 'Time (minutes)', 'Win']))
    else:
        scaled_features = scaler.transform(data.drop(columns=['match_id', 'Time (minutes)', 'Win']))

    scaled_df = pd.DataFrame(scaled_features, columns=data.columns.drop(['match_id', 'Time (minutes)', 'Win']))
    data = pd.concat([data[['match_id', 'Time (minutes)', 'Win']], scaled_df], axis=1)

    return data, encoder, scaler

def create_sequences(data, seq_length):
    sequences = []
    labels = []
    for match_id in data['match_id'].unique():
        match_data = data[data['match_id'] == match_id]
        num_rows = len(match_data)
        for i in range(num_rows - seq_length):
            seq = match_data.iloc[i:i+seq_length].drop(columns=['match_id', 'Win']).values
            label = match_data.iloc[i+seq_length]['Win']
            sequences.append(seq)
            labels.append(label)
    return np.array(sequences), np.array(labels)
