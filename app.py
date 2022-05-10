from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify, redirect, url_for
import jwt

import hashlib
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TOKEN_KEY = 'SPARTA'

client = MongoClient('13.125.152.229', 27017, username="test", password="test")
db = client.MyHiddenSong


# Add Song Branch Start


@app.route('/add_song_page')
def add_song_page():
    return render_template('add_song.html')


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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
