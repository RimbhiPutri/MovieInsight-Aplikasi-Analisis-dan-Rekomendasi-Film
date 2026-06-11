import pandas as pd
import numpy as np
import joblib
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'movies_cleaned.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
GENRE_PATH = os.path.join(MODELS_DIR, 'genre_list.txt')

# Load data
df = pd.read_csv(DATA_PATH)

# Load genre list
with open(GENRE_PATH, 'r') as f:
    genres = [line.strip() for line in f.readlines()]

# membuat feature matrix untuk rekomendasi

numeric_features = ['Popularity', 'Vote_Count', 'Year', 'Vote_Average']
genre_features = [f'genre_{g}' for g in genres]
feature_cols = numeric_features + genre_features

# Simpan feature columns untuk digunakan di app.py
joblib.dump(feature_cols, os.path.join(MODELS_DIR, 'feature_cols_recommend.pkl'))

# Scale numeric features
scaler = StandardScaler()
df_scaled = df.copy()
df_scaled[numeric_features] = scaler.fit_transform(df[numeric_features])

# Buat feature matrix
feature_matrix = df_scaled[feature_cols].values

#training KNN models

# Model 1: Cosine Similarity (recommended untuk high-dimensional data)
knn_cosine = NearestNeighbors(
    n_neighbors=15,
    metric='cosine',
    algorithm='brute',
    n_jobs=-1
)
knn_cosine.fit(feature_matrix)

# Model 2: Euclidean Distance (alternative)
knn_euclidean = NearestNeighbors(
    n_neighbors=15,
    metric='euclidean',
    algorithm='auto',
    n_jobs=-1
)
knn_euclidean.fit(feature_matrix)

#save model
joblib.dump(knn_cosine, os.path.join(MODELS_DIR, 'knn_recommender.pkl'))
joblib.dump(knn_euclidean, os.path.join(MODELS_DIR, 'knn_euclidean.pkl'))
joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler_recommend.pkl'))

print(f"   - {os.path.join(MODELS_DIR, 'knn_recommender.pkl')}")
print(f"   - {os.path.join(MODELS_DIR, 'knn_euclidean.pkl')}")
print(f"   - {os.path.join(MODELS_DIR, 'scaler_recommend.pkl')}")
print(f"   - {os.path.join(MODELS_DIR, 'feature_cols_recommend.pkl')}")
