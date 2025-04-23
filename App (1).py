import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import pymysql
from sqlalchemy import create_engine



def get_connection():
    user = '2bw8jBBSyMYoXiE.root'
    password = '8VgxDyP2vIj1wnHh'
    host = 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com'
    port = '4000'
    database = 'imdb'
    engine = create_engine("mysql+mysqlconnector://2bw8jBBSyMYoXiE.root:8VgxDyP2vIj1wnHh@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/imdb")
    return engine

def load_data():
    try:
        engine = get_connection()
        query = "SELECT * FROM all_genres_movies"  # Adjust to your actual table/fields
        df = pd.read_sql(query, engine)
        df['Duration_hours'] = df['Duration'] / 60
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame if loading fails
df=load_data()
st.title("🎬 IMDb Movies Data Dashboard")

# Clean text columns if needed
df['Genre'] = df['Genre'].str.strip()
df['Title'] = df['Title'].str.strip()


# --- Interactive Filtering ---
st.header("Interactive Movie Filter")

# Genre Filter
genres = df['Genre'].unique()
selected_genre = st.selectbox(" Select Genre", options=genres)

# Rating Filter
selected_rating = st.slider(" Min&Max IMDb Rating", min_value=float(df['Rating'].min()),
                            max_value=float(df['Rating'].max()), value=8.0)

# Duration Filter (in minutes)
duration_range = st.slider(" Duration (minutes)", min_value=int(df['Duration'].min()),
                           max_value=int(df['Duration'].max()), value=(90, 180))

# Votes Filter
min_votes = st.number_input(" Min&Max Votes", min_value=0, value=50000, step=1000)

# Apply Filters
filtered_df = df[
    (df['Genre'] == selected_genre) &
    (df['Rating'] >= selected_rating) &
    (df['Duration'] >= duration_range[0]) & (df['Duration'] <= duration_range[1]) &
    (df['Votes'] >= min_votes)
]

# Show filtered results
st.subheader(" Filtered Movies Based on Criteria")
st.dataframe(filtered_df)

# Top 10 Movies by Rating and Votes
st.header("Top 10 Movies by Rating and Voting Counts")
top_movies = df.sort_values(['Rating', 'Votes'], ascending=[False, False]).head(10)
fig1 = px.bar(top_movies, x='Title', y='Rating', color='Votes', title='Top 10 Rated Movies')
st.plotly_chart(fig1)

# Genre Distribution
st.header("Genre Distribution")
genre_counts = df['Genre'].value_counts()
st.bar_chart(genre_counts)

# Average Duration by Genre
st.header("Average Duration by Genre")
avg_duration = df.groupby('Genre')['Duration'].mean().sort_values()
st.bar_chart(avg_duration)

# Voting Trends by Genre
st.header("Voting Trends by Genre")
avg_votes = df.groupby('Genre')['Votes'].mean().sort_values(ascending=False)
st.bar_chart(avg_votes)

# Rating Distribution
st.header("Rating Distribution")
fig2, ax2 = plt.subplots()
sns.histplot(df['Rating'], kde=True, bins=15, ax=ax2)
st.pyplot(fig2)

# Genre-Based Rating Leaders
st.header("Top-Rated Movie per Genre")
top_per_genre = df.loc[df.groupby('Genre')['Rating'].idxmax()]
st.dataframe(top_per_genre[['Genre', 'Title', 'Rating']])

# Most Popular Genres by Voting
st.header("Most Popular Genres by Voting (Pie Chart)")
votes_by_genre = df.groupby('Genre')['Votes'].sum()
fig3 = px.pie(values=votes_by_genre, names=votes_by_genre.index, title="Voting Distribution by Genre")
st.plotly_chart(fig3)

# Duration Extremes
st.header(" Shortest and Longest Movies")

min_dur = df.loc[df['Duration'].idxmin()]
max_dur = df.loc[df['Duration'].idxmax()]

col1, col2 = st.columns(2)

with col1:
    st.subheader(" Shortest Movie")
    st.write(f"**{min_dur['Title']}**")
    st.write(f"🕒 Duration: {min_dur['Duration']} min")

with col2:
    st.subheader("Longest Movie")
    st.write(f"**{max_dur['Title']}**")
    st.write(f"Duration: {max_dur['Duration']} min")

# Ratings by Genre Heatmap
st.header("Average Ratings by Genre (Heatmap)")
ratings_pivot = df.pivot_table(index='Genre', values='Rating', aggfunc='mean')
fig4, ax4 = plt.subplots(figsize=(10, 6))
sns.heatmap(ratings_pivot, annot=True, cmap='coolwarm', ax=ax4)
st.pyplot(fig4)

# Correlation Analysis
st.header("Correlation Between Rating and Votes")
fig5 = px.scatter(df, x='Votes', y='Rating', hover_data=['Title'])
st.plotly_chart(fig5)
