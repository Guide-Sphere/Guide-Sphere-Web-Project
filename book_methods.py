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
db = mongo_client.booksdf  # Database name 'booksdf'
collection = db.books_coll_1  # Collection name 'books_coll_1'
# Read data from MongoDB into a list of dictionaries
data_from_mongodb = list(collection.find())
# Convert the list of dictionaries to a pandas DataFrame
books = pd.DataFrame(data_from_mongodb)

###
###
###

# Data Cleaning
# Remove null values
books.dropna(inplace=True)
books = books.reset_index()
books = books[['book_id','book_url','book_img','book_title','book_author','book_desc_text','book_desc_html']]

# Function to clean title
def clean_title(title):
    return re.sub("[^a-zA-Z0-9 ]", "", title)

# Convert string(sentence) to lists
books['temp_book_author'] = books['book_author']
books['temp_book_author'] = books['temp_book_author'].apply(clean_title)
books['temp_book_author'] = books['temp_book_author'].apply(lambda x: x.split())
books['temp_title'] = books['book_title']
books['temp_title'] = books['temp_title'].apply(clean_title)
books['temp_title'] = books['temp_title'].apply(lambda x: x.split())

###
###
###

# Recommendation function
# The ultimate concatenation
books['tags'] = books['temp_title'] + books['temp_book_author']

# Converting tags from lists to strings
books['tags'] = books['tags'].apply(lambda x: " ".join(x))
books['tags'] = books['tags'].str.lower()

# Using CountVectorizer for vectorization
cv = CountVectorizer(max_features=2000, stop_words='english')
vectors = cv.fit_transform(books['tags']).toarray()

# Using cosine similarity for finding distance between vectors
similarity = cosine_similarity(vectors)

# Final logic for recommendation
def recommend_books(keyword):
    keyword_vector = cv.transform([keyword]).toarray()
    similarity_scores = cosine_similarity(keyword_vector, vectors)[0]
    top_indices = similarity_scores.argsort()[::-1][:10]
    
    recommended_books_list = []   # list bcz it returns list of dictionaries
    for idx in top_indices:
        book_details = {
            'book_id': books.iloc[idx]['book_id'],
            'book_url': books.iloc[idx]['book_url'],
            'book_img': books.iloc[idx]['book_img'],
            'book_title': books.iloc[idx]['book_title'],
            'book_author': books.iloc[idx]['book_author'],
            'book_desc_text': books.iloc[idx]['book_desc_text'],
            'book_desc_html': books.iloc[idx]['book_desc_html']
        }
        recommended_books_list.append(book_details)
    
    return recommended_books_list

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

def get_personalized_book_recommendations(email):
    try:
        # Find the user data based on the username
        user_data = user_collection.find_one({'email': email})

        if not user_data:
            return "Username not found"
        
        # Extract interests from the user data
        interests = user_data.get('interests', [])

        # Initialize array to store personalized recommendations
        personalized_book_recommendations_list = []

        # Pass each interest keyword to the recommend function and add recommended books to the array
        for interest in interests:
            recommended_books = recommend_books(interest) 
            for book in recommended_books[:5]:  # Add top 5 recommended books for each interest
                personalized_book_recommendations_list.append(book)

        # Shuffle the list of personalized recommendations
        shuffle(personalized_book_recommendations_list)

        return personalized_book_recommendations_list
    except Exception as e:
        print("Error occurred while fetching personalized recommendations:", e)
        return "An error occurred while fetching personalized recommendations"

###
###
###

# Search Books function
def search_books(keyword):
    result_books = books[books['tags'].str.contains(keyword, case=False)]

    result_books_list = []
    for idx, book in result_books.iterrows():
        book_details = {
            'book_id': book['book_id'],
            'book_url': book['book_url'],
            'book_img': book['book_img'],
            'book_title': book['book_title'],
            'book_author': book['book_author'],
            'book_desc_text': book['book_desc_text'],
            'book_desc_html': book['book_desc_html']
        }
        result_books_list.append(book_details)
    
    return result_books_list

###
###
###

# Book Details Function
def getBook(title):
    book_data = books[books['book_title'] == title]

    if book_data.empty:
        return None
    else:
        book_data = book_data.iloc[0]
        book_details = {
            'book_id': book_data['book_id'],
            'book_url': book_data['book_url'],
            'book_img': book_data['book_img'],
            'book_title': book_data['book_title'],
            'book_author': book_data['book_author'],
            'book_desc_text': book_data['book_desc_text'],
            'book_desc_html': book_data['book_desc_html']
        }
        return book_details
