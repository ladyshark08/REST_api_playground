import flask
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from random import randint
from flask import jsonify
import sqlalchemy as sa
from random import choice

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random", methods=['GET', 'POST'])
def random():
    cafes = db.session.scalars(sa.select(Cafe)).all()
    result = choice(cafes).to_dict()
    f_result = {"cafe": result}
    return flask.jsonify(f_result)


@app.route("/all")
def all_cafes():
    cafes = db.session.scalars(sa.select(Cafe)).all()
    result = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=result)


@app.route('/search')
def search():
    loc = request.args.get('loc')
    cafes = db.session.scalars(sa.select(Cafe).where(Cafe.location == loc)).all()
    if cafes:
        result = {cafe.name: cafe.to_dict() for cafe in cafes}
        return jsonify(result)
    cant_find = {'Not Found': "Sorry, we don't have a cafe at that location."}
    return jsonify(error=cant_find)


@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    map_url = request.form.get('map_url')
    img_url = request.form.get('img_url')
    location = request.form.get('location')
    seats = request.args.get('seats')
    has_toilet = request.args.get('has_toilet')
    has_wifi = request.args.get('has_wifi')
    has_sockets = request.args.get('has_sockets')
    can_take_calls = request.args.get('can_take_calls')
    coffee_price = request.args.get('coffee_price')
    new_cafe = Cafe(name=name, map_url=map_url, img_url=img_url, location=location, seats=seats, has_toilet=has_toilet,
                    has_wifi=has_wifi, has_sockets=has_sockets, can_take_calls=can_take_calls, coffee_price=coffee_price)
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={'success': 'successfully added'})


@app.route('/update_price/<cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify(response={'success': 'successfully updated the price'})
    return jsonify(error={'not found': "sorry no cafe with that id"}), 404


@app.route('/report_closed/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    if request.args.get('api_key') != 'TopSecretAPIKey':
        return jsonify({'error': "You have the wrong API key"}), 401
    cafe_to_delete = db.session.scalar(sa.select(Cafe).where(Cafe.id == cafe_id))
    if cafe_to_delete is None:
        return jsonify(error={'not found': "sorry no cafe with that id"}), 404
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return jsonify(response={'success': 'successfully removed'})



# # HTTP GET - Read Record
#
# # HTTP POST - Create Record
#
# # HTTP PUT/PATCH - Update Record
#
# # HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
