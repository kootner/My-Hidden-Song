from pymongo import MongoClient
from flask import Flask

app = Flask(__name__)

client = MongoClient('13.125.152.229', 27017, username="test", password="test")
db = client.MyHiddenSong


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)