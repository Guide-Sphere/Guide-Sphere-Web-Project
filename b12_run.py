from flask import Flask, url_for, render_template, request, flash, redirect
from werkzeug.utils import secure_filename
import os
from flask import Blueprint
from flask_cors import CORS
from functools import wraps
from b12_youtube_methods import recommend_yts
from b12_youtube_methods import get_recent_yts
from b12_youtube_methods import get_personalized_yt_recommendations
from b12_youtube_methods import search_yts
from b12_youtube_methods import getYt
from b12_books_methods import recommend_books
from b12_books_methods import search_books
from b12_books_methods import getBook
from b12_books_methods import get_personalized_book_recommendations
from b12_websites_methods import recommend_websites
from b12_websites_methods import search_websites
from b12_websites_methods import get_personalized_websites_recommendations
from userdata_methods import getuserdata    
from userdata_methods import insert_user_fullName
from userdata_methods import insert_user_moreAboutUser
from userdata_methods import insert_user_userPhoto
from userdata_methods import insert_user_interests
from userdata_methods import delete_user_interests
from userdata_methods import insert_user_education
from userdata_methods import delete_user_education
from userdata_methods import store_and_check

# Define a blueprint for searchyts model
searchyts_bp = Blueprint('searchyts', __name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define a global variable to store the email
email = None

# Wrapper function to set the email value only once
def set_email_once(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global email
        if email is None:
            email = request.args.get('email')
        return func(*args, **kwargs)
    return wrapper

app = Flask(__name__)

@app.route('/before12th')
@set_email_once
def b12_homepage():
    recent_yts = get_recent_yts()
    personalized_yt_recommendations = get_personalized_yt_recommendations(email)
    trending_books = recommend_books("English")
    recommended_websites = recommend_websites("Real Number")
    return render_template('b12_homepage.html', recent_yts_list=recent_yts, trending_books_list=trending_books,
                           personalized_yt_recommendations_list=personalized_yt_recommendations, 
                           recommended_websites_list=recommended_websites)

@app.route('/b12_ytsearchpage')
def b12_ytsearchpage():
    recent_yts = get_recent_yts()
    personalized_yt_recommendations = get_personalized_yt_recommendations(email)
    real_numbers_yts = recommend_yts("Real Numbers")
    ecology_yts = recommend_yts("Ecology")
    electricity_yts = recommend_yts("Electricity")
    return render_template('b12_ytsearchpage.html', recent_yts_list=recent_yts,
                           personalized_yt_recommendations_list=personalized_yt_recommendations,
                           real_numbers_yts_list=real_numbers_yts, ecology_yts_list=ecology_yts,
                           electricity_yts_list=electricity_yts)

@app.route('/b12_booksearchpage')
def b12_booksearchpage():
    personalized_book_recommendations = get_personalized_book_recommendations(email)
    english_books = recommend_books("English")
    hindi_books = recommend_books("Hindi")
    kannada_books = recommend_books("Kannada")
    return render_template('b12_booksearchpage.html', personalized_book_recommendations_list = personalized_book_recommendations,
                            english_books_list = english_books,hindi_books_list = hindi_books, kannada_books_list = kannada_books)

@app.route('/b12_websearchpage')
def b12_websearchpage():
    personalized_website_recommendations = get_personalized_websites_recommendations(email)
    byjus_websites = recommend_websites("byjus")
    vedantu_websites = recommend_websites("Vedantu")
    physics_wallah_websites = recommend_websites("Physics Wallah")
    gfg_websites = recommend_websites("GeeksforGeeks")
    return render_template('b12_websearchpage.html',personalized_website_recommendations_list = personalized_website_recommendations,
                           byjus_websites_list = byjus_websites, vedantu_websites_list = vedantu_websites,
                           physics_wallah_websites_list = physics_wallah_websites, gfg_websites_list = gfg_websites)

@app.route('/b12_searchresults', methods=['GET'])
def b12_searchresults():
    if request.method == 'GET':
        pageid = request.args.get('pageid')
        keyword = request.args.get('keyword')
        if pageid == '1':
            result_yts = search_yts(keyword)
            results = result_yts
        elif pageid == '2':
            result_books = search_books(keyword)
            results = result_books
        elif pageid == '3':
            result_websites = search_websites(keyword)
            results = result_websites

        store_and_check(email,keyword)

        return render_template('b12_searchresults.html', pageid=pageid, keyword=keyword, results_list=results)

    return render_template('b12_searchresults.html')

@app.route('/b12_ytdetailspage/<title>', methods=['GET'])
def b12_ytdetailspage(title):
    youtube = getYt(title)
    similar_yts = recommend_yts(title)
    similar_books = recommend_books(title)
    similar_websites = recommend_websites(title)
    return render_template('b12_ytdetailspage.html', youtube=youtube, similar_yts_list=similar_yts,
                           similar_books_list=similar_books, similar_websites_list=similar_websites)

@app.route('/b12_bookdetailspage/<title>', methods=['GET'])
def b12_bookdetailspage(title):
    book = getBook(title)
    similar_books = recommend_books(title)
    similar_websites = recommend_websites(title)
    return render_template('b12_bookdetailspage.html', book=book, similar_books_list=similar_books,
                           similar_websites_list=similar_websites)

@app.route('/b12_homepagesearchresults', methods=['GET'])
def b12_homepagesearchresults():
    if request.method == 'GET':
        keyword = request.args.get('keyword')
        home_result_yts = search_yts(keyword)
        home_result_books = search_books(keyword)
        home_result_webs = search_websites(keyword)
        store_and_check(email,keyword)
        return render_template('b12_homepagesearchresults.html', keyword=keyword, home_result_yts_list=home_result_yts,
                            home_result_books_list=home_result_books, home_result_webs_list=home_result_webs)
    
    return render_template('b12_homepagesearchresults.html')

UPLOAD_FOLDER = r'D:\Coding\Guide-Sphere-Web-Project-master\Guide-Sphere-Web-Project-master\static\uploads'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSTIONS = set (['png','jpg','jpeg','gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSTIONS


@app.route('/b12_myprofilepage/<section>', methods=['GET', 'POST'])
def b12_myprofilepage(section):
    if request.method == 'POST':
        if section == 'userPhotoDetails':
            # Handle user photo details
            if 'userPhoto' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['userPhoto']
            if file.filename == '':
                flash('No image selected for uploading')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                insert_user_userPhoto(email, filename)
                flash('Successfully uploaded')
            else:
                flash('Allowed image types are - png, jpg, jpeg, gif')
                return redirect(request.url)

        elif section == 'basicDetails':
            fullName = request.form.get('fullName')
            insert_user_fullName(email, fullName)
            flash('Basic details saved successfully!')

        elif section == 'interestsDetails':
            interests = request.form.get('interests')
            insert_user_interests(email, interests)
            flash('Interests saved successfully!')

        elif section == 'deleteinterestsDetails':
            selected_interests = request.form.getlist('selected_interests[]')
            delete_user_interests(email, selected_interests)
            flash('Selected interests deleted successfully!')

        elif section == 'moreAboutUserDetails':
            moreAboutUser = request.form.get('moreAboutUser')
            insert_user_moreAboutUser(email, moreAboutUser)
            flash('More about user details saved successfully!')

        elif section == 'educationDetails':
            collegeName = request.form.get('collegeName')
            specialization = request.form.get('specialization')
            grade = request.form.get('grade')
            insert_user_education(email, collegeName, specialization, grade)
            flash('Education details saved successfully!')

        elif section == 'deleteducationDetails':
            selected_education = request.form.getlist('selected_education[]')
            delete_user_education(email, selected_education)
            flash('Selected education details deleted successfully!')

        # Redirect to the same page using GET method
        return redirect(url_for('b12_myprofilepage', section=section))

    user = getuserdata(email)
    return render_template('b12_myprofilepage.html', user=user)

if __name__ == '__main__':
    app.run(port=5001, debug=True)










