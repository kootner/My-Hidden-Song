from pymongo import MongoClient
from flask import Flask, render_template, request,jsonify

import hashlib
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


client = MongoClient('13.125.152.229', 27017, username="test", password="test")
db = client.MyHiddenSong



# Add Song Branch Start

@app.route('/add_song_page')
def add_song_page():
    return render_template('add_song.html')


@app.route('/add_song', methods=['GET'])
def add_song():

    # gini_url = request.args.get("gini_url")
    gini_url = "https://www.genie.co.kr/detail/songInfo?xgnm=92366473"
    # youtube_url = request.args.get("youtube_url")
    # comment = request.args.get("comment")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(gini_url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    album = soup.select('#body-content > div.song-main-infos > div.photo-zone > a > span.cover > img')[0]['src']

    music = soup.select('#body-content > div.song-main-infos > div.info-zone > h2')[0].text

    artist = soup.select('#body-content > div.song-main-infos > div.info-zone > ul > li:nth-child(1) > span.value > a')[0].text
    print(album,music,artist)
    return render_template('music_list.html')

# Add Song Branch End

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)