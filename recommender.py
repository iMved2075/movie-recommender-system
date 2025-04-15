import pickle
import streamlit as st
import requests
import dotenv
import os

dotenv.load_dotenv()

st.set_page_config(layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # Default theme
mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = mode

if st.session_state.dark_mode:
    st.markdown("""
        <style>
        body, .stApp {
            background: linear-gradient(to right, #121212, #1e1e1e);
            color: #f0f0f0 !important;
        }
        .movie-card, .trailer-container {
            background-color: rgba(255, 255, 255, 0.05);
            color: #ffffff;
        }
        .css-1kyxreq, .css-1cpxqw2, .css-qrbaxs 
            color: #ffffff !important;
        }
        p, h1, h2, h3, h4 {
            color: #ffffff !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body, .stApp {
            background: linear-gradient(to right, #f4f4f4, #ffffff);
            color: #000000 !important;
        }
        .movie-card, .trailer-container {
            background-color: rgba(0, 0, 0, 0.05);
            color: #000000;
        }
        .css-1kyxreq, .css-1cpxqw2, .css-qrbaxs {
            color: #000000 !important;
        }
        p, h1, h2, h3, h4 {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

with open('movies.pkl', 'rb') as f:
    movies = pickle.load(f)

with open('similarities.pkl', 'rb') as f:
    similarities = pickle.load(f)

with open('new_df.pkl', 'rb') as f:
    new_df = pickle.load(f)




all_genres = sorted({genre for sublist in movies['genres'] for genre in sublist})

def fetch_movie_data(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={os.getenv('API_KEY')}"
    data = requests.get(url)
    data = data.json()
    return data

def fetch_movie_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={os.getenv('API_KEY')}"
    data = requests.get(url)
    data = data.json()
    videos = data.get("results", [])

    for video in videos:
        if video['type'] == "Trailer" and video['site'] == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

def fetch_poster(movie_id):
    path = fetch_movie_data(movie_id)
    poster_path = path.get("poster_path")
    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"

def truncate_overview(movie_id, word_limit=35):
    path = fetch_movie_data(movie_id)
    overview = path.get("overview")
    if not overview or not isinstance(overview, str):
        return "No overview available."
    words = overview.split()
    return ' '.join(words[:word_limit]) + '...' if len(words) > word_limit else overview

def recommend(movie, num_recommendations=15):
    if movie not in new_df['title'].values:
        return [], []

    index = new_df[new_df['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarities[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    count = 0
    for i in distances[1:]:
        movie_id = new_df.iloc[i[0]].id
        title = movies.iloc[i[0]].title
        if title != movie:
            recommended_movie_names.append(title)
            recommended_movie_posters.append(fetch_poster(movie_id))
            count += 1
            if count == num_recommendations:
                break
    return recommended_movie_names, recommended_movie_posters

def suggest_by_genres(selected_genres, num_recommendations=15):
    recommended_movie_names = []
    recommended_movie_posters = []

    genres_list = [g.lower() for g in selected_genres]

    def match_all(genre_tags):
        movie_genres = [tag.lower() for tag in genre_tags]
        return all(g in movie_genres for g in genres_list)

    filtered = movies[movies['genres'].apply(match_all)].copy()
    if filtered.empty:
        return [], []

    filtered = filtered.sort_values(by=['score'], ascending=False)

    for _, row in filtered.head(num_recommendations).iterrows():
        movie_id = row.id
        recommended_movie_names.append(row.title)
        recommended_movie_posters.append(fetch_poster(movie_id))
    return recommended_movie_names, recommended_movie_posters

def clickable_image(title, image_url):
    font_color = "#f0f0f0" if st.session_state.dark_mode else "#000000"
    return f"""
    <div style="text-align: center; margin: 10px;">
        <a href="?selected={title}" target="_self" style="text-decoration: none; color: inherit;">
            <div style="transition: transform 0.2s; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.4);">
                <img src="{image_url}" width="150" style="border-radius: 12px;"/>
            </div>
            <p style="margin-top: 5px; font-size: 14px; font-weight: 500; color: {font_color};">{title}</p>
        </a>
    </div>
    """

def show_recommendations(names, posters):
    total = len(names)
    if total == 0:
        st.warning("No recommendations available.")
        return

    rows = (total + 4) // 5  # Ceiling division for number of rows
    for r in range(rows):
        cols = st.columns(5)
        for i in range(5):
            idx = r * 5 + i
            if idx < total:
                with cols[i]:
                    html = clickable_image(names[idx], posters[idx])
                    st.markdown(html, unsafe_allow_html=True)

st.title("🎬 SuggestIt – Recommendations that get you")

query_params = st.query_params
selected_title = query_params.get("selected", [None])


option = st.radio("Choose recommendation type:", ["🔍 Search by Title", "🎞 Filter by Genres"])

if option == "🔍 Search by Title":
    st.subheader("Search for a movie title:")
    selected_movie = st.selectbox("Type or select a movie from the dropdown", movies['title'].values)
    if st.button('Show Recommendation'):
        st.query_params.selected = selected_movie
        st.rerun()


elif option == "🎞 Filter by Genres":
    st.query_params.clear()
    selected_title = [None]
    st.subheader("Select genres:")
    selected_genres = st.multiselect("Choose genres:", all_genres)

    if st.button('Show Recommendation'):
        if not selected_genres:
            st.warning("Please select at least one genre.")
        else:
            with st.spinner('Fetching recommendations...'):
                recommended_movie_names, recommended_movie_posters = suggest_by_genres(selected_genres)

                st.markdown("### 🎥 Recommended Movies")
                st.markdown("&nbsp;")

                show_recommendations(recommended_movie_names, recommended_movie_posters)

if selected_title and selected_title[0]:
    st.markdown("""
        <style>
        .movie-card {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
            color: #fff;
        }
        .main {
            background: linear-gradient(to right, #121212, #1e1e1e);
        }
        img:hover {
            transform: scale(1.05);
            transition: 0.3s ease;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    movie_info = movies[movies['title'].str.strip() == selected_title.strip()].iloc[0]
    cols = st.columns([1, 2])

    with st.spinner('Fetching details...'):
        info = fetch_movie_data(movie_info['id'])

        with cols[0]:
            image_url = fetch_poster(movie_info['id'])
            st.image(image_url, width=300)

        with cols[1]:
            st.markdown(f"""
                <div style="
                    background-color: rgba(255, 255, 255, 0.05);
                    padding: 25px;
                    border-radius: 16px;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
                    color: #fff;
                ">
                    <h2>🎬 {movie_info['title']}</h2>
                    <p><strong>🎭 Genres:</strong> {', '.join(movie_info['genres'])}</p>
                    <p><strong>⭐ Rating:</strong> {movie_info['vote_average']} ({movie_info['vote_count']} votes)</p>
                    <p><strong>🔥 Popularity:</strong> {round(movie_info['popularity'], 2)}</p>
                    <p><strong>🎬 Cast:</strong> {', '.join(movie_info['cast'])}</p>
                    <p><strong>🎥 Director:</strong> {', '.join(movie_info['crew'])}</p>
                    <p><strong>📅 Release Date:</strong> {info.get('release_date')}</p>
                    <p><strong>⏱️ Runtime:</strong> {info.get('runtime')} minutes</p>
                    <p><strong>📝 Overview:</strong> {truncate_overview(movie_info['id'], word_limit=35)}</p>
                </div>
            """, unsafe_allow_html=True)
        trailer_url = fetch_movie_trailer(movie_info['id'])
        if trailer_url:
            st.markdown("""
                <style>
                .trailer-container {
                    text-align: center;
                    margin-top: 30px;
                    margin-bottom: 40px;
                }
                .trailer-title {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 15px;
                }
                .stVideo iframe {
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                }
                </style>
                <div class="trailer-container">
                    <div class="trailer-title">🎬 Watch Trailer</div>
                </div>
            """, unsafe_allow_html=True)
            st.video(trailer_url)
        else:
            st.markdown("<div style='text-align: center; color: #bbb; margin-top: 30px;'>No trailer available.</div>",
                        unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🎥 Recommended Movies")
    with st.spinner("Fetching recommendations..."):
        recommended_movie_names, recommended_movie_posters = recommend(selected_title)
        show_recommendations(recommended_movie_names, recommended_movie_posters)