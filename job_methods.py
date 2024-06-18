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
db = mongo_client.jobsdf  # Database name 'jobsdf'
collection = db.jobs_coll_2  # Collection name 'jobs_coll_1'
# Read data from MongoDB into a list of dictionaries
data_from_mongodb = list(collection.find())
# Convert the list of dictionaries to a pandas DataFrame
jobs = pd.DataFrame(data_from_mongodb)

###
###
###

# Data Cleaning
# Remove null values
jobs.dropna(inplace=True)
jobs = jobs.reset_index()
jobs = jobs[['job_id', 'job_url', 'job_role', 'job_company','job_experience',
            'job_salary', 'job_location', 'job_skills', 'job_logo',
            'job_desc_pref1', 'job_desc_pref2', 'job_desc_pref3']]

# Function to clean title
def clean_title(title):
    return re.sub("[^a-zA-Z0-9 ]", "", title)

# Convert string(sentence) to lists
jobs['temp_job_role'] = jobs['job_role']
jobs['temp_job_role'] = jobs['temp_job_role'].apply(clean_title)
jobs['temp_job_role'] = jobs['temp_job_role'].apply(lambda x: x.split())
jobs['temp_job_company'] = jobs['job_company']
jobs['temp_job_company'] = jobs['temp_job_company'].apply(clean_title)
jobs['temp_job_company'] = jobs['temp_job_company'].apply(lambda x: x.split())
jobs['temp_job_skills'] = jobs['job_skills']
jobs['temp_job_skills'] = jobs['temp_job_skills'].apply(clean_title)
jobs['temp_job_skills'] = jobs['temp_job_skills'].apply(lambda x: x.split())
jobs['temp_job_location'] = jobs['job_location']
jobs['temp_job_location'] = jobs['temp_job_location'].apply(clean_title)
jobs['temp_job_location'] = jobs['temp_job_location'].apply(lambda x: x.split())

###
###
###

# Recommendation function
# The ultimate concatenation
jobs['tags'] =   jobs['temp_job_company'] + jobs['temp_job_skills'] + jobs['temp_job_role'] + jobs['temp_job_location']

# Converting tags from lists to strings
jobs['tags'] = jobs['tags'].apply(lambda x: " ".join(x))
jobs['tags'] = jobs['tags'].str.lower()

# Using CountVectorizer for vectorization
cv = CountVectorizer(max_features=2000, stop_words='english')
vectors = cv.fit_transform(jobs['tags']).toarray()

# Using cosine similarity for finding distance between vectors
similarity = cosine_similarity(vectors)

# Final logic for recommendation
def recommend_jobs(keyword):
    keyword_vector = cv.transform([keyword]).toarray()
    similarity_scores = cosine_similarity(keyword_vector, vectors)[0]
    top_indices = similarity_scores.argsort()[::-1][:10]
    
    recommended_jobs_list = []   # list bcz it returns list of dictionaries
    for idx in top_indices:
        job_details = {
            'job_id': jobs.iloc[idx]['job_id'],
            'job_url': jobs.iloc[idx]['job_url'],
            'job_role': jobs.iloc[idx]['job_role'],
            'job_company': jobs.iloc[idx]['job_company'],
            'job_experience': jobs.iloc[idx]['job_experience'],
            'job_salary': jobs.iloc[idx]['job_salary'],
            'job_location': jobs.iloc[idx]['job_location'],
            'job_skills': jobs.iloc[idx]['job_skills'],
            'job_logo': jobs.iloc[idx]['job_logo'],
            'job_desc_pref1': jobs.iloc[idx]['job_desc_pref1'],
            'job_desc_pref2': jobs.iloc[idx]['job_desc_pref2'],
            'job_desc_pref3': jobs.iloc[idx]['job_desc_pref3'],
        }

        # print(job_details['job_title'])
        recommended_jobs_list.append(job_details)
    
    return recommended_jobs_list

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

def get_personalized_job_recommendations(email):
    try:
        # Find the user data based on the username
        user_data = user_collection.find_one({'email': email})

        if not user_data:
            return "Username not found"
        
        # Extract interests from the user data
        interests = user_data.get('interests', [])

        # Initialize array to store personalized recommendations
        personalized_job_recommendations_list = []

        # Pass each interest keyword to the recommend function and add recommended jobs to the array
        for interest in interests:
            recommended_jobs = recommend_jobs(interest) 
            for job in recommended_jobs[:5]:  # Add top 5 recommended jobs for each interest
                personalized_job_recommendations_list.append(job)

        # Shuffle the list of personalized recommendations
        shuffle(personalized_job_recommendations_list)

        return personalized_job_recommendations_list
    except Exception as e:
        print("Error occurred while fetching personalized recommendations:", e)
        return "An error occurred while fetching personalized recommendations"

###
###
###

# Search Jobs function
def search_jobs(keyword):
    result_jobs = jobs[jobs['tags'].str.contains(keyword, case=False)]

    result_jobs_list = []
    for idx, job in result_jobs.iterrows():
        job_details = {
            'job_id': job['job_id'],
            'job_url': job['job_url'],
            'job_role': job['job_role'],
            'job_company': job['job_company'],
            'job_experience': job['job_experience'],
            'job_salary': job['job_salary'],
            'job_location': job['job_location'],
            'job_skills': job['job_skills'], 
            'job_logo': job['job_logo'], 
            'job_desc_pref1': job['job_desc_pref1'],
            'job_desc_pref2': job['job_desc_pref2'],
            'job_desc_pref3': job['job_desc_pref3'],
        }
        result_jobs_list.append(job_details)
    
    return result_jobs_list

###
###
###

# Job Details Function
def getJob(title):
    job_data = jobs[jobs['job_role'] == title]

    if job_data.empty:
        return None
    else:
        job_data = job_data.iloc[0]
        job_details = {
            'job_id': job_data['job_id'],
            'job_url': job_data['job_url'],
            'job_role': job_data['job_role'],
            'job_company': job_data['job_company'],
            'job_experience': job_data['job_experience'],
            'job_salary': job_data['job_salary'],
            'job_location': job_data['job_location'],
            'job_skills': job_data['job_skills'], 
            'job_logo': job_data['job_logo'], 
            'job_desc_pref1': job_data['job_desc_pref1'],
            'job_desc_pref2': job_data['job_desc_pref2'],
            'job_desc_pref3': job_data['job_desc_pref3'],
        }
        return job_details

