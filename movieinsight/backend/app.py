from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)  # Izinkan frontend mengakses API

def get_db_connection():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row  # Biar bisa diakses seperti dictionary
    return conn

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'MovieInsight API is running!',
        'endpoints': {
            '/api/stats': 'Statistik dashboard',
            '/api/search?q=<judul>': 'Pencarian film',
            '/api/movies/<int:page>': 'Semua film (paginated)',
            '/api/movie/<int:id>': 'Detail film',
            '/api/genres': 'Daftar semua genre',
            '/api/filter?genre=<genre>&page=1': 'Filter berdasarkan genre',
            '/api/top10': '10 film rating tertinggi',
            '/api/movies-per-year': 'Data grafik film per tahun',
            '/api/rating-distribution': 'Data sebaran rating film'
        }
    })

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total film
    total = cursor.execute('SELECT COUNT(*) FROM movies').fetchone()[0]
    
    # Rata-rata rating
    avg_rating = cursor.execute('SELECT AVG(vote_average) FROM movies').fetchone()[0]
    
    # Film rating tertinggi
    top_rated = cursor.execute('SELECT title, vote_average, year FROM movies ORDER BY vote_average DESC LIMIT 1').fetchone()
    
    # Film paling populer
    most_popular = cursor.execute('SELECT title, popularity, year FROM movies ORDER BY popularity DESC LIMIT 1').fetchone()
    
    # Total genre unik
    genres_count = cursor.execute('SELECT COUNT(DISTINCT main_genre) FROM movies WHERE main_genre IS NOT NULL AND main_genre != ""').fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_movies': total,
        'avg_rating': round(avg_rating, 2),
        'top_rated': {
            'title': top_rated[0],
            'rating': top_rated[1],
            'year': top_rated[2]
        },
        'most_popular': {
            'title': most_popular[0],
            'popularity': most_popular[1],
            'year': most_popular[2]
        },
        'total_genres': genres_count
    })

@app.route('/api/search')
def search_movies():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cari berdasarkan judul
    cursor.execute('''
        SELECT id, title, year, vote_average, popularity, main_genre, poster_url, overview
        FROM movies 
        WHERE title LIKE ? 
        ORDER BY vote_average DESC
        LIMIT ? OFFSET ?
    ''', (f'%{query}%', per_page, offset))
    
    movies = [dict(row) for row in cursor.fetchall()]
    
    # Total hasil
    total_results = cursor.execute('SELECT COUNT(*) FROM movies WHERE title LIKE ?', (f'%{query}%',)).fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'query': query,
        'total_results': total_results,
        'page': page,
        'per_page': per_page,
        'movies': movies
    })

@app.route('/api/movies/<int:page>')
def get_movies(page=1):
    per_page = 24
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, year, vote_average, popularity, main_genre, poster_url
        FROM movies 
        ORDER BY popularity DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    
    movies = [dict(row) for row in cursor.fetchall()]
    
    # Total film
    total = cursor.execute('SELECT COUNT(*) FROM movies').fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total_movies': total,
        'total_pages': (total + per_page - 1) // per_page,
        'movies': movies
    })

@app.route('/api/movie/<int:id>')
def get_movie_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM movies WHERE id = ?', (id,))
    movie = cursor.fetchone()
    conn.close()
    
    if movie is None:
        return jsonify({'error': 'Film tidak ditemukan'}), 404
    
    return jsonify(dict(movie))

@app.route('/api/genres')
def get_genres():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT main_genre, COUNT(*) as count 
        FROM movies 
        WHERE main_genre IS NOT NULL AND main_genre != ''
        GROUP BY main_genre 
        ORDER BY count DESC
    ''')
    
    genres = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(genres)

@app.route('/api/filter')
def filter_by_genre():
    genre = request.args.get('genre', '')
    page = int(request.args.get('page', 1))
    per_page = 24
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, year, vote_average, popularity, main_genre, poster_url
        FROM movies 
        WHERE main_genre LIKE ?
        ORDER BY vote_average DESC
        LIMIT ? OFFSET ?
    ''', (f'%{genre}%', per_page, offset))
    
    movies = [dict(row) for row in cursor.fetchall()]
    
    total = cursor.execute('SELECT COUNT(*) FROM movies WHERE main_genre LIKE ?', (f'%{genre}%',)).fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'genre': genre,
        'total_results': total,
        'page': page,
        'per_page': per_page,
        'movies': movies
    })

@app.route('/api/top10')
def get_top10():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, year, vote_average, popularity, main_genre, poster_url, overview
        FROM movies 
        ORDER BY vote_average DESC
        LIMIT 10
    ''')
    
    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(movies)

@app.route('/api/movies-per-year')
def movies_per_year():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT year, COUNT(*) as count 
        FROM movies 
        WHERE year IS NOT NULL AND year > 0
        GROUP BY year 
        ORDER BY year
    ''')
    
    data = [{'year': row[0], 'count': row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(data)

@app.route('/api/rating-distribution')
def rating_distribution():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Kelompokkan rating ke dalam interval 1 poin
    cursor.execute('''
        SELECT 
            CASE 
                WHEN vote_average >= 0 AND vote_average < 1 THEN '0-1'
                WHEN vote_average >= 1 AND vote_average < 2 THEN '1-2'
                WHEN vote_average >= 2 AND vote_average < 3 THEN '2-3'
                WHEN vote_average >= 3 AND vote_average < 4 THEN '3-4'
                WHEN vote_average >= 4 AND vote_average < 5 THEN '4-5'
                WHEN vote_average >= 5 AND vote_average < 6 THEN '5-6'
                WHEN vote_average >= 6 AND vote_average < 7 THEN '6-7'
                WHEN vote_average >= 7 AND vote_average < 8 THEN '7-8'
                WHEN vote_average >= 8 AND vote_average < 9 THEN '8-9'
                WHEN vote_average >= 9 AND vote_average <= 10 THEN '9-10'
            END as rating_range,
            COUNT(*) as count
        FROM movies 
        WHERE vote_average IS NOT NULL AND vote_average > 0
        GROUP BY rating_range
        ORDER BY MIN(vote_average)
    ''')
    
    data = [{'range': row[0], 'count': row[1]} for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(data)

@app.route('/api/recommend/<int:movie_id>')
def get_recommendations(movie_id):
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    conn = get_db_connection()
    
    # Ambil data film
    df = pd.read_sql_query("SELECT id, title, main_genre, overview FROM movies", conn)
    conn.close()
    
    # Buat fitur teks (genre + overview)
    df['features'] = df['main_genre'].fillna('') + ' ' + df['overview'].fillna('')
    
    # TF-IDF Vectorizer
    tfidf = TfidfVectorizer(stop_words='english', max_features=5000)
    tfidf_matrix = tfidf.fit_transform(df['features'])
    
    # Hitung cosine similarity
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Cari index film yang dipilih
    idx = df[df['id'] == movie_id].index
    if len(idx) == 0:
        return jsonify({'error': 'Film tidak ditemukan'}), 404
    
    idx = idx[0]
    
    # Ambil skor similarity
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Ambil 10 rekomendasi (skip film itu sendiri)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    
    recommendations = df.iloc[movie_indices][['id', 'title']].to_dict('records')
    
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)