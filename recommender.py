import pickle
import streamlit as st
import requests
import dotenv
import os

dotenv.load_dotenv()


with open('movies.pkl', 'rb') as f:
    movies = pickle.load(f)

with open('similarities.pkl', 'rb') as f:
    similarities = pickle.load(f)

with open('new_df.pkl', 'rb') as f:
    new_df = pickle.load(f)

with open('movies_dataset.pkl', 'rb') as f:
    movies_dataset = pickle.load(f).dropna()

movies['overview'] = movies_dataset["overview"]


all_genres = sorted({genre for sublist in movies['genres'] for genre in sublist})

def fetch_movie_data(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={os.getenv('API_KEY')}"
    data = requests.get(url)
    data = data.json()
    return data

def fetch_poster(movie_id):
    path = fetch_movie_data(movie_id)
    poster_path = path.get("poster_path")
    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"

def recommend(movie):
    if movie not in new_df['title'].values:
        return f"'{movie}' not found in the database. Please try another movie."

    index = new_df[new_df['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarities[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = new_df.iloc[i[0]].id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

def suggest_by_genres(selected_genres):
    recommended_movie_names = []
    recommended_movie_posters = []

    genres_list = [g.lower() for g in selected_genres]
    def match_all(genre_tags):
        movie_genres = [tag.lower() for tag in genre_tags]
        return all(g in movie_genres for g in genres_list)

    filtered = movies[movies['genres'].apply(match_all)].copy()
    if filtered.empty:
        return f"No movies found matching genres: {genres_list}"

    filtered = filtered.sort_values(by=['score'], ascending=False)

    for i in range(5):
        movie_id = filtered.iloc[i].id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(filtered.iloc[i].title)

    return recommended_movie_names, recommended_movie_posters

def clickable_image(title, image_url):
    return f'''
        <a href="?selected={title}" target="_self" style="text-decoration: none;">
            <img src="{image_url}" width="150" style="border-radius: 10px; margin: 5px"/>
            <p style="text-align:center; color: white;">{title}</p>
        </a>
    '''

st.title("🎬 Movie Recommendation System")

query_params = st.query_params
selected_title = query_params.get("selected", [None])
# print(selected_title)

option = st.radio("Choose recommendation type:", ["🔍 Search by Title", "🎞 Filter by Genres"])

if option == "🔍 Search by Title":
    st.subheader("Search for a movie title:")
    selected_movie = st.selectbox("Type or select a movie from the dropdown", movies['title'].values)
    if st.button('Show Recommendation'):
        with st.spinner('Fetching recommendations...'):
            recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    html = clickable_image(recommended_movie_names[i], recommended_movie_posters[i])
                    st.markdown(html, unsafe_allow_html=True)

elif option == "🎞 Filter by Genres":
    st.subheader("Select genres:")
    selected_genres = st.multiselect("Choose genres:", all_genres)

    if st.button('Show Recommendation'):
        if not selected_genres:
            st.warning("Please select at least one genre.")
        else:
            with st.spinner('Fetching recommendations...'):
                recommended_movie_names, recommended_movie_posters = suggest_by_genres(selected_genres)
                cols = st.columns(5)
                for i in range(5):
                    with cols[i]:
                        html = clickable_image(recommended_movie_names[i], recommended_movie_posters[i])
                        st.markdown(html, unsafe_allow_html=True)

def truncate_overview(text, word_limit=35):
    if not text or not isinstance(text, str):
        return "No overview available."
    words = text.split()
    return ' '.join(words[:word_limit]) + '...' if len(words) > word_limit else text

if selected_title and selected_title[0]:
    movie_info = movies[movies['title'].str.strip() == selected_title.strip()].iloc[0]

    cols = st.columns(2)
    with st.spinner('Fetching details...'):
        info = fetch_movie_data(movie_info['id'])
        with cols[0]:
            image_url = fetch_poster(movie_info['id'])
            st.image(image_url, width=300)
        with cols[1]:
            # st.markdown("---")
            st.markdown(f"## 🎬 {movie_info['title']}")
            st.markdown(f"**Genres:** {', '.join(movie_info['genres'])}")
            st.markdown(f"**Rating:** {movie_info['vote_average']} ({movie_info['vote_count']} votes)")
            st.markdown(f"**Popularity:** {round(movie_info['popularity'], 2)}")
            st.markdown(f"**Cast:** {', '.join(movie_info['cast'])}")
            st.markdown(f"**Director:** {', '.join(movie_info['crew'])}")
            st.markdown(f"**Release Date:** {info.get('release_date')}")
            st.markdown(f"**Runtime:** {info.get('runtime')} minutes")
            short_overview = truncate_overview(movie_info['overview'], word_limit=35)
            st.markdown(f"**Overview:** {short_overview}")
