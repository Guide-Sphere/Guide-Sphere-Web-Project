from flask import Flask, render_template, request, session
from flask import Blueprint
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from datetime import datetime
import json
import random

# Read Data : MongoDB
from pymongo import MongoClient
# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.coursesdf  # Database name 'coursesdf'
collection = db.courses_coll_1  # Collection name 'courses_coll_1'
# Read data from MongoDB into a list of dictionaries
data_from_mongodb = list(collection.find())
# Convert the list of dictionaries to a pandas DataFrame
courses = pd.DataFrame(data_from_mongodb)

###
###
###

# Data Cleaning
# Remove null values
courses.dropna(inplace=True)
courses = courses.reset_index()
courses = courses[['course_id','course_url', 'course_img', 'course_duration', 'course_price',
       'course_price_original', 'course_instrutor', 'course_title',
       'course_short_desc', 'course_rating', 'course_date', 'course_language',
       'course_outcome_text', 'course_outcome_html', 'course_about_text',
       'course_about_html','course_platform']]

# Function to clean title
def clean_title(title):
    return re.sub("[^a-zA-Z0-9 ]", "", title)

# Convert string(sentence) to lists
courses['temp_course_short_desc'] = courses['course_short_desc']
courses['temp_course_short_desc'] = courses['temp_course_short_desc'].apply(clean_title)
courses['temp_course_short_desc'] = courses['temp_course_short_desc'].apply(lambda x: x.split())
courses['temp_course_instrutor'] = courses['course_instrutor']
courses['temp_course_instrutor'] = courses['temp_course_instrutor'].apply(clean_title)
courses['temp_course_instrutor'] = courses['temp_course_instrutor'].apply(lambda x: x.split())
courses['temp_title'] = courses['course_title']
courses['temp_title'] = courses['temp_title'].apply(clean_title)
courses['temp_title'] = courses['temp_title'].apply(lambda x: x.split())

###
###
###

# Recommendation function
# The ultimate concatenation
courses['tags'] = courses['temp_title'] + courses['temp_course_short_desc'] + courses['temp_course_instrutor']

# Converting tags from lists to strings
courses['tags'] = courses['tags'].apply(lambda x: " ".join(x))
courses['tags'] = courses['tags'].str.lower()

# Using CountVectorizer for vectorization
cv = CountVectorizer(max_features=2000, stop_words='english')
vectors = cv.fit_transform(courses['tags']).toarray()

# Using cosine similarity for finding distance between vectors
similarity = cosine_similarity(vectors)

# Final logic for recommendation
def recommend_courses(keyword):
    keyword_vector = cv.transform([keyword]).toarray()
    similarity_scores = cosine_similarity(keyword_vector, vectors)[0]
    top_indices = similarity_scores.argsort()[::-1][:10]
    
    recommended_courses_list = []   # list bcz it returns list of dictionaries
    for idx in top_indices:
        course_details = {
            'course_url': courses.iloc[idx]['course_url'],
            'course_img': courses.iloc[idx]['course_img'],
            'course_duration': courses.iloc[idx]['course_duration'],
            'course_price': courses.iloc[idx]['course_price'],
            'course_price_original': courses.iloc[idx]['course_price_original'],
            'course_instrutor': courses.iloc[idx]['course_instrutor'],
            'course_title': courses.iloc[idx]['course_title'],
            'course_short_desc': courses.iloc[idx]['course_short_desc'],
            'course_rating': courses.iloc[idx]['course_rating'],
            'course_date': courses.iloc[idx]['course_date'],
            'course_language': courses.iloc[idx]['course_language'],
            'course_outcome_text': courses.iloc[idx]['course_outcome_text'],
            'course_outcome_html': courses.iloc[idx]['course_outcome_html'],
            'course_about_text': courses.iloc[idx]['course_about_text'],
            'course_about_html': courses.iloc[idx]['course_about_html'],
            'course_id': courses.iloc[idx]['course_id'],
            'course_platform': courses.iloc[idx]['course_platform']
        }
        recommended_courses_list.append(course_details)
  
    return recommended_courses_list

###
###
###

# Recently added courses/ latest courses
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
    
def get_recent_courses():
    # To prevent that date issue part
    courses['course_date'] = courses['course_date'].apply(clean_date)
    # Convert 'course_date' to datetime
    courses['course_date'] = pd.to_datetime(courses['course_date'], format='%m/%Y') 
    # Get current month and year
    current_date = datetime.now() 
    # Filter courses that are nearest or in the same month and year as the current month and year
    recent_courses = courses[courses['course_date'].dt.strftime('%m/%Y') <= current_date.strftime('%m/%Y')].sort_values(by='course_date', ascending=False).head(10)
    # Convert 'course_date' back to the original format
    courses['course_date'] = courses['course_date'].apply(format_date)
    courses['course_date'] = courses['course_date'].apply(clean_date)
    
    recent_courses_list = []
    for idx, course in recent_courses.iterrows():
        course_details = {
            'course_url': course['course_url'],
            'course_img': course['course_img'],
            'course_duration': course['course_duration'],
            'course_price': course['course_price'],
            'course_price_original': course['course_price_original'],
            'course_instrutor': course['course_instrutor'],
            'course_title': course['course_title'],
            'course_short_desc': course['course_short_desc'],
            'course_rating': course['course_rating'],
            'course_date': course['course_date'],
            'course_language': course['course_language'],
            'course_outcome_text': course['course_outcome_text'],
            'course_outcome_html': course['course_outcome_html'],
            'course_about_text': course['course_about_text'],
            'course_about_html': course['course_about_html'],
            'course_id': course['course_id'],
            'course_platform': course['course_platform'],
        }
        recent_courses_list.append(course_details)
    courses['course_date'] = courses['course_date'].apply(format_date)

    return recent_courses_list

###
###
###

# Persnoalised recommendations

# MongoDB part
# Load data from mongodb
from pymongo import MongoClient
from random import shuffle
# Initialize MongoDB client
client = MongoClient('mongodb://localhost:27017/')  # Update with your MongoDB connection URI
db = client['users']  # Update with your database name
user_collection = db['users']  # Assuming your collection name is 'users'

def get_personalized_course_recommendations(email):
    try:
        # Find the user data based on the username
        user_data = user_collection.find_one({'email': email})

        if not user_data:
            return "Username not found"
        
        # Extract interests from the user data
        interests = user_data.get('interests', [])

        # Initialize array to store personalized recommendations
        personalized_course_recommendations_list = []

        # Pass each interest keyword to the recommend function and add recommended courses to the array
        for interest in interests:
            recommended_courses = recommend_courses(interest) 
            for course in recommended_courses[:5]:  # Add top 5 recommended courses for each interest
                personalized_course_recommendations_list.append(course)

        # Shuffle the list of personalized recommendations
        shuffle(personalized_course_recommendations_list)

        return personalized_course_recommendations_list
    except Exception as e:
        print("Error occurred while fetching personalized recommendations:", e)
        return "An error occurred while fetching personalized recommendations"

###
###
###

# Search Courses function
def search_courses(keyword):
    result_courses = courses[courses['tags'].str.contains(keyword, case=False)]

    result_courses_list = []
    for idx, course in result_courses.iterrows():
        course_details = {
            'course_url': course['course_url'],
            'course_img': course['course_img'],
            'course_duration': course['course_duration'],
            'course_price': course['course_price'],
            'course_price_original': course['course_price_original'],
            'course_instrutor': course['course_instrutor'],
            'course_title': course['course_title'],
            'course_short_desc': course['course_short_desc'],
            'course_rating': course['course_rating'],
            'course_date': course['course_date'],
            'course_language': course['course_language'],
            'course_outcome_text': course['course_outcome_text'],
            'course_outcome_html': course['course_outcome_html'],
            'course_about_text': course['course_about_text'],
            'course_about_html': course['course_about_html'],
            'course_id': course['course_id'],
            'course_platform': courses['course_platform']
        }
        result_courses_list.append(course_details)
    
    return result_courses_list

###
###
###

# Course Details Function
def getCourse(title):
    course_data = courses[courses['course_title'] == title]

    if course_data.empty:
        return None
    else:
        course_data = course_data.iloc[0]
        course_details = {
            'course_url': course_data['course_url'],
            'course_img': course_data['course_img'],
            'course_duration': course_data['course_duration'],
            'course_price': course_data['course_price'],
            'course_price_original': course_data['course_price_original'],
            'course_instrutor': course_data['course_instrutor'],
            'course_title': course_data['course_title'],
            'course_short_desc': course_data['course_short_desc'],
            'course_rating': course_data['course_rating'],
            'course_date': course_data['course_date'],
            'course_language': course_data['course_language'],
            'course_outcome_text': course_data['course_outcome_text'],
            'course_outcome_html': course_data['course_outcome_html'],
            'course_about_text': course_data['course_about_text'],
            'course_about_html': course_data['course_about_html'],
            'course_id': course_data['course_id'],
            'course_platform': course_data['course_platform'],
        }
        return course_details

###
###
###

def get_top_rated_courses():
    # Ensure the 'course_rating' column is numeric, coercing errors to NaN
    courses['course_rating'] = pd.to_numeric(courses['course_rating'], errors='coerce')
    
    # Optionally fill NaN values with a default value, e.g., 0
    courses['course_rating'].fillna(0, inplace=True)
    
    # Sort courses by 'course_rating' in descending order and get the top 20
    top_rated_courses = courses.sort_values(by='course_rating', ascending=False).head(20)
    
    top_rated_courses_list = []
    for idx, course in top_rated_courses.iterrows():
        course_details = {
            'course_url': course['course_url'],
            'course_img': course['course_img'],
            'course_duration': course['course_duration'],
            'course_price': course['course_price'],
            'course_price_original': course['course_price_original'],
            'course_instrutor': course['course_instrutor'],
            'course_title': course['course_title'],
            'course_short_desc': course['course_short_desc'],
            'course_rating': course['course_rating'],
            'course_date': course['course_date'],
            'course_language': course['course_language'],
            'course_outcome_text': course['course_outcome_text'],
            'course_outcome_html': course['course_outcome_html'],
            'course_about_text': course['course_about_text'],
            'course_about_html': course['course_about_html'],
            'course_id': course['course_id'],
            'course_platform': course['course_platform'],
        }
        top_rated_courses_list.append(course_details)

    return top_rated_courses_list

