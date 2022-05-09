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

            return render_template('list.html', user_info=user_info)
        else:
            return render_template('index.html')
    except jwt.ExpiredSignatureError:
        print("로그인 시간 만료")
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        print("로그인 정보가 없습니다")
        return render_template('index.html')


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
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, TOKEN_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': "로그인 실패!"})


# Login Branch End


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
