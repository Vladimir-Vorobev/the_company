# -*- coding: utf-8 -*-
import hashlib
from flask import jsonify
import json
from datetime import datetime
from dateutil.parser import parse

from server_setup import users, game_info


class helpful_functions:
    @staticmethod
    def modify_word(nick):
        nick = nick.replace('e', 'е')
        nick = nick.replace('E', 'Е')
        nick = nick.replace('T', 'Т')
        nick = nick.replace('y', 'у')
        nick = nick.replace('I', 'I')
        nick = nick.replace('І', 'I')
        nick = nick.replace('і', 'i')
        nick = nick.replace('o', 'о')
        nick = nick.replace('O', 'О')
        nick = nick.replace('p', 'р')
        nick = nick.replace('P', 'Р')
        nick = nick.replace('x', 'х')
        nick = nick.replace('X', 'Х')
        nick = nick.replace('a', 'а')
        nick = nick.replace('A', 'А')
        nick = nick.replace('H', 'Н')
        nick = nick.replace('K', 'К')
        nick = nick.replace('c', 'с')
        nick = nick.replace('C', 'С')
        nick = nick.replace('B', 'В')
        nick = nick.replace('M', 'М')
        return nick.strip()

    def check_session_id(self, data):
        nick = self.modify_word(data['nick'])
        user = users.find_one({'nick': nick})
        if not user:
            print(0)
            return False
        session_id, salt = user['session_id'].split(':')
        if user and session_id == hashlib.sha512(salt.encode() + data['session_id'].encode()).hexdigest():
            return True
        else:
            print(1)
            return False

    @staticmethod
    def get_statistics(data):
        data = dict(json.loads(data))
        user = users.find_one({
            "nick": data['nick']
        })
        if not user:
            return jsonify('incorrect_email')
        if user['role'] not in ['developer']:
            return jsonify('permission_denied')
        password, salt = user['password'].split(':')
        if password != hashlib.sha512(salt.encode() + data['password'].encode()).hexdigest():
            return jsonify('incorrect_password')
        info_game = game_info.find_one()
        del info_game['_id']
        statistics = {
            'total_users_num': users.find().count(),
            'online_users_num': users.find({'is_online': True}).count(),
            'offline_users_num': users.find({'is_online': False}).count(),
            'users_game_counter_sum': 0,
            'total_game_counter': game_info.find_one()['total_game_counter'],
            'visitors_1': 0,
            'visitors_3': 0,
            'visitors_7': 0,
            'visitors_30': 0,
            'game_info': info_game,
            'developers': {},
        }
        for user in users.find():
            statistics['users_game_counter_sum'] += user['statistics']['game_counter']
            if (datetime.utcnow() - parse(user['last_seen'])).total_seconds() <= 86400:
                statistics['visitors_1'] += 1
                statistics['visitors_3'] += 1
                statistics['visitors_7'] += 1
                statistics['visitors_30'] += 1
            elif (datetime.utcnow() - parse(user['last_seen'])).total_seconds() <= 259200:
                statistics['visitors_3'] += 1
                statistics['visitors_7'] += 1
                statistics['visitors_30'] += 1
            elif (datetime.utcnow() - parse(user['last_seen'])).total_seconds() <= 604800:
                statistics['visitors_7'] += 1
                statistics['visitors_30'] += 1
            elif (datetime.utcnow() - parse(user['last_seen'])).total_seconds() <= 2592000:
                statistics['visitors_30'] += 1
        for user in users.find({'role': 'developer'}):
            statistics['developers'][user['nick']] = user['admin_effectivity']
        return jsonify(statistics)


hf = helpful_functions()
