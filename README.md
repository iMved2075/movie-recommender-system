# Movie Recommendation System

This project is a **content-based movie recommendation system** built using the TMDB dataset. It uses cosine similarity to recommend movies based on user preferences.

## Features

- **Movie Recommendations**: Suggests movies similar to the movie or genres selected by the user.
- **Poster Fetching**: Displays movie posters alongside recommendations using the TMDB API.
- **Interactive UI**: Built with Streamlit for a user-friendly interface.
- **Movie Information**: Gives information about the recommended movies, including their titles and genres.

## Dataset

The system uses the TMDB 5000 Movies dataset, which contains metadata about movies such as genres, keywords, production companies, and more.

## Installation

1. Clone the repository:
   ```bash
   git 
   cd movie-recommendation-system
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the `movies.pkl`, `new_df`, `movies_dataset` and `similarities.pkl` files are in the project directory.

## Usage

1. Run the application:
   ```bash
   streamlit run recommender.py
   ```

2. Open the application in your browser and select a movie from the dropdown to get recommendations.

## File Structure

- `recommender.py`: Main application file containing the Streamlit interface and recommendation logic.
- `movies.pkl`, `new_df.pkl` and `movies_dataset.pkl`: Preprocessed movie data.
- `similarities.pkl`: Precomputed cosine similarity matrix.
- `input/tmdb-movie-metadata/tmdb_5000_movies.csv`: Raw dataset containing movie metadata such as genres, keywords, production companies, and more.
- `input/tmdb-movie-metadata/tmdb_5000_credits.csv`: Dataset containing information about the cast and crew of movies.

## API Integration

The project uses the TMDB API to fetch movie posters. Ensure you have a valid API key and replace it in the `fetch_poster` function in `.venv` file.

## Example
For recommendation based on selected movie:
1. Select a movie from the dropdown.
2. Click the "Show Recommendation" button.
3. View the recommended movies along with their posters.
4. Select the poster to get additional information about the movie.

For recommendation based on selected genres:
1. Select one or more genres from the dropdown.
2. Click the "Show Recommendation" button.
3. View the recommended movies along with their posters.
4. Select the poster to get additional information about the movie.

## Dependencies

- Python 3.7+
- Streamlit
- Pandas
- Requests
- Pickle
- Python-dotenv
- 

## Acknowledgments

- [TMDB Dataset](https://www.kaggle.com/tmdb/tmdb-movie-metadata)
- [Streamlit](https://streamlit.io/)
