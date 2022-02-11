# -*- coding: utf-8 -*-
from flask_socketio import emit
from datetime import datetime
import hashlib
import uuid

from server_setup import users
from modules import hf

max_image_len = 1048576 / 2


class user_processing:
    @staticmethod
    def get_profile(data):
        if not hf.check_session_id(data):
            return
        if 'info_nick' not in data:
            user = users.find_one({'user_id': data['info_user_id']})
            data['info_nick'] = user['nick']
        else:
            user = users.find_one({'nick': data['info_nick']})
        if not user:
            return
        if data['nick'] != data['info_nick']:
            del user['money']
            del user['gold']
        del user['_id']
        del user['password']
        del user['session_id']
        del user['sid']
        emit('get_profile', user)

    @staticmethod
    def edit_profile(data):
        if not hf.check_session_id(data):
            return
        user = users.find_one({'nick': data['nick']})
        update_data = {}
        if 'avatar' in data:
            if len(data['avatar'].encode('utf-8')) > max_image_len:
                return
            update_data['avatar'] = data['avatar']
        if 'new_password' in data:
            if len(data['new_password']) < 7 or len(data['new_password']) > 20:
                return
            password, salt = user['password'].split(':')
            if password != hashlib.sha512(salt.encode() + data['password'].encode()).hexdigest():
                emit('edit_profile', {'status': 'incorrect_password'})
                return
            salt = uuid.uuid4().hex
            update_data['password'] = hashlib.sha512(salt.encode() + data['new_password'].encode()).hexdigest() + ':' + salt
        if 'new_nick' in data:
            new_nick = hf.modify_word(data['new_nick'])
            if len(new_nick) > 15 or len(new_nick) < 3:
                return
            if data['nick'] == new_nick:
                emit('edit_profile', {'status': 'new_nick_is_the_same_with_old_nick'})
            elif users.find_one({'nick': new_nick}):
                emit('edit_profile', {'status': 'incorrect_new_nick'})
            elif (datetime.utcnow() - user['last_nick_update']).total_seconds() < 2592000:
                emit('edit_profile', {'status': 'last_nick_update_was_less_than_a_month_ago'})
            update_data['nick'] = new_nick
            update_data['last_nick_update'] = datetime.utcnow()
        if update_data:
            users.update_one(
                {'nick': data['nick']},
                {'$set': update_data}
            )
        emit('edit_profile', {'status': 'OK'})

    @staticmethod
    def connection(data):
        if not hf.check_session_id(data):
            return
        users.update_one(
            {'nick': data['nick']},
            {'$set': {'is_online': True, 'sid': data['sid']}}
        )

    @staticmethod
    def disconnect(sid):
        user = users.find_one({'sid': sid})
        if not user:
            return
        users.update_one(
            {'sid': sid},
            {'$set': {'is_online': False, 'last_seen': datetime.utcnow().isoformat()}}
        )


up = user_processing()
