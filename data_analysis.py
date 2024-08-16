import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

df_normal = pd.read_csv("./match_info_csvs/kitkat_miffy_Kai'Sa_match_info.csv")
df_pro = pd.read_csv("./pro_match_info_csvs/feedmeiron_0696_Kai'Sa_match_info.csv")

df_normal = df_normal.drop(df_normal.columns[0], axis=1).drop(columns=['match_id'])
df_pro = df_pro.drop(df_pro.columns[0], axis=1).drop(columns=['match_id'])

df_combined = pd.concat([df_normal, df_pro], ignore_index=True)
df_combined = df_combined.dropna()

features = df_combined.drop('win', axis=1)
target = df_combined['win']

X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

rf = RandomForestClassifier(n_estimators=100, random_state=25)

rf.fit(X_train, y_train)

feature_importances = rf.feature_importances_
importance_df = pd.DataFrame({
    'Feature': features.columns,
    'Importance': feature_importances
})

importance_df = importance_df.sort_values(by='Importance', ascending=False)

print(importance_df)

rf_normal = RandomForestClassifier(n_estimators=100, random_state=42)
rf_normal.fit(df_normal.drop('win', axis=1), df_normal['win'])

rf_pro = RandomForestClassifier(n_estimators=100, random_state=42)
rf_pro.fit(df_pro.drop('win', axis=1), df_pro['win'])

importance_normal = rf_normal.feature_importances_
importance_pro = rf_pro.feature_importances_

importance_df_normal = pd.DataFrame({
    'Feature': df_normal.columns.drop('win'),
    'Importance_Normal': importance_normal
})

importance_df_pro = pd.DataFrame({
    'Feature': df_pro.columns.drop('win'),
    'Importance_Pro': importance_pro
})

importance_comparison = pd.merge(importance_df_normal, importance_df_pro, on='Feature')

print(importance_comparison)
