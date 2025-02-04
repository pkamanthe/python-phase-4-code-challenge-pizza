#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os
from flask_cors import CORS

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class RestaurantsResource(Resource):
    def get(self):
        """Fetch all restaurants without restaurant_pizzas field"""
        restaurants = Restaurant.query.all()
        return jsonify([{
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address
        } for restaurant in restaurants])

class RestaurantResource(Resource):
    def get(self, id):
        """Fetch a single restaurant by ID"""
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return jsonify(restaurant.to_dict())
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

    def delete(self, id):
        """Delete a restaurant by ID"""
        restaurant = Restaurant.query.get(id)
        if restaurant:
            # Delete associated restaurant_pizzas
            for rp in restaurant.restaurant_pizzas:
                db.session.delete(rp)
            db.session.delete(restaurant)
            db.session.commit()
            return make_response("", 204)
        return make_response(jsonify({"error": "Restaurant not found"}), 404)

class PizzasResource(Resource):
    def get(self):
        """Fetch all pizzas without restaurant_pizzas field"""
        pizzas = Pizza.query.all()
        return jsonify([{
            'id': pizza.id,
            'name': pizza.name,
            'ingredients': pizza.ingredients
        } for pizza in pizzas])

class RestaurantPizzasResource(Resource):
    def post(self):
        """Create a new restaurant_pizza"""
        data = request.get_json()

        price = data.get("price")
        if price < 1 or price > 30:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        try:
            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
        except Exception as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

api.add_resource(RestaurantsResource, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)