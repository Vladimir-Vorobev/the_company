# -*- coding: utf-8 -*-
import json
import numpy as np
import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse

from server_setup import users, game_info
from modules import hf

statistics_shape = {
    'game_counter': 0,
    'online_game_counter': 0,
    'max_game_time': 0,
    'min_game_time': 0,
    'win_game': 0,
}


class authentification_precessing:
    def reg_in(self, data):
        data = dict(json.loads(data))
        nick = hf.modify_word(data['nick'].strip())
        salt = uuid.uuid4().hex
        if len(data['password']) < 7 or len(data['password']) > 20:
            return
        if len(nick) > 15 or len(nick) < 3 or [s for s in nick if s in '.[]{}()']:
            return
        if users.find_one({'nick': nick}):
            return 'incorrect_nick'
        users.insert_one({
            'nick': nick,
            'password': hashlib.sha512(salt.encode() + data['password'].encode()).hexdigest() + ':' + salt,
            'avatar': None,
            'company_name': 'Компания',
            'role': 'user',
            'user_id': self.make_user_id(),
            'session_id':
                hashlib.sha512(salt.encode() + self.make_session_id().encode()).hexdigest() + ':' + salt,
            'is_online': False,
            'last_seen': datetime.utcnow().isoformat(),
            'money': 0,
            'gold': 0,
            'exp': 0,
            'rang': 1,
            'premium_time': None,
            'statistics': statistics_shape,
            'reg_in_date': datetime.utcnow(),
            'sid': 'sid',
            'last_nick_update': datetime.utcnow(),
        })
        info_game = game_info.find_one()
        year = str(datetime.now(timezone(timedelta(hours=3))).year)
        month = str(datetime.now(timezone(timedelta(hours=3))).month)
        day = str(datetime.now(timezone(timedelta(hours=3))).day)
        hour = str(datetime.now(timezone(timedelta(hours=3))).hour)
        if year not in info_game['new_registrations']:
            info_game['new_registrations'][year] = {}
        if month not in info_game['new_registrations'][year]:
            info_game['new_registrations'][year][month] = {}
        if day not in info_game['new_registrations'][year][month]:
            info_game['new_registrations'][year][month][day] = {}
        if hour not in info_game['new_registrations'][year][month][day]:
            info_game['new_registrations'][year][month][day][hour] = 1
        else:
            info_game['new_registrations'][year][month][day][hour] += 1
        game_info.update_one({}, {'$set': {'new_registrations': info_game['new_registrations']}})
        return 'reg_in'

    def log_in(self, data):
        data = dict(json.loads(data))
        nick = hf.modify_word(data['nick'])
        if data['current_game_version'] != game_info.find_one()['game_version']:
            return 'incorrect_game_version'
        user = users.find_one({'nick': nick})
        if not user:
            return 'incorrect_nick'
        password, salt = user['password'].split(':')
        if password != hashlib.sha512(salt.encode() + data['password'].encode()).hexdigest():
            return 'incorrect_password'
        salt = uuid.uuid4().hex
        session_id = self.make_session_id()
        users.update_one(
            {'nick': nick},
            {
                '$set':
                    {
                        'session_id': hashlib.sha512(salt.encode() + session_id.encode()).hexdigest() + ':' + salt
                    }
            }
        )
        del user['_id']
        del user['password']
        user['session_id'] = session_id
        info_game = game_info.find_one()
        year = str(datetime.now(timezone(timedelta(hours=3))).year)
        month = str(datetime.now(timezone(timedelta(hours=3))).month)
        day = str(datetime.now(timezone(timedelta(hours=3))).day)
        hour = str(datetime.now(timezone(timedelta(hours=3))).hour)
        if str(((parse(user['last_seen'])) + timedelta(hours=3)).day) != day:
            if year not in info_game['unique_visitors']:
                info_game['unique_visitors'][year] = {}
            if month not in info_game['unique_visitors'][year]:
                info_game['unique_visitors'][year][month] = {}
            if day not in info_game['unique_visitors'][year][month]:
                info_game['unique_visitors'][year][month][day] = {}
            if hour not in info_game['unique_visitors'][year][month][day]:
                info_game['unique_visitors'][year][month][day][hour] = 1
            else:
                info_game['unique_visitors'][year][month][day][hour] += 1
            game_info.update_one({}, {'$set': {'unique_visitors': info_game['unique_visitors']}})
        if year not in info_game['visits']:
            info_game['visits'][year] = {}
        if month not in info_game['visits'][year]:
            info_game['visits'][year][month] = {}
        if day not in info_game['visits'][year][month]:
            info_game['visits'][year][month][day] = {}
        if hour not in info_game['visits'][year][month][day]:
            info_game['visits'][year][month][day][hour] = 1
        else:
            info_game['visits'][year][month][day][hour] += 1
        game_info.update_one({}, {'$set': {'visits': info_game['visits']}})
        return user

    @staticmethod
    def make_user_id():
        user = 1
        result = ''
        letters = '0123456789qwertyuiopasdfghjklzxcvbnm'
        maximum = len(letters)
        while user:
            result = ''
            for i in range(16):
                result += letters[np.random.randint(0, maximum)]
            user = users.find_one({
                "user_id": result
            })
        return result

    @staticmethod
    def make_session_id():
        result = ''
        letters = '0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
        maximum = len(letters)
        for i in range(128):
            result += letters[np.random.randint(0, maximum)]
        return result


ap = authentification_precessing()
