from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)
CORS(app)

df = pd.read_csv(r'C:\Users\Hp\Documents\coolyeah\sems 4\PASD\tubes2\data\movies_cleaned.csv')
rf_model = joblib.load(r'C:\Users\Hp\Documents\coolyeah\sems 4\PASD\tubes2\models\rf_regressor.pkl')
rf_scaler = joblib.load(r'C:\Users\Hp\Documents\coolyeah\sems 4\PASD\tubes2\models\rf_scaler.pkl')

with open(r'C:\Users\Hp\Documents\coolyeah\sems 4\PASD\tubes2\models\genre_list.txt', 'r') as f:
    genres = [line.strip() for line in f.readlines()]

numeric_features = ['Popularity', 'Vote_Count', 'Year']

genre_features = [f'genre_{g}' for g in genres]

feature_cols = numeric_features + genre_features
def get_similar_movies(genres_selected, year, popularity, vote_count, top_n=5):
    mask = pd.Series([False] * len(df))
    for genre in genres_selected:
        col_name = f'genre_{genre}'
        if col_name in df.columns:
            mask = mask | (df[col_name] == 1)

    filtered = df[mask].copy()
    
    if len(filtered) == 0:
        return []
    
    filtered['year_sim'] = 1 / (1 + abs(filtered['Year'] - year))
    filtered['pop_sim'] = 1 / (1 + abs(filtered['Popularity'] - popularity))
    filtered['vote_sim'] = 1 / (1 + abs(filtered['Vote_Count'] - vote_count))
    filtered['rating_score'] = filtered['Vote_Average'] / 10
 
    filtered['similarity'] = (filtered['year_sim'] * 0.25 + 
                              filtered['pop_sim'] * 0.20 + 
                              filtered['vote_sim'] * 0.15 + 
                              filtered['rating_score'] * 0.40)
    
    recommendations = filtered.nlargest(top_n * 2, 'similarity')
    recommendations = recommendations[recommendations['Vote_Average'] >= 5].head(top_n)

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
            'poster_url': poster
        })
    
    return result

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': True,
        'total_features': len(feature_cols),
        'total_genres': len(genres)
    })

@app.route('/api/feature-info', methods=['GET'])
def get_feature_info():
    return jsonify({
        'numeric_features': numeric_features,
        'total_features': len(feature_cols),
        'genres_count': len(genres),
        'genres': genres
    })

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

@app.route('/api/search', methods=['GET'])
def search_movies():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    results = df[df['Title'].str.contains(query, case=False, na=False)]
    results = results.head(30)
    
    result = []
    for _, row in results.iterrows():
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

@app.route('/api/genre/<genre_name>', methods=['GET'])
def filter_by_genre(genre_name):
    col_name = f'genre_{genre_name}'
    
    if col_name not in df.columns:
        return jsonify([])
    
    filtered = df[df[col_name] == 1]
    filtered = filtered.head(50)
    
    result = []
    for _, row in filtered.iterrows():
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

@app.route('/api/genres', methods=['GET'])
def get_genres():
    return jsonify({'genres': genres})

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
    
    return jsonify({
        'genre': genre_name,
        'recommendations': result
    })

@app.route('/api/predict', methods=['POST'])
def predict_rating():
    data = request.get_json()
   
    genres_selected = data.get('genres', [])
    popularity = float(data.get('popularity', 50))
    year = int(data.get('year', 2024))

    vote_count = data.get('vote_count', None)
    if vote_count is None:
        vote_count = float(df['Vote_Count'].median())
    else:
        vote_count = float(vote_count)

    if not genres_selected:
        return jsonify({'error': 'Pilih minimal 1 genre'}), 400
    
    if popularity < 0 or popularity > 1000:
        return jsonify({'error': 'Popularitas harus antara 0-1000'}), 400
    
    if year < 1900 or year > 2030:
        return jsonify({'error': 'Tahun harus antara 1900-2030'}), 400

    features = np.zeros(len(feature_cols))
    features[0] = popularity      
    features[1] = vote_count      
    features[2] = year           

    for genre in genres_selected:
        col_name = f'genre_{genre}'
        if col_name in genre_features:
            idx = feature_cols.index(col_name)
            features[idx] = 1
  
    features_scaled = rf_scaler.transform(features.reshape(1, -1))
  
    prediction = rf_model.predict(features_scaled)[0]
    prediction = max(0, min(10, prediction))
   
    similar_movies = get_similar_movies(genres_selected, year, popularity, vote_count, top_n=6)

    return jsonify({
        'predicted_rating': round(prediction, 2),
        'input': {
            'genres': genres_selected,
            'popularity': round(popularity, 2),
            'vote_count': int(vote_count),
            'year': year
        },
        'similar_movies': similar_movies
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint tidak ditemukan'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Terjadi kesalahan internal server'}), 500
if __name__ == '__main__':    
    app.run(debug=True, host='0.0.0.0', port=5000)
