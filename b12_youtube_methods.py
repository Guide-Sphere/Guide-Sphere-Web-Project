import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import MongoClient
import pandas as pd
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import json
import random

# Read Data : MongoDB
from pymongo import MongoClient
# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.b12_youtubedf  # Database name 'youtubedf'
collection = db.yt_coll_1  # Collection name 'yt_coll_1'
# Read data from MongoDB into a list of dictionaries
data_from_mongodb = list(collection.find())
# Convert the list of dictionaries to a pandas DataFrame
youtube_data = pd.DataFrame(data_from_mongodb)

###
###
###

# Data Cleaning
# Remove null values
youtube_data.dropna(inplace=True)
youtube_data = youtube_data.reset_index()
youtube_data = youtube_data[['yt_img','yt_url','yt_duration','yt_price','yt_origianl_price','yt_instructor',
                             'yt_title','yt_short_desc','yt_course_rating','yt_date','yt_language','yt_subject','yt_class',
                             'yt_about','yt_id']]

# Function to clean title
def clean_title(title):
    return re.sub("[^a-zA-Z0-9 ]", "", title)

# Convert string(sentence) to lists
youtube_data['temp_yt_instructor'] = youtube_data['yt_instructor']
youtube_data['temp_yt_instructor'] = youtube_data['temp_yt_instructor'].apply(clean_title)
youtube_data['temp_yt_instructor'] = youtube_data['temp_yt_instructor'].apply(lambda x: x.split())
youtube_data['temp_yt_title'] = youtube_data['yt_title']
youtube_data['temp_yt_title'] = youtube_data['temp_yt_title'].apply(clean_title)
youtube_data['temp_yt_title'] = youtube_data['temp_yt_title'].apply(lambda x: x.split())
youtube_data['temp_yt_short_desc'] = youtube_data['yt_short_desc']
youtube_data['temp_yt_short_desc'] = youtube_data['temp_yt_short_desc'].apply(clean_title)
youtube_data['temp_yt_short_desc'] = youtube_data['temp_yt_short_desc'].apply(lambda x: x.split())
youtube_data['temp_yt_subject'] = youtube_data['yt_subject']
youtube_data['temp_yt_subject']  = youtube_data['temp_yt_subject'].apply(clean_title)
youtube_data['temp_yt_subject']  = youtube_data['temp_yt_subject'].apply(lambda x: x.split())
youtube_data['temp_yt_class'] = youtube_data['yt_class'].astype(str)
youtube_data['temp_yt_about'] = youtube_data['yt_about']
youtube_data['temp_yt_about']  = youtube_data['temp_yt_about'].apply(clean_title)
youtube_data['temp_yt_about']  = youtube_data['temp_yt_about'].apply(lambda x: x.split())

###
###
###

# Recommendation function
# The ultimate concatenation
youtube_data['tags'] =  youtube_data['temp_yt_title'] + youtube_data['temp_yt_instructor'] + youtube_data['temp_yt_short_desc'] + youtube_data['temp_yt_subject']  + youtube_data['temp_yt_about'] 

# Converting tags from lists to strings
youtube_data['tags'] = youtube_data['tags'].apply(lambda x: " ".join(x))
youtube_data['tags'] = youtube_data['tags'].str.lower()

# Using CountVectorizer for vectorization
cv = CountVectorizer(max_features=2000, stop_words='english')
vectors = cv.fit_transform(youtube_data['tags']).toarray()

# Using cosine similarity for finding distance between vectors
similarity = cosine_similarity(vectors)

# Final logic for recommendation
def recommend_yts(keyword):
    keyword_vector = cv.transform([keyword]).toarray()
    similarity_scores = cosine_similarity(keyword_vector, vectors)[0]
    top_indices = similarity_scores.argsort()[::-1][:10]
    
    recommended_yts_list = []   # list bcz it returns list of dictionaries
    for idx in top_indices:
        yt_details = {
            'yt_img': youtube_data.iloc[idx]['yt_img'],
            'yt_url': youtube_data.iloc[idx]['yt_url'],
            'yt_duration': youtube_data.iloc[idx]['yt_duration'],
            'yt_price': youtube_data.iloc[idx]['yt_price'],
            'yt_origianl_price': youtube_data.iloc[idx]['yt_origianl_price'],
            'yt_instructor': youtube_data.iloc[idx]['yt_instructor'],
            'yt_title': youtube_data.iloc[idx]['yt_title'],
            'yt_short_desc': youtube_data.iloc[idx]['yt_short_desc'],
            'yt_course_rating': youtube_data.iloc[idx]['yt_course_rating'],
            'yt_date': youtube_data.iloc[idx]['yt_date'],
            'yt_language': youtube_data.iloc[idx]['yt_language'],
            'yt_subject': youtube_data.iloc[idx]['yt_subject'],
            'yt_class': youtube_data.iloc[idx]['yt_subject'],
            'yt_about': youtube_data.iloc[idx]['yt_about'],
            'yt_id': youtube_data.iloc[idx]['yt_id']
        }
        recommended_yts_list.append(yt_details)
  
    return recommended_yts_list

###
###
###

# Recently added Youtube Videos/ latest Playlists
def format_date(date):
    # Extract year and month from the datetime object
    year = str(date.year)
    month = str(date.month).zfill(2)  # Zero-padding for single-digit months
    # Format the date as 'mm/yyyy'
    formatted_date = f"{month}/{year}"
    return formatted_date

def clean_date(date_str):
    try:
        return pd.to_datetime(date_str, format='%m/%Y')
    except (ValueError, TypeError):
        return pd.NaT  # Return NaT for invalid or missing dates
    
def get_recent_yts():
    # To prevent that date issue part
    youtube_data['yt_date'] = youtube_data['yt_date'].apply(clean_date)
    # Convert 'yt_date' to datetime
    youtube_data['yt_date'] = pd.to_datetime(youtube_data['yt_date'], format='%m/%Y') 
    # Get current month and year
    current_date = datetime.now() 
    # Filter Youtube Vidoes that are nearest or in the same month and year as the current month and year
    recent_yts = youtube_data[youtube_data['yt_date'].dt.strftime('%m/%Y') <= current_date.strftime('%m/%Y')].sort_values(by='yt_date', ascending=False).head(10)
    # Convert 'yt_date' back to the original format
    youtube_data['yt_date'] = youtube_data['yt_date'].apply(format_date)
    youtube_data['yt_date'] = youtube_data['yt_date'].apply(clean_date)
    
    recent_yts_list = []
    for idx, yt in recent_yts.iterrows():
        yt_details = {
            'yt_img': yt['yt_img'],
            'yt_url': yt['yt_url'],
            'yt_duration': yt['yt_duration'],
            'yt_price': yt['yt_price'],
            'yt_origianl_price': yt['yt_origianl_price'],
            'yt_instructor': yt['yt_instructor'],
            'yt_title': yt['yt_title'],
            'yt_short_desc': yt['yt_short_desc'],
            'yt_course_rating': yt['yt_course_rating'],
            'yt_date': yt['yt_date'],
            'yt_language': yt['yt_language'],
            'yt_subject': yt['yt_subject'],
            'yt_class': yt['yt_class'],
            'yt_about': yt['yt_about'],
            'yt_id': yt['yt_id']
        }
        recent_yts_list.append(yt_details)
    youtube_data['yt_date'] = youtube_data['yt_date'].apply(format_date)

    return recent_yts_list

###
###
###

# Persnoalised recommendations
# Load data from mongodb
from pymongo import MongoClient
from random import shuffle
# Initialize MongoDB client
client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection URI
db = client['users']  # Update with your database name
user_collection = db['users']  # Assuming your collection name is 'users'

def get_personalized_yt_recommendations(email):
    try:
        # Find the user data based on the username
        user_data = user_collection.find_one({'email': email})

        if not user_data:
            return "Username not found"
        
        # Extract interests from the user data
        interests = user_data.get('interests', [])

        # Initialize array to store personalized recommendations
        personalized_yt_recommendations_list = []

        # Pass each interest keyword to the recommend function and add Youtube Playlists to the array
        for interest in interests:
            recommended_yts = recommend_yts(interest) 
            for course in recommended_yts[:5]:  # Add top 5 recommended Youtube Playlists for each interest
                personalized_yt_recommendations_list.append(course)

        # Shuffle the list of personalized recommendations
        shuffle(personalized_yt_recommendations_list)

        return personalized_yt_recommendations_list
    except Exception as e:
        print("Error occurred while fetching personalized recommendations:", e)
        return "An error occurred while fetching personalized recommendations"

###
###
###

# Search Youtube Videos function
def search_yts(keyword):
    result_yts = youtube_data[youtube_data['tags'].str.contains(keyword, case=False)]

    result_yt_list = []
    for idx, yt in result_yts.iterrows():
        yt_details = {
            'yt_img': yt['yt_img'],
            'yt_url': yt['yt_url'],
            'yt_duration': yt['yt_duration'],
            'yt_price': yt['yt_price'],
            'yt_origianl_price': yt['yt_origianl_price'],
            'yt_instructor': yt['yt_instructor'],
            'yt_title': yt['yt_title'],
            'yt_short_desc': yt['yt_short_desc'],
            'yt_course_rating': yt['yt_course_rating'],
            'yt_date': yt['yt_date'],
            'yt_language': yt['yt_language'],
            'yt_subject': yt['yt_subject'],
            'yt_class': yt['yt_class'],
            'yt_about': yt['yt_about'],
            'yt_id': yt['yt_id']
        }
        result_yt_list.append(yt_details)
    
    return result_yt_list

###
###
###

# Youtube Video Details Function
def getYt(title):
    yt_data = youtube_data[youtube_data['yt_title'] == title]

    if yt_data.empty:
        return None
    else:
        yt_data = yt_data.iloc[0]
        yt_details = {
            'yt_img': yt_data['yt_img'],
            'yt_url': yt_data['yt_url'],
            'yt_duration': yt_data['yt_duration'],
            'yt_price': yt_data['yt_price'],
            'yt_origianl_price': yt_data['yt_origianl_price'],
            'yt_instructor': yt_data['yt_instructor'],
            'yt_title': yt_data['yt_title'],
            'yt_short_desc': yt_data['yt_short_desc'],
            'yt_course_rating': yt_data['yt_course_rating'],
            'yt_date': yt_data['yt_date'],
            'yt_language': yt_data['yt_language'],
            'yt_subject': yt_data['yt_subject'],
            'yt_class': yt_data['yt_class'],
            'yt_about': yt_data['yt_about'],
            'yt_id': yt_data['yt_id']
        }
        return yt_details
















