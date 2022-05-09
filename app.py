from pymongo import MongoClient
from flask import Flask, render_template,request,jsonify
import hashlib


app = Flask(__name__)

client = MongoClient('13.125.152.229', 27017, username="test", password="test")
db = client.MyHiddenSong



@app.route('/sign_up')
def sign_up_page():
    return render_template('Sign_up_page.html')

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                                   # 아이디
        "password": password_hash,                                      # 비밀번호
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)