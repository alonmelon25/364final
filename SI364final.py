import os
import json
import datetime
import requests

import pdb

from flask import Flask, url_for, redirect, render_template, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, RadioField
from wtforms.validators import Required, Length
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from flask_wtf import FlaskForm

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # In order to use both http and https
basedir = os.path.abspath(os.path.dirname(__file__))

"""App Configuration"""
class Auth:
    """Google Project Credentials"""
    CLIENT_ID = ('577377604559-ahjtaggn4n3p34khm8i4s3pj48rvnpo7.apps.googleusercontent.com')
    CLIENT_SECRET = '-bV72mkDet0QAktCxMiTtGZE'
    REDIRECT_URI = 'http://localhost:5000/gCallback'
    # URIs determined by Google, below
    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']

class Config:
    """Base config"""
    APP_NAME = "Test Google Login"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "something secret"


class DevConfig(Config):
    """Dev config"""
    DEBUG = True
    USE_RELOADER = True
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/proaaronSI364final"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


class ProdConfig(Config):
    """Production config"""
    DEBUG = False
    USE_RELOADER = True
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/SI364final_prod"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

# To set up different configurations for development of an application
config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}

"""APP creation and configuration"""
app = Flask(__name__)
app.config.from_object(config['dev']) # Here's where we specify which configuration is being used for THIS Flask application instance, stored in variable app, as usual!
app.config['HEROKU_ON'] = os.environ.get('HEROKU') # Heroku
db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.session_protection = "strong" # New - because using sessions with oauth instead of our own auth verification

###################
#### API Setup ####
###################
## Helper function
def get_movie_info(title):
    url = 'http://www.omdbapi.com/?apikey=9d267298&'
    # img = 'http://img.omdbapi.com/?apikey=9d267298&'
    params = {'t': title}
    r = requests.get(url, params = params).json()
    return r

##################
##### MODELS #####
##################
# Association table
# Many to many relationship - directors can have many movies and vice versa
movie_director = db.Table('movie_director', db.Column('movie_id', db.Integer, db.ForeignKey('movies.id')), db.Column('director_id', db.Integer, db.ForeignKey('directors.id')))

class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    plot = db.Column(db.String())
    rated = db.Column(db.String(16))
    released = db.Column(db.String(16))
    runtime = db.Column(db.String(16))
    genre = db.Column(db.String(64))
    director = db.Column(db.String(256))
    directors = db.relationship('Director', secondary=movie_director, backref=db.backref('Movie',lazy='dynamic'),lazy='dynamic')
    ratings = db.relationship('Rating', backref='Movie')
    # This model contains the movie attributes such as the title, year of release, genre, director, etc.

class Director(db.Model):
    __tablename__ = "directors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    # This model contains the movie directors

class Rating(db.Model):
    __tablename__ = "ratings"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    rating = db.Column(db.Integer)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id')) # One to many relationship - one rating, many movies
    # This model contains the movie ratings

class User(db.Model, UserMixin):
    __tablename__ = "users" # This was built to go with Google specific auth
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(16))
    avatar = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

## IMPORTANT FUNCTION / MANAGEMENT
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


""" OAuth Session creation """
def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth

###################
###### FORMS ######
###################
class MovieForm(FlaskForm):
    # Form that asks users to enter movie title in order to search a movie
    title = StringField("Enter name of movie:", validators= [Required(), Length(1,128)])
    submit = SubmitField()

class RatingForm(FlaskForm):
    # Form that asks users to rate movies
    title = StringField("Enter name of movie:", validators=[Required(), Length(1,128)])
    rating_selection = RadioField("Select rating for movie", choices= [('1', '1'),
    ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], validators= [Required()])
    submit = SubmitField()

class UpdateButtonForm(FlaskForm):
    submit = SubmitField("Update")

class UpdateRatingForm(FlaskForm):
    rating_update = RadioField("Select rating for movie", choices= [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], validators= [Required()])
    submit = SubmitField("Update")

class DeleteButtonForm(FlaskForm):
    submit = SubmitField("Delete")

#############################
######## HELPER FXNS ########
#############################
def get_or_create_movie(title, plot, rated, released, runtime, genre, director_name):
    # Always returns a movie instance
    movie = Movie.query.filter_by(title=title, plot=plot, rated=rated, released=released,
    runtime=runtime, genre=genre, director=director_name).first()
    if movie:
        return movie
    else:
        movie_entry = Movie(title=title, plot=plot, rated=rated, released=released,
        runtime=runtime, genre=genre, director=director_name)
        response = get_movie_info(title)
        director = response['Director'].split(',')
        for d in director:
            #pdb.set_trace()
            d = get_or_create_director(d)
            movie_entry.directors.append(d)
        db.session.add(movie_entry)
        db.session.commit()
        return movie_entry

def get_or_create_director(name):
    # Always returns a director instance
    director = Director.query.filter_by(name=name).first()
    if director:
        return director
    else:
        director_entry = Director(name=name)
        db.session.add(director_entry)
        db.session.commit()
        return director_entry

def get_or_create_rating(title, rating):
    # Always returns a rating instance
    rating = Rating.query.filter_by(title=title, rating=rating, movie_id=get_or_create_movie(title, plot, rated, released, runtime, genre, director, name).id).first()
    if rating:
        return rating
    else:
        rating_entry = Rating(title=title, rating=rating, movie_id=get_or_create_movie(title, plot, rated, released, runtime, genre, director, name).id)
        db.session.add(rating_entry)
        db.session.commit()
        return rating_entry

##########################
###### LOGIN ROUTES ######
##########################
@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('login.html', auth_url=auth_url)
    # Route for users to login

@app.route('/gCallback')
def callback():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    # print(request.args, "ARGS")
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            # print("SUCCESS 200") # For debugging/understanding
            user_data = resp.json()
            email = user_data['email']
            user = User.query.filter_by(email=email).first()
            if user is None:
                # print("No user...")
                user = User()
                user.email = email
            user.name = user_data['name']
            # print(token)
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))
        return 'Could not fetch your information.'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
    # Route for users to logout
    # Route is login required because users cannot logout without logging in

#######################
###### VIEW FXNS ######
#######################
@app.route('/')
@login_required
def index():
    # This function will display the home page of the web application and will only be available to users who have an account.
    # It will show a welcome screen with a navigation of all the functions that will be available in the app
    # Each navigation will be treated as a hyperlink in order to click in to each function
    return render_template('base.html')

@app.route('/movie', methods= ['GET','POST'])
def movie():
    # Prompts MovieForm
    # If form validate_on_submit, retrieve title and movie. However, if is movie never entered into the database, create new entry by retriving movie information from the API
    # When the form is submitted, should redirect to the same page with the empty form; if not, leads users back to the form where they originally started.
    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data
        movie = Movie.query.filter_by(title=title).first()
        if movie == None:
            movie_info = get_movie_info(title)
            title = movie_info['Title']
            plot = movie_info['Plot']
            rated = movie_info['Rated']
            released = movie_info['Released']
            runtime = movie_info['Runtime']
            genre = movie_info['Genre']
            director = movie_info['Director']
            # Create object
            movie_entry = get_or_create_movie(title, plot, rated, released, runtime, genre, director)
            # Save entry
            db.session.add(movie_entry)
            # Commit
            db.session.commit()
        else:
            title = movie.title
            plot = movie.plot
            rated = movie.rated
            released = movie.released
            runtime = movie.runtime
            genre = movie.genre
            director = movie.director
        return render_template('movie_info.html', title=title, plot=plot, rated=rated,
        released=released, runtime=runtime, genre=genre, director=director)
    return render_template('search_movie.html', form=form)

@app.route('/all_movies')
def all_movies():
    movies = Movie.query.all()
    return render_template('all_movies.html', movies=movies)
    # Allows users to view all movies.
    # The list is created by the users. Therefore, it can only be seen by the logged in user. Other users cannot see the list.

@app.route('/rating', methods= ['GET','POST'])
def rating():
    # Prompts RatingForm
    # If form validate_on_submit, proceeds to the nested if loop.
    # If user has entered movie that is new to the database, retrieves movie information from the API. After adding it to the database, the rating gets added with the corresponding movie.
    # When the form is submitted, should redirect to the same page with the empty form; if not, leads users back to the form where they originally started.
    form = RatingForm()
    if form.validate_on_submit():
        title = form.title.data
        rating_selection = form.rating_selection.data
        rating = Rating.query.filter_by(title=title, rating=rating_selection).first()
        movie = Movie.query.filter_by(title=title).first()
        if not movie:
            movie_info = get_movie_info(title)
            title = movie_info['Title']
            plot = movie_info['Plot']
            rated = movie_info['Rated']
            released = movie_info['Released']
            runtime = movie_info['Runtime']
            genre = movie_info['Genre']
            director = movie_info['Director']
            # Create object
            movie = get_or_create_movie(title, plot, rated, released, runtime, genre, director)
            # Save entry
            db.session.add(movie)
            # Commit
            db.session.commit()
        if not rating:
            rating = Rating(title=title, rating=rating_selection, movie_id=movie.id)
            db.session.add(rating)
            db.session.commit()
        flash("Entry successfully added!")
        return render_template('rating_info.html', title=rating.title, rating=rating.rating, movie_id=rating.id)
    return render_template('rating_entry.html', form=form)

@app.route('/all_ratings')
def all_ratings():
    form = DeleteButtonForm()
    ratings = Rating.query.all()
    # Order from highest rating to lowest
    ratings = sorted(ratings, key = lambda r: r.rating, reverse=True)
    return render_template('all_ratings.html', form=form, ratings=ratings)
    # Allows users to view all movies with movies that the users have rated

@app.route('/list/<i>',methods=["GET","POST"])
def mov_list(i):
    form = UpdateButtonForm()
    mov = Movie.query.filter_by(id=i).first()
    dirs = mov.directors.all()
    return render_template('movie_list.html', form=form, mov=mov, dirs=dirs)

@app.route('/update/<title>',methods=["GET","POST"])
def update(title):
    form = UpdateRatingForm()
    r = Rating.query.filter_by(title=title).first()
    if form.validate_on_submit():
        rating_update = form.rating_update.data
        r.rating = rating_update
        db.session.commit()
        # flash('Successfully updated priority of {}'.format(movie.title))
        return redirect(url_for('all_ratings'))
    return render_template('rating_update.html', form=form, title=title)

@app.route('/delete/<item>',methods=["GET","POST"])
def delete(item):
    r = Rating.query.filter_by(id=item).first()
    db.session.delete(r)
    db.session.commit()
    # flash("Successfully deleted: {}".format(m.title))
    return redirect(url_for('all_ratings'))

@app.route('/director', methods= ['GET','POST'])
def director():
    directors = Director.query.filter_by()
    return render_template('all_directors.html', directors=directors)

###################################
###### ERROR HANDLING ROUTES ######
###################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    db.create_all() # Will create any defined models when running the application
    manager.run() # Allows the web application to run and debug when there are errors
