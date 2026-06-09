const API_URL = 'http://localhost:5000/api';

let ratingChart, yearChart;

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadTop10();
    loadGenres();
    loadChartData();
    loadRecommendGenres();
    loadYears();
    
    const titleBtn = document.querySelector('.search-type-btn[data-type="title"]');
    const genreBtn = document.querySelector('.search-type-btn[data-type="genre"]');
    const titleBox = document.getElementById('search-title-box');
    const genreBox = document.getElementById('search-genre-box');
    
    if (titleBtn && genreBtn) {
        titleBtn.addEventListener('click', () => {
            titleBtn.classList.add('active');
            genreBtn.classList.remove('active');
            titleBox.style.display = 'flex';
            genreBox.style.display = 'none';
            document.getElementById('search-results').innerHTML = '';
        });
        
        genreBtn.addEventListener('click', () => {
            genreBtn.classList.add('active');
            titleBtn.classList.remove('active');
            titleBox.style.display = 'none';
            genreBox.style.display = 'flex';
            document.getElementById('search-results').innerHTML = '';
            loadGenreSelect();
        });
    }
    
    const slider = document.getElementById('popularity');
    const popValue = document.getElementById('pop-value');
    if (slider && popValue) {
        slider.addEventListener('input', (e) => {
            popValue.textContent = e.target.value;
        });
    }
    
    const voteSlider = document.getElementById('vote_count');
    const voteValue = document.getElementById('vote-value');
    if (voteSlider && voteValue) {
        voteSlider.addEventListener('input', (e) => {
            voteValue.textContent = parseInt(e.target.value).toLocaleString();
        });
    }
    
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchMovie();
        });
    }
});

async function loadYears() {
    try {
        const res = await fetch(`${API_URL}/stats`);
        const data = await res.json();
        const yearSelect = document.getElementById('year');
        if (yearSelect) {
            yearSelect.innerHTML = '';
            const startYear = Math.max(data.year_min, data.year_max - 30);
            for (let year = data.year_max; year >= startYear; year--) {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                if (year === 2024) option.selected = true;
                yearSelect.appendChild(option);
            }
        }
    } catch (error) {
        console.error('Error loading years:', error);
        const yearSelect = document.getElementById('year');
        if (yearSelect) {
            yearSelect.innerHTML = '';
            for (let year = 2024; year >= 1990; year--) {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                if (year === 2024) option.selected = true;
                yearSelect.appendChild(option);
            }
        }
    }
}

async function loadStats() {
    try {
        const res = await fetch(`${API_URL}/stats`);
        const data = await res.json();
        document.getElementById('total-movies').textContent = data.total_movies.toLocaleString();
        document.getElementById('avg-rating').textContent = data.avg_rating + ' / 10';
        document.getElementById('year-range').textContent = `${data.year_min} - ${data.year_max}`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadTop10() {
    try {
        const res = await fetch(`${API_URL}/top10`);
        const data = await res.json();
        const container = document.getElementById('top10-list');
        container.innerHTML = '';
        data.forEach((movie, i) => {
            const card = document.createElement('div');
            card.className = 'movie-poster-card';
            card.innerHTML = `
                <div class="poster-container">
                    <img class="movie-poster" src="${movie.Poster_Url}" alt="${movie.Title}" onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
                    <div class="poster-overlay">
                        <span class="movie-rating-badge">⭐ ${movie.Vote_Average.toFixed(1)}</span>
                    </div>
                </div>
                <div class="movie-info-poster">
                    <div class="movie-title-poster" title="${movie.Title}">${movie.Title}</div>
                    <div class="movie-year-poster">${movie.Year} | #${i+1}</div>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading top10:', error);
    }
}

async function loadChartData() {
    try {
        const res = await fetch(`${API_URL}/chart-data`);
        const data = await res.json();
        
        const ctx1 = document.getElementById('ratingChart').getContext('2d');
        if (ratingChart) ratingChart.destroy();
        ratingChart = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: data.rating_distribution.bins,
                datasets: [{
                    label: 'Jumlah Film',
                    data: data.rating_distribution.counts,
                    backgroundColor: '#e85d04',
                    borderRadius: 4,
                    barPercentage: 0.7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { 
                    legend: { 
                        labels: { color: '#d4c9b8', font: { size: 11 } } 
                    } 
                },
                scales: { 
                    y: { ticks: { color: '#8a817c' }, grid: { color: '#2a2a2a' } }, 
                    x: { ticks: { color: '#8a817c', font: { size: 10 } }, grid: { display: false } } 
                }
            }
        });
        
        const ctx2 = document.getElementById('yearChart').getContext('2d');
        if (yearChart) yearChart.destroy();
        yearChart = new Chart(ctx2, {
            type: 'line',
            data: {
                labels: data.movies_per_year.years,
                datasets: [{
                    label: 'Jumlah Film',
                    data: data.movies_per_year.counts,
                    borderColor: '#ffb703',
                    backgroundColor: 'rgba(255, 183, 3, 0.05)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 1,
                    pointHoverRadius: 4,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { 
                    legend: { 
                        labels: { color: '#d4c9b8', font: { size: 11 } } 
                    } 
                },
                scales: { 
                    y: { ticks: { color: '#8a817c' }, grid: { color: '#2a2a2a' } }, 
                    x: { ticks: { color: '#8a817c', font: { size: 10, rotation: 45 } }, grid: { display: false } } 
                }
            }
        });
    } catch (error) {
        console.error('Error loading chart:', error);
    }
}

async function predictRating() {
    const selectedGenres = Array.from(document.querySelectorAll('input[name="genre"]:checked'))
        .map(cb => cb.value);
    const popularity = document.getElementById('popularity').value;
    const year = document.getElementById('year').value;
    const voteCount = document.getElementById('vote_count').value;  
    
    if (selectedGenres.length === 0) {
        alert('Pilih minimal 1 genre!');
        return;
    }
    
    const resultDiv = document.getElementById('prediction-result');
    resultDiv.innerHTML = '<span class="loading-text">memproses...</span>';
    
    try {
        const res = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                genres: selectedGenres, 
                popularity: parseInt(popularity),
                vote_count: parseInt(voteCount),  
                year: parseInt(year) 
            })
        });
        
        const data = await res.json();
        
        if (data.error) {
            resultDiv.innerHTML = `<span class="error-text">${data.error}</span>`;
            return;
        }
        
        const rating = data.predicted_rating;
        const fullStars = Math.floor(rating);
        let starsHtml = '★'.repeat(fullStars) + '☆'.repeat(10 - fullStars);
        
        let similarMoviesHtml = '';
        if (data.similar_movies && data.similar_movies.length > 0) {
            similarMoviesHtml = `
                <div style="margin-top: 1.5rem; text-align: left; border-top: 1px solid var(--border-subtle); padding-top: 1rem;">
                    <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: var(--accent-secondary); margin-bottom: 0.75rem;">
                        🎬 film rekomendasi berdasarkan prediksi
                    </div>
                    <div class="similar-movies-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 0.75rem;">
                        ${data.similar_movies.map(movie => `
                            <div class="similar-movie-card" style="background: var(--bg-elevated); border-radius: 8px; overflow: hidden; transition: var(--transition);">
                                <div style="aspect-ratio: 2/3; position: relative;">
                                    <img src="${movie.poster_url}" alt="${movie.title}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
                                    <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(to top, rgba(0,0,0,0.8), transparent); padding: 0.3rem;">
                                        <span style="background: rgba(0,0,0,0.6); padding: 0.1rem 0.3rem; border-radius: 4px; font-size: 0.6rem;">⭐ ${movie.rating.toFixed(1)}</span>
                                    </div>
                                </div>
                                <div style="padding: 0.4rem;">
                                    <div style="font-size: 0.7rem; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${movie.title}">${movie.title}</div>
                                    <div style="font-size: 0.6rem; color: var(--text-muted);">${movie.year} | ${movie.vote_count?.toLocaleString() || '?'} votes</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            similarMoviesHtml = `
                <div style="margin-top: 1rem; font-size: 0.7rem; color: var(--text-muted);">
                    ℹ️ Tidak ditemukan film dengan genre yang sama.
                </div>
            `;
        }
        
        resultDiv.innerHTML = `
            <div class="prediction-value">${starsHtml}</div>
            <div class="prediction-number">${rating} / 10</div>
            <div class="prediction-detail">${selectedGenres.join(', ')} · pop: ${popularity} · vote: ${parseInt(voteCount).toLocaleString()} · thn: ${year}</div>
            ${similarMoviesHtml}
        `;
        
    } catch (error) {
        console.error('Prediction error:', error);
        resultDiv.innerHTML = '<span class="error-text">gagal memprediksi</span>';
    }
}

async function loadGenres() {
    try {
        const res = await fetch(`${API_URL}/genres`);
        const data = await res.json();
        const checkContainer = document.getElementById('genre-checkboxes');
        if (checkContainer) {
            checkContainer.innerHTML = '';
            data.genres.slice(0, 15).forEach(genre => {
                const label = document.createElement('label');
                label.innerHTML = `<input type="checkbox" name="genre" value="${genre}"> <span>${genre}</span>`;
                checkContainer.appendChild(label);
            });
        }
    } catch (error) {
        console.error('Error loading genres:', error);
    }
}

async function loadRecommendGenres() {
    try {
        const res = await fetch(`${API_URL}/genres`);
        const data = await res.json();
        const container = document.getElementById('recommend-genre-buttons');
        if (!container) return;
        container.innerHTML = '';
        const topGenres = ['Action', 'Drama', 'Comedy', 'Horror', 'Sci-Fi', 'Romance', 'Thriller', 'Adventure'];
        topGenres.forEach(genre => {
            if (data.genres.includes(genre)) {
                const btn = document.createElement('button');
                btn.className = 'genre-btn';
                btn.textContent = genre;
                btn.onclick = () => getRecommendationsByGenre(genre);
                container.appendChild(btn);
            }
        });
    } catch (error) {
        console.error('Error loading recommend genres:', error);
    }
}

async function getRecommendationsByGenre(genre) {
    const resultsDiv = document.getElementById('recommend-results');
    resultsDiv.innerHTML = '<div class="loading-text">mencari rekomendasi...</div>';
    try {
        const res = await fetch(`${API_URL}/recommend-by-genre/${encodeURIComponent(genre)}`);
        const data = await res.json();
        if (!data.recommendations || data.recommendations.length === 0) {
            resultsDiv.innerHTML = `<div class="error-text">tidak ada rekomendasi untuk genre "${genre}"</div>`;
            return;
        }
        resultsDiv.innerHTML = `<div class="recommend-header">🎯 top 5 film ${genre} rating tertinggi</div><div class="recommend-grid"></div>`;
        const grid = resultsDiv.querySelector('.recommend-grid');
        data.recommendations.forEach((movie, index) => {
            const card = document.createElement('div');
            card.className = 'recommend-card-poster';
            card.style.position = 'relative';
            card.innerHTML = `
                <div class="recommend-rank-badge">#${index + 1}</div>
                <div class="poster-container" style="aspect-ratio: 2/3;">
                    <img class="movie-poster" src="${movie.poster_url}" alt="${movie.title}" onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
                    <div class="poster-overlay">
                        <span class="movie-rating-badge">⭐ ${movie.rating.toFixed(1)}</span>
                    </div>
                </div>
                <div class="movie-info-poster">
                    <div class="movie-title-poster" title="${movie.title}">${movie.title}</div>
                    <div class="movie-year-poster">${movie.year}</div>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error-text">gagal memuat rekomendasi</div>';
    }
}

async function searchMovie() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) { alert('masukkan judul film!'); return; }
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '<div class="loading-text">mencari...</div>';
    try {
        const res = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        if (data.length === 0) {
            resultsDiv.innerHTML = '<div class="error-text">film tidak ditemukan</div>';
            return;
        }
        resultsDiv.innerHTML = `<div style="margin-bottom: 1rem; font-size:0.75rem; color:#8a817c;">ditemukan ${data.length} film</div>`;
        data.forEach(movie => {
            const card = document.createElement('div');
            card.className = 'movie-poster-card';
            card.innerHTML = `
                <div class="poster-container">
                    <img class="movie-poster" src="${movie.Poster_Url}" alt="${movie.Title}" onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
                    <div class="poster-overlay">
                        <span class="movie-rating-badge">⭐ ${movie.Vote_Average.toFixed(1)}</span>
                    </div>
                </div>
                <div class="movie-info-poster">
                    <div class="movie-title-poster" title="${movie.Title}">${movie.Title}</div>
                    <div class="movie-year-poster">${movie.Year}</div>
                    <div class="genre-small">${movie.Genre.substring(0, 40)}${movie.Genre.length > 40 ? '...' : ''}</div>
                </div>
            `;
            resultsDiv.appendChild(card);
        });
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error-text">gagal mencari film</div>';
    }
}

async function loadGenreSelect() {
    try {
        const res = await fetch(`${API_URL}/genres`);
        const data = await res.json();
        const select = document.getElementById('genre-select');
        if (select) {
            select.innerHTML = '<option value="">-- pilih genre --</option>';
            data.genres.forEach(genre => {
                const option = document.createElement('option');
                option.value = genre;
                option.textContent = genre;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading genre select:', error);
    }
}

async function searchByGenre() {
    const select = document.getElementById('genre-select');
    const genre = select?.value;
    if (!genre) { alert('pilih genre terlebih dahulu!'); return; }
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '<div class="loading-text">mencari film...</div>';
    try {
        const res = await fetch(`${API_URL}/genre/${encodeURIComponent(genre)}`);
        const data = await res.json();
        if (data.length === 0) {
            resultsDiv.innerHTML = `<div class="error-text">tidak ada film dengan genre "${genre}"</div>`;
            return;
        }
        resultsDiv.innerHTML = `<div style="margin-bottom: 1rem; font-size:0.75rem; color:#8a817c;">🎭 ${genre} · ${data.length} film</div>`;
        data.slice(0, 20).forEach(movie => {
            const card = document.createElement('div');
            card.className = 'movie-poster-card';
            card.innerHTML = `
                <div class="poster-container">
                    <img class="movie-poster" src="${movie.Poster_Url}" alt="${movie.Title}" onerror="this.src='https://via.placeholder.com/300x450?text=No+Poster'">
                    <div class="poster-overlay">
                        <span class="movie-rating-badge">⭐ ${movie.Vote_Average.toFixed(1)}</span>
                    </div>
                </div>
                <div class="movie-info-poster">
                    <div class="movie-title-poster" title="${movie.Title}">${movie.Title}</div>
                    <div class="movie-year-poster">${movie.Year}</div>
                </div>
            `;
            resultsDiv.appendChild(card);
        });
        if (data.length > 20) {
            const more = document.createElement('div');
            more.className = 'more-text';
            more.innerHTML = `<small>... dan ${data.length - 20} film lainnya</small>`;
            resultsDiv.appendChild(more);
        }
    } catch (error) {
        resultsDiv.innerHTML = '<div class="error-text">gagal memuat film</div>';
    }
}
