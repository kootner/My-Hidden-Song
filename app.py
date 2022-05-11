from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, request, jsonify, render_template, redirect,url_for
import hashlib
import jwt
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# JWT 키
TOKEN_KEY = 'SPARTA'

# 몽고DB 접속 아이디 test, 비밀번호 test
client = MongoClient('13.125.152.229', 27017, username="test", password="test")
db = client.MyHiddenSong


# 루트 페이지 랜더링
@app.route('/')
def home():
    # 쿠키에 저장된 토큰 가져오기
    token = request.cookies.get('mytoken')
    try:
        if token is not None:
            # 쿠키에 저장 된 토큰이 있을 떄 JWT 키(TOKEN_KEY)와 토큰으로 서버에 저장된 payload를 불러옴
            payload = jwt.decode(token, TOKEN_KEY, algorithms=['HS256'])
            # payload에 저장된 id 값으로 users 디비에서 유저 정보를 불러옴
            user_info = db.users.find_one({"id": payload["id"]})
            if user_info is None:
                # 유저가 없을때 index로..
                return render_template('index.html', msg='로그인 정보가 없습니다.')
            # 로그인이 되어 있을때 음악 목록 페이지로 랜더링
            return redirect(url_for('music_data'))
        else:
            # 쿠키에 저장 된 토큰이 없을 때 index 페이지로 랜더링
            return render_template('index.html', msg='로그인 정보가 없습니다.')
    except jwt.ExpiredSignatureError:
        # 로그인 시간이 만료 되었을 때 jwt 에서 주는 에러 예외 처리, 홈으로 랜더링
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        # 기타 다른 오류가 발생했을 때 jwt 에서 주는 에러 예외 처리, 홈으로 랜더링
        return render_template('index.html')

# 회원가입 페이지 랜더링
@app.route('/sign_up')
def sign_up_page():
    # 쿠키에 저장된 토큰 가져오기
    token = request.cookies.get('mytoken')
    if token is not None:
        # 로그인이 된 상태에서 회원가입 페이지 접근 금지
        return redirect(url_for("home"))
    else:
        # 로그인이 안된 상태 회원가입 페이지 접근 가능
        return render_template('Sign_up_page.html')

# 노래추가 페이지 랜더링
@app.route('/add_song_page')
def add_song_page():
    # 쿠키에 저장된 토큰 가져오기
    token = request.cookies.get('mytoken')
    if token is not None:
        # 로그인이 안된 상태 노래 추가 페이지 접근 가능
        return render_template('add_song.html')
    else:
        # 로그인이 된 상태에서 노래 추가 페이지 접근 금지
        return redirect(url_for("home"))


# 노래 정보 불러오기 프로세스
@app.route('/check_song', methods=['GET'])
def check_song():
    # 지니 url을 통해 노래 정보 불러오기
    gini_url = request.args.get("gini_url")
    # gini_url 예시 "https://www.genie.co.kr/detail/songInfo?xgnm=96664100"
    # gini_url 로 중복 등록 확인
    is_exist = db.musics.find_one({"gini_url": gini_url}, {"_id": False})
    if is_exist is not None:
        return jsonify({'result': 'fail', 'msg': '이미 등록된 음악입니다!'})
    # 중복이 아닌 지니 url 로 곡 정보 파싱
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(gini_url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    # 앨범 사진
    album = "https:" + soup.select('#body-content > div.song-main-infos > div.photo-zone > a > span.cover > img')[0][
        'src'].strip()
    # 노래 제목
    music = soup.select('#body-content > div.song-main-infos > div.info-zone > h2')[0].text.strip()

    # 가수 이름
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

# 노래 추가 프로세스
@app.route('/add_song', methods=['GET'])
def add_song():
    # 쿠키에 저장된 토큰 가져오기
    token = request.cookies.get('mytoken')
    try:
        # 쿠키에 저장 된 토큰이 있을 떄 JWT 키(TOKEN_KEY)와 토큰으로 서버에 저장된 payload를 불러옴
        if token is not None:
            # 쿠키에 저장 된 토큰이 있을 떄 JWT 키(TOKEN_KEY)와 토큰으로 서버에 저장된 payload를 불러옴
            payload = jwt.decode(token, TOKEN_KEY, algorithms=['HS256'])
            # payload에 저장된 id 값으로 users 디비에서 유저 정보를 불러옴
            user_info = db.users.find_one({"id": payload["id"]})
            if user_info is None:
                # 유저가 없을때 index로..
                return render_template('index.html', msg='로그인 정보가 없습니다.')
        else:
            # 쿠키에 저장 된 토큰이 없을 때 index 페이지로 랜더링
            return render_template('index.html', msg='로그인 정보가 없습니다.')
        # ajax 를 통해 받은 데이터들 초기화
        album = request.args.get("album")
        music = request.args.get("music")
        artist = request.args.get("artist")
        gini_url = request.args.get("gini_url")
        youtube_url = request.args.get("youtube_url")
        comment = request.args.get("comment")

        # gini_url 로 중복 등록 다시 한번 확인
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
        # 디비에 노래 정보 추가
        db.musics.insert_one(doc)
        return jsonify({'result': 'success'})

    except jwt.ExpiredSignatureError:
        # 로그인 시간이 만료 되었을 때 jwt 에서 주는 에러 예외 처리, 홈으로 랜더링
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        # 기타 다른 오류가 발생했을 때 jwt 에서 주는 에러 예외 처리, 홈으로 랜더링
        return render_template('index.html')


# Add Song Branch End



# 로그인 프로세스
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 서버에서 받은 아이디, 비밀번호 값
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 디비 안에 저장할 때 암호화를 해서 저장, 암호화 함수
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # ajax 를 통해 받은 id 와 암호화 된 pw 를 통해 users 디비에서 조회
    result = db.users.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        # 입력받은 id, pw 와 일치하는 유저가 db에 존재할때

        # jwt를 통해 서버에 저장할 데이터
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60)  # 로그인 1시간 유지
        }
        # jwt를 통해 서버에 저장 한 후 받은 토큰 값 저장, 쿠키에 저장을 위해 프론트로 토큰 값 리턴
        token = jwt.encode(payload, TOKEN_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': "로그인 실패!"})

# 아이디 중복 확인 프로세스
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # ajax를 통해 받은 id 값
    id_receive = request.form['id_give']

    # 받은 id 를 통해 users 디비에서 조회, None 이 아니면(유저가 있으면) bool 을 통해 True 반환, None 이라면 False
    exists = bool(db.users.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 닉네임 중복 확인 프로세스
@app.route('/sign_up/check_dup_nick', methods=['POST'])
def check_dup_nick():
    # ajax를 통해 받은 nick 값
    nick_receive = request.form['nick_give']

    # 받은 nick 를 통해 users 디비에서 조회, None 이 아니면(유저가 있으면) bool 을 통해 True 반환, None 이라면 False
    exists = bool(db.users.find_one({"nick": nick_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# 회원 가입 프로세스
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    # ajax를 통해 받은 신규 회원 id, pw, nick 값
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 디비 안에 저장할 때 암호화를 해서 저장, 암호화 함수
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    nick_recive = request.form['nick_give']


    doc = {
        "id": id_receive,  # 아이디
        "pw": pw_hash,  # 비밀번호
        "nick": nick_recive
    }
    # 디비에 신규 회원 정보 추가
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


# 노래 목록 페이지 랜더링
@app.route('/music_list', methods=['GET'])
def music_data():
    # 쿠키에 저장된 토큰 가져오기
    token = request.cookies.get('mytoken')
    try:
        # 쿠키에 저장 된 토큰이 있을 떄 JWT 키(TOKEN_KEY)와 토큰으로 서버에 저장된 payload를 불러옴
        if token is not None:
            # 쿠키에 저장 된 토큰이 있을 떄 JWT 키(TOKEN_KEY)와 토큰으로 서버에 저장된 payload를 불러옴
            payload = jwt.decode(token, TOKEN_KEY, algorithms=['HS256'])
            # payload에 저장된 id 값으로 users 디비에서 유저 정보를 불러옴
            user_info = db.users.find_one({"id": payload["id"]})
            if user_info is None:
                # 유저가 없을때 index로..
                return render_template('index.html', msg='로그인 정보가 없습니다.')
        else:
            # 쿠키에 저장 된 토큰이 없을 때 index 페이지로 랜더링
            return render_template('index.html', msg='로그인 정보가 없습니다.')

        # musics 디비에서 추천 수 (reco) 내림차순 (-1) 정렬 하여 find
        music_data_temp = list(db.musics.find().sort('reco', -1))

        # ObjectId 객체인 musics 디비의 _id 필드를 string 타입으로 변경하여 music_data 배열에 넣는 과정
        music_data = []
        for document in music_data_temp:
            document['_id'] = str(document['_id'])
            music_data.append(document)

        # 음악 목록 페이지에 음악 목록과 유저 정보 전달하며 랜더링
        return render_template('music_list.html', music_datas = music_data, user_info = user_info)
    except jwt.ExpiredSignatureError:
        # 로그인 시간이 만료 되었을 때 jwt 에서 주는 에러 예외 처리, 홈으로 랜더링
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        # 기타 다른 오류가 발생했을 때 jwt 에서 주는 에러 예외 처리, 홈으로 랜더링
        return render_template('index.html')

@app.route('/heart', methods=['POST'])
def heart():
    # 쿠키에 저장된 토큰 가져오기
    token = request.cookies.get('mytoken')
    try:
        # 쿠키에 저장 된 토큰이 있을 떄 JWT 키(TOKEN_KEY)와 토큰으로 서버에 저장된 payload를 불러옴
        if token is not None:
            # 쿠키에 저장 된 토큰이 있을 떄 JWT 키(TOKEN_KEY)와 토큰으로 서버에 저장된 payload를 불러옴
            payload = jwt.decode(token, TOKEN_KEY, algorithms=['HS256'])
            # payload에 저장된 id 값으로 users 디비에서 유저 정보를 불러옴
            user_info = db.users.find_one({"id": payload["id"]})
            if user_info is None:
                # 유저가 없을때 index로..
                return render_template('index.html', msg='로그인 정보가 없습니다.')
        else:
            # 쿠키에 저장 된 토큰이 없을 때 index 페이지로 랜더링
            return render_template('index.html', msg='로그인 정보가 없습니다.')

        # ajax 에서 받은 좋아요 관련 작업을 할 음악의 _id 값
        music_id = request.form['id']

        # music_id 의 _id 값을 받는 음악의 reco 필드에 더할 값 ( 좋아요일 경우 +1, 좋아요 취소 일 경우 -1 )
        sum_reco = int(request.form['sum_reco'])
        if sum_reco > 0:
            # 추천함, users 디비의 reco_music(내가 추천한 노래들 _id값을 모아둔 배열) 에 music_id 를 추가, upSert = True 는 배열이 없으면 생성하는 기능.
            db.users.update_one({"id" : user_info['id']}, {"$push": {"reco_music": music_id}}, upsert = True)
        else:
            # 추천 취소함, users 디비의 reco_music(내가 추천한 노래들 _id값을 모아둔 배열) 에 music_id 를 뺌
            db.users.update_one({"id" : user_info['id']}, {"$pull": {"reco_music": music_id}})

        # 음악의 reco(추천 수) 계산, reco 값에 sum_reco를 더해줌 ( 좋아요일 경우 +1, 좋아요 취소 일 경우 -1 )
        db.musics.update_one(
            {"_id": ObjectId(music_id)},
            {"$inc": {"reco": sum_reco}}
        )
        return jsonify({'result': "success"})
    except jwt.ExpiredSignatureError:
        # 로그인 시간이 만료 되었을 때 jwt 에서 주는 에러 예외 처리, 홈으로 랜더링
        return render_template('index.html')
    except jwt.exceptions.DecodeError:
        # 기타 다른 오류가 발생했을 때 jwt 에서 주는 에러 예외 처리, 홈으로 랜더링
        return render_template('index.html')


# index 페이지에서 CORS로 인해 재생이 안되는 유튜브 URL 을 재생이 가능한 URL로 변경하는 프로세스
@app.route('/getYoutubeUrl', methods=['GET'])
def getYoutubeUrl():
    # 추천수 많은 영상 재생
    # youtubeUrl_temp=db.musics.find_one(sort=[("reco", -1)])

    # 랜덤재생, musics 에서 랜덤으로 한 곡을 뽑아옴, (size 가 몇개 뽑아 올지 정하는 변수)
    youtubeUrl_temp=list(db.musics.aggregate([{'$sample': { 'size': 1 } }]))[0]

    # 뽑아온 음악이 없으면
    if youtubeUrl_temp is None:
        return jsonify({'result': 'fail', 'msg': "노래 정보가 없습니다."})


    youtubeUrl_temp=youtubeUrl_temp["youtube_url"]
    # Youtube code 추출
    if "?v=" in youtubeUrl_temp:
        #  https://www.youtube.com/watch?v=Hbj48Cw87BQ&ab_channel=dingofreestyle 형식의 링크일 때
        youtubeUrl=youtubeUrl_temp.split('?v=')[1].split("&")[0] # Hbj48Cw87BQ 코드가 반환

    elif "youtu.be/" in youtubeUrl_temp:
        # https://youtu.be/Hbj48Cw87BQ 형식의 링크일 떄
        youtubeUrl=youtubeUrl_temp.split('youtu.be/')[1].split("?")[0] # Hbj48Cw87BQ 코드가 반환

    elif "/embed/" in youtubeUrl_temp:
        # https://www.youtube.com/embed/OsA3iPO2fEg?autoplay=1&mute=1 형식의 링크일 때
        youtubeUrl=youtubeUrl_temp.split('/embed/')[1].split("?")[0] # OsA3iPO2fEg 코드가 반환

    return jsonify({'result': 'success', 'youtubeUrl': youtubeUrl})

# 음악 목록 페이지에서 CORS로 인해 재생이 안되는 유튜브 URL 을 재생이 가능한 URL로 변경하는 프로세스
@app.route('/getYoutube', methods=['GET'])
def getYoutube():
    # ajax 에서 받은 youtube_url
    youtubeUrl_temp = request.args.get("youtube_url")

    # Youtube code 추출
    if "?v=" in youtubeUrl_temp:
        # https://www.youtube.com/watch?v=Hbj48Cw87BQ&ab_channel=dingofreestyle 형식의 링크일 때
        youtubeUrl=youtubeUrl_temp.split('?v=')[1].split("&")[0] # Hbj48Cw87BQ 코드가 반환

    elif "youtu.be/" in youtubeUrl_temp:
        # https://youtu.be/Hbj48Cw87BQ 형식의 링크일 떄
        youtubeUrl=youtubeUrl_temp.split('youtu.be/')[1].split("?")[0] # Hbj48Cw87BQ 코드가 반환

    elif "/embed/" in youtubeUrl_temp:
        # https://www.youtube.com/embed/OsA3iPO2fEg?autoplay=1&mute=1 형식의 링크일 때
        youtubeUrl=youtubeUrl_temp.split('/embed/')[1].split("?")[0] # OsA3iPO2fEg 코드가 반환

    return jsonify({'result': 'success', 'youtubeUrl': youtubeUrl})


# 로그인 페이지 랜더링
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('index.html', msg=msg)

# 노래 추가 페이지에서 노래 검색시 넘어온 검색어로 파싱 하는 프로세스
@app.route('/search', methods=['GET'])
def search():
    # ajax 에서 넘어온 search_text(검색어)
    search_text = request.args.get("search_text")

    # 예시) https://www.genie.co.kr/search/searchAuto?query=아이유
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get("https://www.genie.co.kr/search/searchAuto?query="+search_text, headers=headers)

    # 파싱한 데이터를 json으로 변환해 ajax 함수로 리턴
    return jsonify(data.json())


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
