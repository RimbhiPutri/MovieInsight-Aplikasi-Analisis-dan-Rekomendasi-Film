import sys
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

DATA_PATH = os.path.join(PARENT_DIR, 'data', 'movies_cleaned.csv')
MODELS_DIR = os.path.join(PARENT_DIR, 'models')
FRONTEND_DIR = os.path.join(PARENT_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR, template_folder=FRONTEND_DIR)
CORS(app)

df = pd.read_csv(DATA_PATH)
rf_model = joblib.load(os.path.join(MODELS_DIR, 'rf_regressor.pkl'))
rf_scaler = joblib.load(os.path.join(MODELS_DIR, 'rf_scaler.pkl'))

knn_recommender = joblib.load(os.path.join(MODELS_DIR, 'knn_recommender.pkl'))
scaler_recommend = joblib.load(os.path.join(MODELS_DIR, 'scaler_recommend.pkl'))
feature_cols_recommend = joblib.load(os.path.join(MODELS_DIR, 'feature_cols_recommend.pkl'))

with open(os.path.join(MODELS_DIR, 'genre_list.txt'), 'r') as f:
    genres = [line.strip() for line in f.readlines()]

def get_ml_recommendations(genres_selected, year, popularity, vote_count, top_n=5):

    mask = pd.Series([False] * len(df))
    for genre in genres_selected:
        col_name = f'genre_{genre}'
        if col_name in df.columns:
            mask = mask | (df[col_name] == 1)
    
    if mask.sum() == 0:
        return []
    
    input_vector = np.zeros(len(feature_cols_recommend))
    input_vector[0] = popularity   
    input_vector[1] = vote_count   
    input_vector[2] = year         
    input_vector[3] = df['Vote_Average'].median()  

    for genre in genres_selected:
        col_name = f'genre_{genre}'
        if col_name in feature_cols_recommend:
            idx = feature_cols_recommend.index(col_name)
            input_vector[idx] = 1

    numeric_part = input_vector[:4].copy()
    scaled_numeric = scaler_recommend.transform([numeric_part])[0]
    input_vector[:4] = scaled_numeric

    distances, indices = knn_recommender.kneighbors([input_vector], n_neighbors=top_n * 3)

    recommendations = df.iloc[indices[0]].copy()
    recommendations['distance'] = distances[0]
    recommendations['similarity'] = 1 / (1 + recommendations['distance'])

    recommendations = recommendations[recommendations['Vote_Average'] >= 5]

    recommendations = recommendations.sort_values('similarity', ascending=False).head(top_n)

    result = []
    for _, row in recommendations.iterrows():
        poster = row.get('Poster_Url', '')
        if pd.isna(poster) or poster == '':
            poster = 'https://via.placeholder.com/300x450?text=No+Poster'
        
        result.append({
            'title': row['Title'],
            'year': int(row['Year']),
            'rating': float(row['Vote_Average']),
            'popularity': float(row['Popularity']),
            'vote_count': int(row['Vote_Count']),
            'genre': row['Genre'],
            'poster_url': poster,
            'similarity_score': round(float(row['similarity']), 3)
        })
    
    return result

@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'rf_model_loaded': True,
        'knn_model_loaded': True,
        'total_movies': len(df),
        'total_genres': len(genres),
        'recommendation_method': 'KNN with Cosine Similarity'
    })

@app.route('/api/genres', methods=['GET'])
def get_genres():
    return jsonify({'genres': genres})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify({
        'total_movies': len(df),
        'avg_rating': round(df['Vote_Average'].mean(), 2),
        'max_rating': round(df['Vote_Average'].max(), 2),
        'min_rating': round(df['Vote_Average'].min(), 2),
        'year_min': int(df['Year'].min()),
        'year_max': int(df['Year'].max()),
        'avg_popularity': round(df['Popularity'].mean(), 2),
        'avg_vote_count': int(df['Vote_Count'].mean())
    })

@app.route('/api/top10', methods=['GET'])
def get_top10():
    top10 = df.nlargest(10, 'Vote_Average')
    result = []
    for _, row in top10.iterrows():
        poster = row.get('Poster_Url', '')
        if pd.isna(poster) or poster == '':
            poster = 'https://via.placeholder.com/300x450?text=No+Poster'
        result.append({
            'Title': row['Title'],
            'Year': int(row['Year']),
            'Vote_Average': float(row['Vote_Average']),
            'Vote_Count': int(row['Vote_Count']),
            'Genre': row['Genre'],
            'Poster_Url': poster
        })
    return jsonify(result)

@app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    rating_bins = pd.cut(df['Vote_Average'], bins=range(0, 11), right=False)
    rating_counts = rating_bins.value_counts().sort_index()
    year_counts = df.groupby('Year').size()
    years = year_counts.index.tolist()
    counts = year_counts.values.tolist()
    
    return jsonify({
        'rating_distribution': {
            'bins': [f"{i}-{i+1}" for i in range(10)],
            'counts': rating_counts.values.tolist()
        },
        'movies_per_year': {
            'years': years[-30:],
            'counts': counts[-30:]
        }
    })

@app.route('/api/predict', methods=['POST'])
def predict_rating():
    data = request.get_json()
    
    genres_selected = data.get('genres', [])
    popularity = float(data.get('popularity', 50))
    year = int(data.get('year', 2024))
    vote_count = float(data.get('vote_count', df['Vote_Count'].median()))
    
    if not genres_selected:
        return jsonify({'error': 'Pilih minimal 1 genre'}), 400
    
    # Prediksi dengan Random Forest
    feature_cols_rf = ['Popularity', 'Vote_Count', 'Year'] + [f'genre_{g}' for g in genres]
    features = np.zeros(len(feature_cols_rf))
    features[0] = popularity
    features[1] = vote_count
    features[2] = year
    
    for genre in genres_selected:
        col_name = f'genre_{genre}'
        if col_name in feature_cols_rf:
            idx = feature_cols_rf.index(col_name)
            features[idx] = 1
    
    features_scaled = rf_scaler.transform(features.reshape(1, -1))
    prediction = rf_model.predict(features_scaled)[0]
    prediction = max(0, min(10, prediction))

    recommendations = get_ml_recommendations(genres_selected, year, popularity, vote_count, top_n=6)
    
    return jsonify({
        'predicted_rating': round(prediction, 2),
        'input': {
            'genres': genres_selected,
            'popularity': round(popularity, 2),
            'vote_count': int(vote_count),
            'year': year
        },
        'recommendations': recommendations,
        'recommendation_method': 'K-Nearest Neighbors (Cosine Similarity)'
    })

@app.route('/api/recommend-by-genre/<genre_name>', methods=['GET'])
def recommend_by_genre(genre_name):
    col_name = f'genre_{genre_name}'
    if col_name not in df.columns:
        return jsonify({'error': 'Genre tidak ditemukan', 'recommendations': []})
    
    recommendations = df[df[col_name] == 1].nlargest(5, 'Vote_Average')
    result = []
    for _, row in recommendations.iterrows():
        poster = row.get('Poster_Url', '')
        if pd.isna(poster) or poster == '':
            poster = 'https://via.placeholder.com/300x450?text=No+Poster'
        result.append({
            'title': row['Title'],
            'year': int(row['Year']),
            'rating': float(row['Vote_Average']),
            'vote_count': int(row['Vote_Count']),
            'genre': row['Genre'],
            'poster_url': poster
        })
    return jsonify({'genre': genre_name, 'recommendations': result})

if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0', port=5000)