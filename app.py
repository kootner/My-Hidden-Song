from pymongo import MongoClient

from flask import Flask, request, jsonify, render_template, redirect,url_for
import hashlib
import jwt
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TOKEN_KEY = 'SPARTA'

client = MongoClient('13.125.152.229', 27017, username="test", password="test")
db = client.MyHiddenSong


@app.route('/sign_up')
def sign_up_page():
    return render_template('Sign_up_page.html')

@app.route('/add_song_page')
def add_song_page():
    return render_template('add_song.html')

@app.route('/music_list')
def music_list():
    return render_template('music_list.html')

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    id_receive = request.form['id_give']
    exists = bool(db.users.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# Add Song Branch Start



@app.route('/check_song', methods=['GET'])
def check_song():
    # 지니 url을 통해 노래 정보 불러오기
    gini_url = request.args.get("gini_url")
    # gini_url = "https://www.genie.co.kr/detail/songInfo?xgnm=96664100"
    youtube_url = request.args.get("youtube_url")
    # gini_url 로 중복 등록 확인
    is_exist = db.musics.find_one({"gini_url": gini_url}, {"_id": False})
    if is_exist is not None:
        return jsonify({'result': 'fail', 'msg': '이미 등록된 음악입니다!'})
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(gini_url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    album = "https:" + soup.select('#body-content > div.song-main-infos > div.photo-zone > a > span.cover > img')[0][
        'src'].strip()

    music = soup.select('#body-content > div.song-main-infos > div.info-zone > h2')[0].text.strip()

    artist = soup.select('#body-content > div.song-main-infos > div.info-zone > ul > li:nth-child(1) > span.value > a')[
        0].text.strip()
    if None in {album, music, artist}:
        # 앨범, 제목, 가수 중 하나라도 None 값이라면 false 반환
        return jsonify({"result": "false", "msg":"파싱 오류 입니다!"})

    doc = {
        "result": "success",
        "album": album,
        "music": music,
        "artist": artist,
        "gini_url": gini_url
    }
    return jsonify(doc)


@app.route('/add_song', methods=['GET'])
def add_song():
    # token_receive = request.cookies.get('mytoken')
    # try:
    #     payload = jwt.decode(token_receive, TOKEN_KEY, algorithms=['HS256'])
    #     user_info = db.users.find_one({"id": payload["id"]})
    user_info={"nick": "test"}
    album = request.args.get("album")
    music = request.args.get("music")
    artist = request.args.get("artist")
    gini_url = request.args.get("gini_url")
    youtube_url = request.args.get("youtube_url")
    comment = request.args.get("comment")
    # gini_url 로 중복 등록 확인
    is_exist = db.musics.find_one({"gini_url": gini_url}, {"_id": False})
    if is_exist is not None:
        return jsonify({'result': 'fail', 'msg': '이미 등록된 음악입니다!'})

    doc = {
        "album": album,
        "music": music,
        "artist": artist,
        "comment": comment,
        "reco": 0,
        "nick": user_info['nick'],
        "youtube_url": youtube_url,
        "gini_url": gini_url
    }
    db.musics.insert_one(doc)
    return jsonify({'result': 'success'})
    # except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
    #     return redirect(url_for("home"))


# Add Song Branch End


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
