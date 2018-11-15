from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity, jwt_optional, fresh_jwt_required
from flask_restful import Resource, reqparse
from models.item import *


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price', type=float, required=True, help="This field cannot be blank!")
    parser.add_argument('store_id', type=int, required=True, help="Every item needs a store id!")

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        else:
            return {'Message': "Item '{}' is not found".format(name)}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"Message": "Item '{}' already exists".format(name)}

        data = Item.parser.parse_args()
        item = ItemModel(name, **data)
        try:
            item.save_to_db()
        except:
            return {"Message": "An internal error occurred"}, 500

        return item.json(), 201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {"Message": "You have to be an admin."}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message": "Item '{}' deleted.".format(name)}
        else:
            return {"Message": "Item '{}' doesn't exist".format(name)}

    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']

        item.save_to_db()
        return item.json()


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        if user_id:
            return {'items': items}, 200
        return {"Items": [item['name'] for item in items], 'Message': "More data available if you log in."}, 200




