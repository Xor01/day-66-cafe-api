import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

## Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


## Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def get_random_cafe():
    random_cafe = random.choice(Cafe.query.all())
    return jsonify(Cafe.to_dict(random_cafe)), 200


@app.route('/all')
def get_all_cafes():
    all_cafes = Cafe.query.all()
    return jsonify(
        cafes=[cafe.to_dict() for cafe in all_cafes]
    ), 200


## HTTP GET - Read Record
@app.route('/search')
def get_cafe():
    loc = request.args.get('loc')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == loc)).scalars().all()
    if result:
        return jsonify(cafes=[cafe.to_dict() for cafe in result]), 200
    return jsonify(
        error={
            'Not Found': 'No Cafe was found at that location'
        }
    ), 404


## HTTP POST - Create Record
@app.route('/add', methods=['POST'])
def add_cafe():
    cafe_requested = request.form.to_dict()
    cafe = Cafe(
        name=cafe_requested['name'],
        map_url=cafe_requested['map_url'],
        img_url=cafe_requested['img_url'],
        location=cafe_requested['location'],
        seats=cafe_requested['seats'],
        has_toilet=True if cafe_requested['has_toilet'].lower() == 'true' else False,
        has_wifi=True if cafe_requested['has_wifi'].lower() == 'true' else False,
        has_sockets=True if cafe_requested['has_sockets'].lower() == 'true' else False,
        can_take_calls=True if cafe_requested['can_take_calls'].lower() == 'true' else False,
        coffee_price=True if cafe_requested['coffee_price'].lower() == 'true' else False,
    )
    try:
        db.session.add(cafe)
        db.session.commit()
        return jsonify(
            result={
                'Success': 'New Location has been added'
            }
        ), 201
    except Exception as e:
        print('[+] Console: ', e)
        return jsonify(
            error={
                'Failed to add new location': 'error on your data'
            }
        ), 400


## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def patch_coffee_price(cafe_id):
    if request.method == 'PATCH':
        try:
            new_coffee_price = request.args.get('coffee_price')
            if new_coffee_price.isnumeric():
                cafe = db.get_or_404(Cafe, cafe_id)
                cafe.coffee_price = request.args.get('coffee_price')
                db.session.commit()
                return jsonify(result={'Success': 'Coffee price has been updated'}), 200
            else:
                return jsonify(error={'Not a valid price'}), 304
        except Exception as e:
            print('[+] Console: ', e)
            return jsonify(error={'Error': 'Check your request'}), 304
    return jsonify(error={'Failure': 'Only PATCH method'}), 304

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
