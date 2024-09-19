import pandas as pd
import torch
import joblib
from models import JungleNet
from util import preprocess_data, create_sequences
import numpy as np

scaler = joblib.load('scaler.pkl')
encoder = joblib.load('encoder.pkl')

model = JungleNet(input_size=103, hidden_size=128)
model.load_state_dict(torch.load('best_model.pth', weights_only=True))
model.eval()

user_data = pd.read_csv('ex_final_fr.csv')
user_data, _, _ = preprocess_data(user_data, encoder=encoder, scaler=scaler, training=False)

seq_length = 10
preprocessed_data = torch.tensor(create_sequences(user_data, seq_length)[0], dtype=torch.float32)

with torch.no_grad():
    baseline_predictions = model(preprocessed_data).squeeze()
    baseline_probabilities = torch.sigmoid(baseline_predictions).numpy()

def mean_squared_difference(original, perturbed):
    return np.mean((original - perturbed) ** 2)

feature_importance = {}
for i in range(user_data.shape[1]):  
    if i >= preprocessed_data.shape[2]:  
        continue

    perturbed_data = preprocessed_data.clone()  
    perturbed_data[:, :, i] = torch.tensor(np.random.permutation(perturbed_data[:, :, i].numpy()))  

    with torch.no_grad():
        perturbed_predictions = model(perturbed_data).squeeze()
        perturbed_probabilities = torch.sigmoid(perturbed_predictions).numpy()

    importance_score = mean_squared_difference(baseline_probabilities, perturbed_probabilities)
    feature_importance[user_data.columns[i]] = importance_score

sorted_importance = sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)

print("Predicted probabilities of favorable outcomes:", baseline_probabilities)
print("\nFeature Importance (sorted by impact):")
for feature, importance in sorted_importance:
    print(f"{feature}: {importance}")
