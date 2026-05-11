const API_BASE = 'http://localhost:5000';

// Page routing
let currentPage = 'home';

// Load page on load
document.addEventListener('DOMContentLoaded', () => {
    loadPage('home');
    
    // Setup navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            loadPage(page);
            
            // Update active class
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
    
    // Setup search
    document.getElementById('searchBtn').addEventListener('click', () => {
        const query = document.getElementById('searchInput').value;
        if (query.trim()) {
            searchMovies(query);
        }
    });
    
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('searchBtn').click();
        }
    });
});

async function loadPage(page) {
    currentPage = page;
    const contentDiv = document.getElementById('content');
    
    contentDiv.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    switch(page) {
        case 'home':
            await loadHomepage();
            break;
        case 'dashboard':
            await loadDashboard();
            break;
        case 'top10':
            await loadTop10();
            break;
        case 'genres':
            await loadGenres();
            break;
    }
}

async function loadHomepage() {
    const contentDiv = document.getElementById('content');
    
    // Fetch stats and popular movies
    try {
        const [statsRes, moviesRes] = await Promise.all([
            fetch(`${API_BASE}/api/stats`),
            fetch(`${API_BASE}/api/movies/1`)
        ]);
        
        const stats = await statsRes.json();
        const movies = await moviesRes.json();
        
        contentDiv.innerHTML = `
            <div class="hero">
                <h1>🎬 MovieInsight</h1>
                <p>Your life in film - Discover, track, and share your movie journey</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>${stats.total_movies.toLocaleString()}</h3>
                    <p>Total Movies</p>
                </div>
                <div class="stat-card">
                    <h3>⭐ ${stats.avg_rating}</h3>
                    <p>Average Rating</p>
                </div>
                <div class="stat-card">
                    <h3>🎭 ${stats.total_genres}</h3>
                    <p>Genres</p>
                </div>
                <div class="stat-card">
                    <h3>🏆 ${stats.top_rated.rating}</h3>
                    <p>Top Rated: ${stats.top_rated.title}</p>
                </div>
            </div>
            
            <h2 class="section-title">🔥 Popular Movies</h2>
            <div class="film-grid" id="popular-grid"></div>
        `;
        
        // Display movies
        const grid = document.getElementById('popular-grid');
        displayMovies(movies.movies, grid);
        
    } catch (error) {
        console.error('Error loading homepage:', error);
        contentDiv.innerHTML = '<div class="error">Failed to load data. Make sure backend is running on port 5000</div>';
    }
}

async function loadDashboard() {
    const contentDiv = document.getElementById('content');
    
    contentDiv.innerHTML = `
        <h1 class="section-title">📊 Movie Analytics Dashboard</h1>
        <div class="stats-grid" id="dashboard-stats"></div>
        <div class="chart-container">
            <h3 style="margin-bottom: 1rem;">📈 Jumlah Film per Tahun</h3>
            <canvas id="yearChart"></canvas>
        </div>
        <div class="chart-container">
            <h3 style="margin-bottom: 1rem;">⭐ Sebaran Rating Film</h3>
            <canvas id="ratingChart"></canvas>
        </div>
    `;
    
    try {
        // Load stats
        const statsRes = await fetch(`${API_BASE}/api/stats`);
        const stats = await statsRes.json();
        
        const statsDiv = document.getElementById('dashboard-stats');
        statsDiv.innerHTML = `
            <div class="stat-card"><h3>${stats.total_movies.toLocaleString()}</h3><p>Total Films</p></div>
            <div class="stat-card"><h3>⭐ ${stats.avg_rating}</h3><p>Average Rating</p></div>
            <div class="stat-card"><h3>🎬 ${stats.total_genres}</h3><p>Genres Available</p></div>
            <div class="stat-card"><h3>🏆 ${stats.top_rated.rating}</h3><p>Top Rated Film</p></div>
        `;
        
        // Load chart data: Film per tahun
        const yearRes = await fetch(`${API_BASE}/api/movies-per-year`);
        const yearData = await yearRes.json();
        
        // Load rating distribution data
        const ratingRes = await fetch(`${API_BASE}/api/rating-distribution`);
        const ratingData = await ratingRes.json();
        
        // Load Chart.js library
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        script.onload = () => {
            // Grafik 1: Film per tahun
            new Chart(document.getElementById('yearChart'), {
                type: 'line',
                data: {
                    labels: yearData.map(d => d.year),
                    datasets: [{
                        label: 'Jumlah Film Rilis per Tahun',
                        data: yearData.map(d => d.count),
                        borderColor: '#e50914',
                        backgroundColor: 'rgba(229, 9, 20, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 0,
                        pointHoverRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { labels: { color: 'white' } },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        x: { 
                            ticks: { color: 'white', maxTicksLimit: 15, rotation: 45 },
                            title: { display: true, text: 'Tahun', color: 'white' }
                        },
                        y: { 
                            ticks: { color: 'white' },
                            title: { display: true, text: 'Jumlah Film', color: 'white' }
                        }
                    }
                }
            });
            
            // Grafik 2: Sebaran Rating (Histogram)
            new Chart(document.getElementById('ratingChart'), {
                type: 'bar',
                data: {
                    labels: ratingData.map(d => d.range),
                    datasets: [{
                        label: 'Jumlah Film',
                        data: ratingData.map(d => d.count),
                        backgroundColor: 'rgba(229, 9, 20, 0.7)',
                        borderColor: '#e50914',
                        borderWidth: 1,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { labels: { color: 'white' } },
                        tooltip: { 
                            callbacks: {
                                label: function(context) {
                                    return `Jumlah film: ${context.raw.toLocaleString()}`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: { 
                            ticks: { color: 'white' },
                            title: { display: true, text: 'Rentang Rating', color: 'white' }
                        },
                        y: { 
                            ticks: { color: 'white' },
                            title: { display: true, text: 'Jumlah Film', color: 'white' }
                        }
                    }
                }
            });
        };
        document.body.appendChild(script);
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        contentDiv.innerHTML += '<div class="error">Failed to load chart data</div>';
    }
}

async function loadTop10() {
    const contentDiv = document.getElementById('content');
    
    contentDiv.innerHTML = `
        <h1 class="section-title">🏆 Top 10 Highest Rated Movies</h1>
        <div class="film-grid" id="top10-grid"></div>
    `;
    
    try {
        const res = await fetch(`${API_BASE}/api/top10`);
        const movies = await res.json();
        
        const grid = document.getElementById('top10-grid');
        displayMovies(movies, grid);
        
    } catch (error) {
        console.error('Error loading top 10:', error);
    }
}

async function loadGenres() {
    const contentDiv = document.getElementById('content');
    
    contentDiv.innerHTML = `
        <h1 class="section-title">🎭 Browse by Genre</h1>
        <div class="stats-grid" id="genres-grid"></div>
        <h2 class="section-title">🎬 Movies in Selected Genre</h2>
        <div class="film-grid" id="genre-movies"></div>
    `;
    
    try {
        const res = await fetch(`${API_BASE}/api/genres`);
        const genres = await res.json();
        
        const genresGrid = document.getElementById('genres-grid');
        genresGrid.innerHTML = genres.map(genre => `
            <div class="stat-card" style="cursor: pointer;" onclick="filterByGenre('${genre.name}')">
                <h3>${genre.name}</h3>
                <p>${genre.count} movies</p>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading genres:', error);
    }
}

async function filterByGenre(genre) {
    const contentDiv = document.getElementById('content');
    contentDiv.scrollIntoView({ behavior: 'smooth' });
    
    try {
        const res = await fetch(`${API_BASE}/api/filter?genre=${encodeURIComponent(genre)}`);
        const data = await res.json();
        
        const grid = document.getElementById('genre-movies');
        if (grid) {
            grid.innerHTML = '';
            displayMovies(data.movies, grid);
        }
        
        // Update section title
        const sectionTitle = document.querySelector('#genres ~ .section-title');
        if (sectionTitle) {
            sectionTitle.innerHTML = `🎬 ${genre} Movies (${data.total_results} films)`;
        }
        
    } catch (error) {
        console.error('Error filtering by genre:', error);
    }
}

async function searchMovies(query) {
    const contentDiv = document.getElementById('content');
    
    contentDiv.innerHTML = `
        <h1 class="section-title">🔍 Search Results for "${query}"</h1>
        <div class="film-grid" id="search-grid"></div>
    `;
    
    try {
        const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        
        const grid = document.getElementById('search-grid');
        if (data.movies.length === 0) {
            grid.innerHTML = '<p style="text-align:center;">No movies found. Try another search term.</p>';
        } else {
            displayMovies(data.movies, grid);
        }
        
    } catch (error) {
        console.error('Error searching:', error);
    }
}

function displayMovies(movies, container) {
    if (!movies || movies.length === 0) {
        container.innerHTML = '<p style="text-align:center;">No movies available</p>';
        return;
    }
    
    container.innerHTML = movies.map(movie => `
        <div class="film-card" onclick="showMovieDetail(${movie.id})">
            <img class="film-poster" src="${movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'}" alt="${movie.title}">
            <div class="film-info">
                <div class="film-title">${escapeHtml(movie.title) || 'Unknown Title'}</div>
                <div>
                    <span class="film-year">${movie.year || 'N/A'}</span>
                    <span class="film-rating">⭐ ${(movie.vote_average || 0).toFixed(1)}</span>
                </div>
                <div style="font-size:0.75rem; color:#e50914; margin-top:0.25rem;">${movie.main_genre || 'Various'}</div>
            </div>
        </div>
    `).join('');
}
// Tampilkan detail film beserta rekomendasi
async function showMovieDetail(movieId) {
    const contentDiv = document.getElementById('content');
    
    contentDiv.innerHTML = `
        <div class="loading"><div class="spinner"></div></div>
    `;
    
    try {
        // Ambil detail film
        const movieRes = await fetch(`${API_BASE}/api/movie/${movieId}`);
        const movie = await movieRes.json();
        
        // Ambil rekomendasi dari backend
        const recRes = await fetch(`${API_BASE}/api/recommend/${movieId}`);
        const recommendations = await recRes.json();
        
        // Tampilkan halaman detail + rekomendasi
        contentDiv.innerHTML = `
            <button onclick="goBack()" class="back-btn"> Back to ${currentPage === 'home' ? 'Home' : currentPage}</button>
            
            <div class="movie-detail">
                <div class="detail-poster">
                    <img src="${movie.poster_url || 'https://via.placeholder.com/300x450?text=No+Poster'}" alt="${movie.title}">
                </div>
                <div class="detail-info">
                    <h1>${escapeHtml(movie.title)}</h1>
                    <div class="detail-meta">
                        <span class="detail-year">📅 ${movie.year || 'N/A'}</span>
                        <span class="detail-rating">⭐ ${(movie.vote_average || 0).toFixed(1)}</span>
                        <span class="detail-language">🌐 ${movie.original_language?.toUpperCase() || 'N/A'}</span>
                    </div>
                    <div class="detail-genre">
                        🎭 ${movie.main_genre || 'Various'}
                    </div>
                    <p class="detail-overview">${escapeHtml(movie.overview) || 'No overview available.'}</p>
                    <div class="detail-stats">
                        <span>🔥 Popularity: ${movie.popularity || 0}</span>
                        <span>👍 Votes: ${(movie.vote_count || 0).toLocaleString()}</span>
                    </div>
                </div>
            </div>
            
            <h2 class="section-title">🎬 You Might Also Like</h2>
            <div class="film-grid" id="recommendations-grid"></div>
        `;
        
        // Tampilkan rekomendasi
        const recGrid = document.getElementById('recommendations-grid');
        if (recommendations && recommendations.length > 0) {
            // Ambil detail lengkap untuk setiap film rekomendasi
            const recDetails = await Promise.all(
                recommendations.map(async (rec) => {
                    try {
                        const res = await fetch(`${API_BASE}/api/movie/${rec.id}`);
                        return res.json();
                    } catch (e) {
                        return null;
                    }
                })
            );
            // Filter yang berhasil diambil
            const validRecs = recDetails.filter(r => r !== null);
            displayMovies(validRecs, recGrid);
        } else {
            recGrid.innerHTML = '<p style="text-align:center; color:rgba(255,255,255,0.6);">No recommendations available for this movie.</p>';
        }
        
        // Scroll ke atas
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error showing movie detail:', error);
        contentDiv.innerHTML = `
            <div class="error">
                <p>Failed to load movie details. Please make sure backend is running.</p>
                <button onclick="loadPage('${currentPage}')" class="back-btn">Try Again</button>
            </div>
        `;
    }
}

// Fungsi untuk kembali ke halaman sebelumnya
function goBack() {
    loadPage(currentPage);
}

// Fungsi untuk menghindari XSS (security)
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Make functions global for onclick
window.filterByGenre = filterByGenre;
window.showMovieDetail = showMovieDetail;