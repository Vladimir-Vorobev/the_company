# -*- coding: utf-8 -*-
from server_setup import sio, games, users, rooms, game_info
from game_events import ge, events_len
from ratings import rap
from modules import hf

import numpy as np
from copy import deepcopy
from datetime import datetime


class game_logic:
    def __init__(self, num, mode, start_time, game_users={}, timer_time=None, run=False, passed_events_ids=[], current_event={}):
        print(passed_events_ids)
        self.num = num
        self.users = game_users
        self.mode = mode
        self.timer_time = timer_time
        self.run = run
        self.passed_events_ids = passed_events_ids
        self.maximum_of_events = events_len
        self.current_event = current_event
        self.start_time = start_time
        self.set_new_timer_time()

    def timer(self):
        while self.run:
            sio.sleep(1)
            self.timer_time -= 1
            self.update_room({'timer_time': self.timer_time})
            if self.timer_time == 0:
                self.event_time_out()
                if self.run:
                    self.set_new_timer_time()
                    self.set_new_event()

    def set_new_timer_time(self):
        self.timer_time = np.random.randint(15, 20)
        self.update_room({'timer_time': self.timer_time})

    def process_user_choice(self, nick, choice_index, time_out_text=''):
        if nick not in self.users:
            return
        print(2)
        consequence = self.current_event['consequences'][choice_index]
        print(consequence)
        self.users[nick]['balance'] += consequence[1]
        sio.emit(
            'event_consequence',
            {
                'consequence': time_out_text + consequence[0],
                'balance': self.users[nick]['balance'],
            },
            room=self.users[nick]['sid'],
        )
        for user in self.users:
            if self.users[user]['balance'] <= 0:
                self.stop_game()
                break
        if self.mode == 'offline':
            sio.sleep(7)

    def event_time_out(self):
        index = np.random.randint(0, len(self.current_event['consequences']))
        for user in self.users:
            self.process_user_choice(user, index, time_out_text=ge.get_time_out_text() + '\n\n')
        self.update_room({'users': self.users})

    def set_new_event(self):
        event, event_id = ge.get_new_event(self.passed_events_ids)
        self.current_event = deepcopy(event)
        del event['consequences']
        for user in self.users:
            company_name = users.find_one({'nick': hf.modify_word(user)})['company_name']
            event_to_send = deepcopy(event)
            event_to_send['task'].format(company_name)
            sio.emit('new_event', {'event': event_to_send}, room=self.users[user]['sid'])

        self.passed_events_ids.append(event_id)
        if len(self.passed_events_ids) == self.maximum_of_events:
            self.passed_events_ids = []
        self.update_room({'current_event': self.current_event, 'passed_events_ids': self.passed_events_ids})

    def add_user(self, user_nick, user_sid):
        self.users[user_nick] = {'sid': user_sid, 'balance': np.random.randint(8000000, 12000000)}
        self.update_room({'users': self.users})

    def update_user_sid(self, user_nick, user_sid):
        self.users[user_nick]['sid'] = user_sid
        self.update_room({f'users.{user_nick}.sid': user_sid})

    def check_winners(self, room, messages):
        game_info.update_one({}, {'$inc': {'total_game_counter': 1}})
        # rap.check_an_update()

    def start_game(self):
        self.run = True
        self.set_new_event()
        for user in self.users:
            sio.emit('get_current_balance', {'balance': self.users[user]['balance']})
        self.update_room({'run': True})
        sio.start_background_task(target=self.timer)

    def stop_game(self):
        self.run = False
        delta = datetime.utcnow() - self.start_time
        game_time = delta.seconds + delta.microseconds // 10000
        for user in self.users:
            sio.emit('stop_game', {'game_time': game_time}, room=self.users[user]['sid'])
            player = users.find_one({'nick': hf.modify_word(user)})
            player_nick = hf.modify_word(user)
            users.update_one({'nick': player_nick}, {'$inc': {'statistics.game_counter': 1}})
            if game_time > 600:
                users.update_one({'nick': player_nick}, {'$inc': {'statistics.win_game': 1}})
            if not player['statistics']['max_game_time'] or game_time > player['statistics']['max_game_time']:
                users.update_one({'nick': player_nick}, {'$set': {'statistics.max_game_time': game_time}})
                rap.update_rating('max_game_time')
            if not player['statistics']['min_game_time'] or game_time < player['statistics']['min_game_time']:
                users.update_one({'nick': player_nick}, {'$set': {'statistics.min_game_time': game_time}})
                rap.update_rating('min_game_time')
        rooms.delete_one({'num': self.num})
        del games[self.num]
        game_info.update_one({}, {'$inc': {'total_game_counter': 1}})

    def update_room(self, data):
        rooms.update_one({'num': self.num}, {'$set': data})


def restart_games():
    for room in rooms.find():
        game = game_logic(
            room['num'],
            room['mode'],
            room['start_time'],
            game_users=room['users'],
            timer_time=room['timer_time'],
            run=room['run'],
            passed_events_ids=room['passed_events_ids'],
            current_event=room['current_event'],
        )
        games[room['num']] = game
        game.start_game()
    sio.emit('restart', {}, broadcast=True)
