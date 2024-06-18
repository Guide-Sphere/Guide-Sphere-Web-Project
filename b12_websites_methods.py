import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pymongo import MongoClient
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Read Data : MongoDB
from pymongo import MongoClient
# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.b12_websitesdf  # Database name 'b12_websitesdf'
collection = db.websites_coll_1  # Collection name 'websites_coll_1'
# Read data from MongoDB into a list of dictionaries
data_from_mongodb = list(collection.find())
# Convert the list of dictionaries to a pandas DataFrame
websites = pd.DataFrame(data_from_mongodb)

###
###
###

# Data Cleaning
# Remove null values
websites.dropna(inplace=True)
websites = websites.reset_index()
websites = websites[['web_url','web_img','web_platform','web_title','web_short_desc','web_subject','web_class','web_language','web_id']]

# Function to clean title
def clean_title(title):
    return re.sub("[^a-zA-Z0-9 ]", "", title)

# Convert string(sentence) to lists
websites['temp_web_platform'] = websites['web_platform']
websites['temp_web_platform'] = websites['temp_web_platform'].apply(clean_title)
websites['temp_web_platform'] = websites['temp_web_platform'].apply(lambda x: x.split())
websites['temp_web_title'] = websites['web_title']
websites['temp_web_title'] = websites['temp_web_title'].apply(clean_title)
websites['temp_web_title'] = websites['temp_web_title'].apply(lambda x: x.split())
websites['temp_web_short_desc'] = websites['web_short_desc']
websites['temp_web_short_desc'] = websites['temp_web_short_desc'].apply(clean_title)
websites['temp_web_short_desc'] = websites['temp_web_short_desc'].apply(lambda x: x.split())
websites['temp_web_subject'] = websites['web_subject']
websites['temp_web_subject'] = websites['temp_web_subject'].apply(clean_title)
websites['temp_web_subject'] = websites['temp_web_subject'].apply(lambda x: x.split())
websites['temp_web_class'] = websites['web_class'].astype(str)

# Creating tags
# The ultimate concatenation
websites['tags'] = websites['temp_web_title'] + websites['temp_web_platform'] + websites['temp_web_short_desc'] + websites['temp_web_subject']  

# Converting tags from lists to strings
websites['tags'] = websites['tags'].apply(lambda x: " ".join(x))
websites['tags'] = websites['tags'].str.lower()

# Using CountVectorizer for vectorization
cv = CountVectorizer(max_features=2000, stop_words='english')
vectors = cv.fit_transform(websites['tags']).toarray()

# Using cosine similarity for finding distance between vectors
similarity = cosine_similarity(vectors)

# Final logic for recommendation
def recommend_websites(keyword):
    keyword_vector = cv.transform([keyword]).toarray()
    similarity_scores = cosine_similarity(keyword_vector, vectors)[0]
    top_indices = similarity_scores.argsort()[::-1][:10]
    
    recommended_websites_list = []   # list bcz it returns list of dictionaries
    for idx in top_indices:
        website_details = {
            'web_url': websites.iloc[idx]['web_url'],
            'web_img': websites.iloc[idx]['web_img'],
            'web_platform': websites.iloc[idx]['web_platform'],
            'web_title': websites.iloc[idx]['web_title'],
            'web_short_desc': websites.iloc[idx]['web_short_desc'],
            'web_subject': websites.iloc[idx]['web_subject'],
            'web_class': websites.iloc[idx]['web_class'],
            'web_language': websites.iloc[idx]['web_language'],
            'web_id': websites.iloc[idx]['web_id']
        }
        recommended_websites_list.append(website_details)
    
    return recommended_websites_list

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

def get_personalized_websites_recommendations(email):
    try:
        # Find the user data based on the username
        user_data = user_collection.find_one({'email': email})

        if not user_data:
            return "Username not found"
        
        # Extract interests from the user data
        interests = user_data.get('interests', [])

        # Initialize array to store personalized recommendations
        personalized_website_recommendations_list = []

        # Pass each interest keyword to the recommend function and add websites to the array
        for interest in interests:
            recommended_websites = recommend_websites(interest) 
            for website in recommended_websites[:5]:  # Add top 5 recommended websites for each interest
                personalized_website_recommendations_list.append(website)

        # Shuffle the list of personalized recommendations
        shuffle(personalized_website_recommendations_list)

        return personalized_website_recommendations_list
    except Exception as e:
        print("Error occurred while fetching personalized recommendations:", e)
        return "An error occurred while fetching personalized recommendations"

###
###
###

# Search logic for websites
def search_websites(keyword):
    result_websites = websites[websites['tags'].str.contains(keyword, case=False)]
    
    result_websites_list = []
    for idx, website in result_websites.iterrows():
        website_details = {
            'web_url': website['web_url'],
            'web_img': website['web_img'],
            'web_platform': website['web_platform'],
            'web_title': website['web_title'],
            'web_short_desc': website['web_short_desc'],
            'web_subject': website['web_subject'],
            'web_class': website['web_class'],
            'web_language': website['web_language'],
            'web_id': website['web_id']
        }
        result_websites_list.append(website_details)
    
    return result_websites_list
















































