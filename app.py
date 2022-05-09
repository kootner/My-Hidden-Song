from pymongo import MongoClient
from flask import Flask, request, jsonify, render_template, redirect
import hashlib
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

TOKEN_KEY = 'SPARTA'

client = MongoClient('13.125.152.229', 27017, username="test", password="test")
db = client.MyHiddenSong


# Login Branc Start

@app.route('/sign_in', methods=['POST'])
def sign_in():
    id = request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    result = db.users.find_one({'id': id, 'pw': pw_hash})

    if result is not None:
        # 입력받은 id, pw 와 일치하는 유저가 db에 존재할때
        payload = {
            'id': id,
            'expire': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, TOKEN_KEY, algorithm='HS256').decode('utf-8')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': "로그인 실패!"})


# Login Branch End


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
