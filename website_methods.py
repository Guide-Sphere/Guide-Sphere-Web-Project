import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Read Data : MongoDB
from pymongo import MongoClient
# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.webdf  # Database name 'webdf'
collection = db.web_coll_1  # Collection name 'web_coll_1'
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
websites = websites[['web_id','web_url','web_img','web_platform','web_title','web_short_desc','web_language']]

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

# Creating tags
# The ultimate concatenation
websites['tags'] = websites['temp_web_platform'] + websites['temp_web_title'] + websites['temp_web_short_desc']

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
            'web_id': websites.iloc[idx]['web_id'],
            'web_url': websites.iloc[idx]['web_url'],
            'web_img': websites.iloc[idx]['web_img'],
            'web_title': websites.iloc[idx]['web_title'],
            'web_platform': websites.iloc[idx]['web_platform'],
            'web_short_desc': websites.iloc[idx]['web_short_desc'],
            'web_language': websites.iloc[idx]['web_language']
        }
        recommended_websites_list.append(website_details)
    
    return recommended_websites_list

