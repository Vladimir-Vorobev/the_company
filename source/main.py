# -*- coding: utf-8 -*-
from flask import request
import eventlet.wsgi
from datetime import datetime
from copy import deepcopy

from server_setup import app, sio, games, rooms, users
# from room_socket_processing import rsp
from user_processing import up
from authentification import ap
from game_logic import game_logic, restart_games
from modules import hf
# from ratings import rap


@app.route('/registration', methods=['POST'])
def reg_in():
    return ap.reg_in(request.data)


@app.route('/login', methods=['POST'])
def log_in():
    return ap.log_in(request.data)


@app.route('/get-statistics', methods=['POST'])
def get_statistics():
    return hf.get_statistics(request.data)


@sio.on('get_profile')
def get_profile(data):
    up.get_profile(data)


@sio.on('connection')
def connection(data):
    data['sid'] = request.sid
    up.connection(data)


@sio.on('disconnect')
def disconnect():
    up.disconnect(request.sid)


@sio.on('leave_app')
def leave_app(data):
    up.disconnect(request.sid)


@sio.on('edit_profile')
def edit_profile(data):
    up.edit_profile(data)


@sio.on('create_game')
def create_game(data):
    if data and not hf.check_session_id(data):
        return
    mode = data['mode']
    nick = data['nick']
    time = datetime.utcnow()
    room = rooms.find_one({f'users.{nick}': {'$exists': True}})
    if mode not in ['offline', 'online']:
        return
    if room:
        print(1)
        sio.emit('create_game', {'num': room['num']})
        return
    num = 1
    while rooms.find_one({'num': num}):
        num += 1
    rooms.insert_one({
        'num': num,
        'users': {},
        'mode': mode,
        'timer_time': None,
        'run': False,
        'passed_events_ids': [],
        'current_event': {},
        'start_time': time,
    })
    game = game_logic(num, mode, time)
    game.add_user(nick, request.sid)
    games[num] = game
    sio.emit('create_game', {'num': num})
    game.start_game()


@sio.on('connect_to_game')
def connect_to_game(data):
    if data and not hf.check_session_id(data):
        return
    num = data['num']
    nick = data['nick']
    if num not in games:
        return
    company_name = users.find_one({'nick': hf.modify_word(nick)})['company_name']
    event_to_send = deepcopy(games[num].current_event)
    event_to_send['task'].format(company_name)
    games[num].update_user_sid(nick, request.sid)
    sio.emit('get_my_game_info', {'balance': games[num].users[nick]['balance'], 'current_event': event_to_send})


@sio.on('user_choice')
def user_choice(data):
    if data and not hf.check_session_id(data):
        return
    games[data['num']].process_user_choice(data['nick'], data['choice_index'])


# @sio.on('get_rating')
# def get_rating(data):
#     rap.get_rating(data)


def send_ping():
    while True:
        sio.emit('ping', {}, broadcast=True)
        sio.sleep(7)


if __name__ == "__main__":
    restart_games()
    sio.start_background_task(target=send_ping)
    eventlet.wsgi.server(eventlet.wrap_ssl(eventlet.listen(('', 5050)),
                                           certfile='/app/server/files/certificate.crt',
                                           keyfile='/app/server/files/private_key.key',
                                           ca_certs='/app/server/files/certificate_ca.crt',
                                           server_side=True),
                         app)
