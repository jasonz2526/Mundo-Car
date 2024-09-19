import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.optim.lr_scheduler import ReduceLROnPlateau
from models import JungleNet
import joblib

data = pd.read_csv('pro_final_fr.csv')

data.replace('N/A', 'unknown', inplace=True)

categorical_columns = [
    'Position', 'Lane Gank Position', 'KP Position', 'Opponent Position',
    'Opponent Lane Gank Position', 'Opponent KP Position'
]
data[categorical_columns] = data[categorical_columns].astype(str)

encoder = OneHotEncoder(sparse_output=False)
encoded_cats = encoder.fit_transform(data[categorical_columns])
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

scaler = StandardScaler()
scaled_features = scaler.fit_transform(data.drop(columns=['match_id', 'Time (minutes)', 'Win']))
scaled_df = pd.DataFrame(scaled_features, columns=data.columns.drop(['match_id', 'Time (minutes)', 'Win']))
data = pd.concat([data[['match_id', 'Time (minutes)', 'Win']], scaled_df], axis=1)

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

seq_length = 10
X_sequences, y_sequences = create_sequences(data, seq_length)

X_train_tensor = torch.tensor(X_sequences, dtype=torch.float32)
y_train_tensor = torch.tensor(y_sequences, dtype=torch.float32)
print(f"X_train_tensor shape: {X_train_tensor.shape}")
print(f"y_train_tensor shape: {y_train_tensor.shape}")

class JungleDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

X_train, X_test, y_train, y_test = train_test_split(X_sequences, y_sequences, test_size=0.2, random_state=122)

train_dataset = JungleDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32))
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

test_dataset = JungleDataset(torch.tensor(X_test, dtype=torch.float32), torch.tensor(y_test, dtype=torch.float32))
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

hidden_size = 128
model = JungleNet(input_size=X_train_tensor.shape[2], hidden_size=hidden_size)
criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = ReduceLROnPlateau(optimizer, 'min', patience=5, factor=0.5)

early_stopping_patience = 10
best_val_loss = float('inf')
patience_counter = 0

best_model_path = 'best_model.pth'

def evaluate(model, data_loader, criterion):
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for inputs, labels in data_loader:
            outputs = model(inputs)
            loss = criterion(outputs.squeeze(), labels)
            total_loss += loss.item()
    return total_loss / len(data_loader)

num_epochs = 200
for epoch in range(num_epochs):
    model.train()
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs.squeeze(), labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

    train_loss = evaluate(model, train_loader, criterion)
   
    val_loss = evaluate(model, test_loader, criterion)
    
    scheduler.step(val_loss)
    
    print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}')

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        torch.save(model.state_dict(), best_model_path)
        scaler_filename = 'scaler.pkl'
        encoder_filename = 'encoder.pkl'
        joblib.dump(scaler, scaler_filename)
        joblib.dump(encoder, encoder_filename)
    else:
        patience_counter += 1
        if patience_counter >= early_stopping_patience:
            print('Early stopping triggered')
            break

