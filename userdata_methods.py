from pymongo import MongoClient
from bson import Binary
import pandas as pd
import nltk
from nltk.corpus import stopwords
from collections import Counter

# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.users  # Database name 'users'
collection = db.users  # Collection name 'users'

def getuserdata(email):
    # Find user document in MongoDB based on email
    user_document = collection.find_one({"email": email})

    if user_document:
        # Extract user details from the document
        user_details = {
            'email': user_document['email'],
            'password': user_document['password'],
            'interests': user_document['interests']
        }

        # Check if the user document contains the 'fullName' field
        if 'fullName' in user_document:
            user_details['fullName'] = user_document['fullName']

        # Check if the user document contains the 'moreAboutUser' field
        if 'moreAboutUser' in user_document:
            user_details['moreAboutUser'] = user_document['moreAboutUser']

        # Check if the user document contains the 'userPhoto' field
        if 'userPhoto' in user_document:
            user_details['userPhoto'] = user_document['userPhoto']

        # Check if the user document contains the 'education' field
        if 'education' in user_document:
            user_details['education'] = user_document['education']

        return user_details  # Return user details as a list containing a dictionary
    else:
        return []  # Return an empty list if user not found
    
def insert_user_fullName(email, fullName):
    # Update user document in MongoDB to insert fullName
    collection.update_one({"email": email}, {"$set": {"fullName": fullName}})

def insert_user_moreAboutUser(email, moreAboutUser):
    # Update user document in MongoDB to insert moreAboutUser
    collection.update_one({"email": email}, {"$set": {"moreAboutUser": moreAboutUser}})

def insert_user_userPhoto(email, userPhoto):
    # Update user document in MongoDB to insert userPhoto
    collection.update_one({"email": email}, {"$set": {"userPhoto": userPhoto}}) 

def insert_user_interests(email, interests):
    # Update user document in MongoDB to insert interests
    collection.update_one({"email": email}, {"$push": {"interests": interests}}) 

def delete_user_interests(email, selected_interests):
    # Delete selected interests from user document in MongoDB
    collection.update_one({"email": email}, {"$pull": {"interests": {"$in": selected_interests}}})

def insert_user_education(email, collegeName, specialization, grade):
    # Create education document
    education_det = {
        "collegeName": collegeName,
        "specialization": specialization,
        "grade": grade
    }
    
    # Find user document by email and update education field
    collection.update_one({"email": email}, {"$push": {"education": education_det}})

def delete_user_education(email, selected_colleges):
    collection.update_one(
        {"email": email},
        {"$pull": {"education": {"collegeName": {"$in": selected_colleges}}}}
    )

# Functions realted to storing user Activity
def store_and_check(email, keyword):

    # Find user document in MongoDB based on email
    user_document = collection.find_one({"email": email})

    search_term = keyword

    # Update user document in MongoDB to insert Search string
    collection.update_one({"email": email}, {'$push': {'searchString': search_term}}, upsert=True) 

    search_strings = user_document.get('searchString', []) if user_document else []

    if len(search_strings) >= 20:
        check_for_repeat(email, search_strings)
        # Clear the Search string field
        collection.update_one({"email": email}, {'$set': {'searchString': []}})

    pass

# Check for repeated words
def check_for_repeat(email, search_strings):
    stop_words = set(stopwords.words('english'))
    words = [word for search_term in search_strings for word in nltk.word_tokenize(search_term) if word.isalnum() and word.lower() not in stop_words]
    
    counter = Counter(words)
    # print("Word counts:", counter)  # Debugging line to print word counts
    # Only consider words that have repeated more than 2 times
    repeated = [word for word, count in counter.items() if count > 5]

    # Get the current list of repeated strings from the database
    user_document = collection.find_one({"email": email})
    current_repeated_strings = user_document.get('interests', []) if user_document else []

    # Only insert words that are not already present in the Repeated string field
    words_to_insert = [word for word in repeated if word.lower() not in map(str.lower, current_repeated_strings)]

    if words_to_insert:
        collection.update_one({"email": email}, {'$push': {'interests': {'$each': words_to_insert}}}, upsert=True)

