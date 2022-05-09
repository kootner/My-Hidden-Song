from pymongo import MongoClient
from flask import Flask, render_template

app = Flask(__name__)

client = MongoClient('13.125.152.229', 27017, username="test", password="test")
db = client.MyHiddenSong



@app.route('/sign_up')
def sign_up():
    return render_template('Sign_up_page.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)