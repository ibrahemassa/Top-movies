from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
Bootstrap5(app)
db = SQLAlchemy()
db.init_app(app)

URL = f"https://api.themoviedb.org/3/search/movie"
ID_URL = 'https://api.themoviedb.org/3/movie/movie_id'
MOVIE_DB_API_KEY = 'ec2fbc7be44b0a6b68fbb467dbd4391c'

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlYzJmYmM3YmU0NGIwYTZiNjhmYmI0NjdkYmQ0MzkxYyIsInN1YiI6IjY0ZjE4NGZhZWJiOTlkMDEzYmNmMjdiNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.5mJD8XUgvqUp2hpAbarjv_fm7vDLibtZnHn7ZvsxOYY"
}

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    description = db.Column(db.String(500), unique=False, nullable=False)
    rating = db.Column(db.Float, unique=False, nullable=True)
    ranking = db.Column(db.Integer, unique=False, nullable=True)
    review = db.Column(db.String, unique=False, nullable=True)
    img_url = db.Column(db.String, unique=False, nullable=False)


class EditForm(FlaskForm):
    new_review = StringField('Your Review')
    new_rating = StringField('Your Rating Out of 10')
    submit = SubmitField('Submit')


class AddMovie(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


with app.app_context():
    db.create_all()

# with app.app_context():
#     db.session.add(second_movie)
#     db.session.commit()


@app.route("/")
def home():
    all_movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()
    rank = 1
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit(id):
    form = EditForm()
    movie = db.session.execute(db.select(Movie).where(Movie.id == id)).scalar()
    if form.validate_on_submit():
        if form.new_review.data != '':
            movie.review = form.new_review.data
        movie.rating = form.new_rating.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie=movie)


@app.route('/delete/<id>')
def delete(id):
    movie = db.session.execute(db.select(Movie).where(Movie.id == id)).scalar()
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
def add():
    form = AddMovie()
    parameters = {
        'query': form.name.data
    }
    if form.validate_on_submit():
        movie_title = form.name.data
        response = requests.get(URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", movies=data)
    return render_template('add.html', form=form)

@app.route('/add/<api_id>')
def add_db(api_id):
    url = f"https://api.themoviedb.org/3/movie/{api_id}?language=en-US"

    headers_id = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlYzJmYmM3YmU0NGIwYTZiNjhmYmI0NjdkYmQ0MzkxYyIsInN1YiI6IjY0ZjE4NGZhZWJiOTlkMDEzYmNmMjdiNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.5mJD8XUgvqUp2hpAbarjv_fm7vDLibtZnHn7ZvsxOYY"
    }

    response = requests.get(url, headers=headers_id)

    movie = response.json()
    print(movie)
    new_movie = Movie(
        title=movie['title'],
        year=movie['release_date'].split("-")[0],
        description=movie['overview'],
        rating=movie['vote_average'],
        ranking=0,
        review="My favourite character was the caller.",
        img_url=f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
