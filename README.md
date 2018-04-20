# SI 364 - Winter 2018 - Final Project


## App Description
This application allows users to register, sign in, and save movies that they searched on to their own account. The saved movies enables users to see the detailed information of the movies. Detailed information include: movie title, plot, rate, release date, movie runtime, and directors. Users can see all the movies they have saved as a list, but cannot see the lists that other users saved. Alternatively, users can also rate a movie with 5/5 being the highest rating possible and 1/5 being the lowest rating possible. If at any reason, users have changed their preference of a particular movie, they can update or delete movies that they have rated.
Based on the saved movies, users are able to see all movies searched, all movies rated, and all directors in the database.

## Motivation
Watching movies is a common type of entertainment for many. I am also a person that likes to watch movies. Sometimes, however, I just don't have the time to watch all of them. Therefore, I always wished there is a platform for me to save a list of movies to watch later or even just to look up some basic information of a particular movie. I can always save a list in my notes, but I may not remember what the movie is about after a period of time. In light of this, with a web application like this one, I will be able to see a saved list of movies each with basic information. This allows me to know what each movie is generally about without searching each movie on the web.

## Usage
Login and Registration: Upon opening the app, users will be prompted to sign in with Google if it is the first time they opened the app. Users may register for a new Google account or login to an existing one. After a successful sign in, users will then be redirected to the home page.

Navigation: On the home page, users may navigate through the functions of the app by clicking the links. Each link will navigate the users to the desired page they have clicked.

Search Movies: Users can search for existing movies by entering the title of the movie in the search field. Once the user clicks "Submit", relevant information of the movie will be returned and will be visible to the users if successful submission.

Rate Movies: Users can rate for movies by entering the title of the movie in the search field and rate the movie out of 5. Once the user clicks "Submit", an entry of the rating will be saved into the database and can be accessed by users whenever.

View All Movies: Users are able to view all of the movies that they have searched in chronological order from top to bottom.

View All Ratings: Users are able to view all of the movies that they have rated. The list is sorted by highest to lowest rating. Therefore, movies that have higher ratings will be on the top of the list, whereas movies that have lower ratings will be at the bottom.

Update or Delete Movie Ratings: Users are able to update or delete movie ratings if they wish to do so. To update a rating, users would have to click the hyperlink of the movie in order to update the rating. Users will get prompted a form that shows the selection of ratings that the users can choose from. In this app, all ratings are out of 5. To delete a rating, users would just simply click the "Delete" button on the list. Upon deletion, users will be redirected back to the page with all movie ratings.

View All Directors: Users are able to view all of the directors that has appeared on search queries.

## Modules
- os
- json
- datetime
- requests
- flask
- flask_sqlalchemy
- wtforms
- wtforms.validators
- requests_oauthlib
- requests.exceptions
- flask_migrate
- flask_script
- flask_wtf

## Routes
- /login --> Direct users to the login page.
- /gCallback --> Handles Google Oauth callback. After prompting the callback, it redirects users to the home page.
- /logout --> Directs users to the logout page.
- / --> Directs users to the homepage with all navigations.
- /movie --> Directs users to a page where they can search for existing movies.
- /all_movies --> Directs users to a page where they can see all the movies that have searched from past to present.
- /rating --> Directs users to a page where they can rate a movie out of 5.
- /all_ratings --> Directs users to a page where they can see all the movies they have rated. The list is sorted and ordered from highest to lowest rating.
- /list --> This page will get prompted only when users wish to update a movie they have rated.
- /update --> Directs users to a page where they can update the rating of a movie they rated. This page allows users to select a new rating out of 5. Upon successful update, it redirects users to the all ratings page.
- /delete --> Route that allows users to delete a movie they have rated. Upon successful delete, it redirects users to the all ratings page.
- /director --> Directs users to a page where they can view all the directors that has been saved in the database so far. Therefore, the visible directors are based on the movies that the users have searched in the past.

## Requirements

### **Documentation README Requirements**

- [x] Create a `README.md` file for your app that includes the full list of requirements from this page. The ones you have completed should be bolded or checked off. (You bold things in Markdown by using two asterisks, like this: `**This text would be bold** and this text would not be`)

- [x] The `README.md` file should use markdown formatting and be clear / easy to read.

- [x] The `README.md` file should include a 1-paragraph (brief OK) description of what your application does

- [x] The `README.md` file should include a detailed explanation of how a user can user the running application (e.g. log in and see what, be able to save what, enter what, search for what... Give us examples of data to enter if it's not obviously stated in the app UI!)

- [x] The `README.md` file should include a list of every module that must be installed with `pip` if it's something you installed that we didn't use in a class session. If there are none, you should note that there are no additional modules to install.

- [x] The `README.md` file should include a list of all of the routes that exist in the app and the names of the templates each one should render OR, if a route does not render a template, what it returns (e.g. `/form` -> `form.html`, like [the list we provided in the instructions for HW2](https://www.dropbox.com/s/3a83ykoz79tqn8r/Screenshot%202018-02-15%2013.27.52.png?dl=0) and like you had to on the midterm, or `/delete -> deletes a song and redirects to index page`, etc).

### **Code Requirements**

- [x] Ensure that your `SI364final.py` file has all the setup (`app.config` values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on `http://localhost:5000` (and the other routes you set up). **Your main file must be called** `SI364final.py`**, but of course you may include other files if you need.**

- [x] A user should be able to load `http://localhost:5000` and see the first page they ought to see on the application.

- [x] Include navigation in `base.html` with links (using `a href` tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, [like this](https://www.dropbox.com/s/hjcls4cfdkqwy84/Screenshot%202018-02-15%2013.26.32.png?dl=0) )

- [x] Ensure that all templates in the application inherit (using template inheritance, with `extends`) from `base.html` and include at least one additional `block`.

- [x] Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).

- [x] Must have data associated with a user and at least 2 routes besides `logout` that can only be seen by logged-in users.

- [x] At least 3 model classes *besides* the `User` class.

- [x] At least one one:many relationship that works properly built between 2 models.

- [x] At least one many:many relationship that works properly built between 2 models.

- [x] Successfully save data to each table.

- [x] Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).

- [x] At least one query of data using an `.all()` method and send the results of that query to a template.

- [x] At least one query of data using a `.filter_by(...` and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).

- [x] At least one helper function that is *not* a `get_or_create` function should be defined and invoked in the application.

- [x] At least two `get_or_create` functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).

- [x] At least one error handler for a 404 error and a corresponding template.

- [x] At least one error handler for any other error (pick one -- 500? 403?) and a corresponding template.

- [x] Include at least 4 template `.html` files in addition to the error handling template files.

- [x] At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.

- [x] At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that *does* accord with other involved sites' Terms of Service, etc).

- [x] Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source *to the database* (in some way).

- [x] At least one WTForm that sends data with a `GET` request to a *new* page.

- [x] At least one WTForm that sends data with a `POST` request to the *same* page. (NOT counting the login or registration forms provided for you in class.)

- [x] At least one WTForm that sends data with a `POST` request to a *new* page. (NOT counting the login or registration forms provided for you in class.)

- [x] At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.

- [x] Include at least one way to *update* items saved in the database in the application (like in HW5).

- [x] Include at least one way to *delete* items saved in the database in the application (also like in HW5).

- [x] Include at least one use of `redirect`.

- [x] Include at least two uses of `url_for`. (HINT: Likely you'll need to use this several times, really.)

- [x] Have at least 5 view functions that are not included with the code we have provided. (But you may have more! *Make sure you include ALL view functions in the app in the documentation and navigation as instructed above.*)

## Additional Requirements

- [ ] (100 points) Include a use of an AJAX request in your application that accesses and displays useful (for use of your application) data.
- [x]  (100 points) Create, run, and commit at least one migration.
- [ ] (100 points) Include file upload in your application and save/use the results of the file. (We did not explicitly learn this in class, but there is information available about it both online and in the Grinberg book.)
- [x]  (100 points) Deploy the application to the internet (Heroku) — only counts if it is up when we grade / you can show proof it is up at a URL and tell us what the URL is in the README. (Heroku deployment as we taught you is 100% free so this will not cost anything.)
- [x]  (100 points) Implement user sign-in with OAuth (from any other service), and include that you need a *specific-service* account in the README, in the same section as the list of modules that must be installed.
