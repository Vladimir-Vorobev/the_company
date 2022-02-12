# -*- coding: utf-8 -*-
from flask_socketio import emit
from datetime import datetime
from operator import itemgetter

from server_setup import users, ratings
from modules import hf


class ratings_processing:
    @staticmethod
    def get_rating(data):
        if not hf.check_session_id(data):
            return
        rating = ratings.find_one({'name': data['name']})
        del rating['_id']
        emit('get_rating', rating)

    @staticmethod
    def update_rating(rating_type, reverse):
        data = []
        if rating_type not in ['min_game_time', 'max_game_time']:
            return
        for user in users.find().sort(f'statistics.{rating_type}', -1).limit(100):
            data.append({
                'nick': user['nick'],
                'user_id': user['user_id'],
                'avatar': user['avatar'],
                'score': user['statistics'][rating_type],
            })
        data.sort(key=itemgetter('score'), reverse=reverse)
        ratings.update_one({'name': rating_type}, {'$set': {'data': data}})


rap = ratings_processing()
