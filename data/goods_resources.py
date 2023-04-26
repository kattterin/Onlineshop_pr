from flask import jsonify
from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.goods import Goods

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('price', required=True, type=int)
parser.add_argument('old_price', required=True, type=int)
parser.add_argument('in_stock', required=True, type=int)


class GoodsResource(Resource):
    def get(self, goods_id):
        abort_if_goods_not_found(goods_id)
        session = db_session.create_session()
        goods = session.query(Goods).get(goods_id)
        return jsonify({'goods': goods.to_dict(
            only=('title', 'content', 'user_id', 'price', "old_price", "in_stock"))})

    def delete(self, goods_id):
        abort_if_goods_not_found(goods_id)
        session = db_session.create_session()
        goods = session.query(Goods).get(goods_id)
        session.delete(goods)
        session.commit()
        return jsonify({'success': 'OK'})


class GoodsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        goods = session.query(Goods).all()
        return jsonify({'goods': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in goods]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        goods = Goods(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            price=args['price'],
            old_price=args['old_price'],
            in_stock=args['in_stock']
        )
        session.add(goods)
        session.commit()
        return jsonify({'success': 'OK'})


def abort_if_goods_not_found(goods_id):
    session = db_session.create_session()
    goods = session.query(Goods).get(goods_id)
    if not goods:
        abort(404, message=f"Goods {goods_id} not found")
