from pymongo import MongoClient
from flask import Flask, render_template,request,jsonify
import hashlib


app = Flask(__name__)

client = MongoClient('13.125.152.229', 27017, username="test", password="test")
db = client.MyHiddenSong



@app.route('/sign_up')
def sign_up_page():
    return render_template('Sign_up_page.html')

@app.route('/music_list')
def music_list():
    return render_template('music_list.html')

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    id_receive = request.form['id_give']
    exists = bool(db.users.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/check_dup_nick', methods=['POST'])
def check_dup_nick():
    nick_receive = request.form['nick_give']
    exists = bool(db.users.find_one({"nick": nick_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    nick_recive = request.form['nick_give']
    doc = {
        "id": id_receive,                                   # 아이디
        "pw": pw_hash,                                      # 비밀번호
        "nick": nick_recive
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)