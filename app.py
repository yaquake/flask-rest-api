import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.item import *
from db import db
from resources.store import Store, StoreList
from blacklist import BLACKLIST

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_SECRET_KEY'] = 'ivan'
api = Api(app)
db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)  # /auth


@jwt.user_claims_loader     # Adding additional arguments in a payload
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}


@jwt.token_in_blacklist_loader      # If the token in a blacklist
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


@jwt.expired_token_loader       # If the token is expired
def expired_token_callback():
    return jsonify({'Error', 'Token expired.'}), 401


@jwt.invalid_token_loader       # Something wrong in token
def invalid_token_callback(error):
    return jsonify({'Error': 'Invalid token formatto.'}), 401


@jwt.unauthorized_loader    # if we don't send a JWT at all
def missing_token_callback():
    return jsonify({"Error", "Request does not contain an access token"})


@jwt.needs_fresh_token_loader   # Needs a fresh token instead of non-fresh one
def token_not_fresh_callback():
    return jsonify({"Error": "The token is not fresh"})


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({"Error": "The token has been revoked"})


api.add_resource(Item, '/item/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, "/register")
api.add_resource(Store, '/store/<string:name>')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')


if __name__ == '__main__':
    app.run(debug=True)


