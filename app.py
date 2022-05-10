from pymongo import MongoClient
from flask import Flask, request, jsonify, render_template, redirect,url_for
import hashlib
import jwt
from datetime import datetime, timedelta


app = Flask(__name__)

TOKEN_KEY = 'SPARTA'

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


@app.route('/')
def home():
    token = request.cookies.get('mytoken')
    print(token)
    try:
        if token is not None:
            payload = jwt.decode(token, TOKEN_KEY, algorithms=['HS256'])
            user_info = db.users.find_one({"id": payload["id"]})
            if user_info is None:
                return render_template('index.html', msg='로그인 정보가 없습니다.')

            return render_template('music_list.html', user_info=user_info)
        else:
            return render_template('index.html')
    except jwt.ExpiredSignatureError:
        print("로그인 시간 만료")
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        print("로그인 정보가 없습니다")
        return render_template('index.html')

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('index.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.users.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        # 입력받은 id, pw 와 일치하는 유저가 db에 존재할때
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, TOKEN_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': "로그인 실패!"})



@app.route('/music_list/data', methods=['GET'])
def music_data():
    music_data = list(db.musics.find({}, {'_id': False}))
    return jsonify({'all_music': music_data})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
