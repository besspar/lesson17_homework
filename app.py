# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
api = Api(app)

movies_ns = api.namespace("movies")
directors_ns = api.namespace("directors")
genres_ns = api.namespace("genres")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movies_ns.route("/")
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        data = Movie.query
        if director_id is not None:
            data = data.filter(Movie.director_id == director_id)
        if genre_id is not None:
            data = data.filter(Movie.genre_id == genre_id)
        if director_id is not None and genre_id is not None:
            data = data.filter(Movie.director_id == director_id, Movie.genre_id == genre_id)
        result = data.all()
        return movies_schema.dump(result), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movies_ns.route("/<int:mid>")
class MovieView(Resource):
    def get(self, mid):
        data = Movie.query.get(mid)

        if not data:
            return "", 404

        return movie_schema.dump(data), 200

    def delete(self, mid):
        data = Movie.query.get(mid)

        if not data:
            return "", 404

        db.session.delete(data)
        db.session.commit()
        return "", 204


@directors_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        all_directors = Director.query.all()
        return directors_schema.dump(all_directors)

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)

        with db.session.begin():
            db.session.add(new_director)

        return "", 201


@directors_ns.route("/<int:did>")
class DirectorsView(Resource):
    def get(self, did):
        data = Director.query.get(did)

        if not data:
            return "", 404

        return director_schema.dump(data), 200

    def put(self, did):
        data = Director.query.get(did)
        req_json = request.json
        data.name = req_json.get("name")
        db.session.add(data)
        db.session.commit()
        return "", 204

    def delete(self, did):
        data = Director.query.get(did)

        if not data:
            return "", 404

        db.session.delete(data)
        db.session.commit()
        return "", 204


@genres_ns.route("/")
class GenresView(Resource):
    def get(self):
        all_genres = Genre.query.all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Movie(**req_json) # Можно было бы еще добавить проверку, что такого жанра нет

        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genres_ns.route("/<int:gid>")
class GenresView(Resource):
    def get(self, gid):
        data = Genre.query.get(gid)

        if not data:
            return "", 404

        return genre_schema.dump(data), 200

    def put(self, gid):
        data = Genre.query.get(gid)
        req_json = request.json
        data.name = req_json.get("name")
        db.session.add(data)
        db.session.commit()
        return "", 204

    def delete(self, gid):
        data = Genre.query.get(gid)

        if not data:
            return "", 404

        db.session.delete(data)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
