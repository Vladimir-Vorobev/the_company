# -*- coding: utf-8 -*-
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

sio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    ping_interval=5,
)

games = {}

client = MongoClient("127.0.0.1:27017")
db = client.TheCompanyDB
rooms = db.rooms
users = db.users
game_info = db.game_info
ratings = db.ratings
