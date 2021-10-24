import random
import json
import os
import inspect
import base64

from pprint import pp
from time import time
from datetime import datetime, timedelta

from traceback import format_exc, print_exc
format_exc.__dict__['limit'] = print_exc.__dict__['limit'] = 30

import requests
import pandas as pd
import numpy as np
import librosa
import ffmpeg
import cv2

import spacy
nlp = spacy.load('ja_ginza')

import matplotlib
import japanize_matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
from bs4 import BeautifulSoup

from dotenv import load_dotenv
dotenv_path = f'{os.path.dirname(__file__)}/.env'
load_dotenv(dotenv_path)
config = {key: os.environ[key] for key in [
        'apiKey',
        'authDomain',
        'databaseURL',
        'projectId',
        'storageBucket',
        'messagingSenderId',
        'appId',
        'measurementId'
    ]}

import pyrebase21 as pyrebase
firebase = pyrebase.initialize_app(config)
db       = firebase.database()


from rmn import RMN
movie_model = RMN()

from flask import Flask, render_template, jsonify, request
from utils.constructed_database import News, Room, Speech, Interest, Evaluation


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string   ='[%',
        block_end_string     ='%]',
        variable_start_string='[[',
        variable_end_string  =']]',
    ))

app = CustomFlask(__name__)


# エラーとjsonifyするためのデコレーター
def deco_api(fn):

    def inr_fn(*args, **kwargs):

        try:
            return jsonify(fn(*args, **kwargs))

        except:
            print_exc()

            return jsonify({'status': 'ERROR', 'reason': format_exc()})

    return inr_fn


# 逆オウム返し
@deco_api
@app.route('/api/communicate-torrap', methods=['POST'])
def api_communicate_torrap():

    res = request.json['text'][::-1]
    print(f'{res=}')

    return {'status': 'SUCCESS', 'res': res}


# 近日のニュースをニュースサイトから取り出して提示
@deco_api
@app.route('/api/suggest-news', methods=['GET'])
def api_suggest_news():

    """
    category_num:
        1: 社会
        2: 暮らし
        3: 科学・文化
        4: 政治
        5: ビジネス？
        6: 国際
        7: スポーツ
        8: 気象
    """
    category_num = 5
    base_url = 'https://www3.nhk.or.jp'
    page_num = 0
    news_list = []
    while True:
        page_num += 1
        child_url = f'news/json16/cat{category_num:02}_{page_num:03}.json'
        url = f'{base_url}/{child_url}'
        with requests.get(url) as req:
            req.encoding = req.apparent_encoding
            if req.status_code != requests.codes.ok:
                break

            data = json.loads(req.text)

        for datum in data['channel']['item']:
            # 画像がない記事は飛ばす
            if datum['imgPath']=='':
                continue

            news_list.append({
                    'url'    : (url := f'{base_url}/news/{datum["link"]}'),
                    'title'  : datum['title'],
                    'news_id': url.rsplit('/', 1)[-1].removesuffix('.html'),
                    'imgsrc' : f'{base_url}/news/{datum["imgPath"]}'
                })

    print('news_list[0]=')
    pp(news_list[0])
    print(f'{len(news_list)=}')

    return {'status': 'SUCCESS', 'res': news_list}


# 選んだニュースを受信し保存する
@deco_api
@app.route('/api/save-news', methods=['POST'])
def api_save_news():

    payload  = {key: request.json[key] for key in [
            'url',
            'title',
            'news_id',
            'imgsrc'
        ]}

    news = News.from_dict(payload)
    print(f'{news=}')

    try:
        news_od = db.child('news')\
                .order_by_child('news_id')\
                .equal_to(news.news_id)\
                .get().val()

    # ニュースがない場合は追加
    except IndexError:
        db.child('news').push(news.to_dict())
        print('saving news....')

        return {'status': 'SAVED'}

    # ニュースがある場合は追加しない
    else:
        print(f'the news already settled. <{news_od=}>')

        return {'status': 'ALREADY SETTLED'}


# 人事によって選ばれた近日のニュースを提示
@deco_api
@app.route('/api/question-news', methods=['GET'])
def api_question_news():

    news_df = db.child('news').get().to_df()
    news_df['timestamp'] = pd.to_datetime(
            news_df['timestamp'],
            format='%y-%m-%d %H:%M:%S'
        )
    news_df = news_df[
            news_df['timestamp'] > datetime.now() - timedelta(weeks=1)
        ]
    news_df = news_df[['title', 'news_id', 'url', 'imgsrc']].drop_duplicates()
    print('news_df=')
    print(news_df)

    news_list = list(news_df.to_dict(orient='index').values())
    news_count = 12 # 一応12個にしている
    res = random.sample(news_list, min(len(news_list), news_count))

    print('res[0]=')
    pp(res[0])
    print(f'{len(res)=}')

    return {'status': 'SUCCESS', 'res': res}


# 興味があるニュースを登録
@deco_api
@app.route('/api/save-degree', methods=['POST'])
def api_save_degree():

    payload  = {key: request.json[key] for key in [
            'name',
            'news_id',
            'degree'
        ]}

    interest = Interest.from_dict(payload)
    print(f'{interest=}')

    try:
        interest_od = db.child('interest')\
                .order_by_child('news_id')\
                .equal_to(interest.news_id)\
                .get().val()

    # ニュースがない場合は追加
    except IndexError:
        db.child('interest').push(interest.to_dict())
        print('saving interest....')

        return {'status': 'SAVED'}

    # ニュースがある場合は追加しない
    else:
        k = list(interest_od.keys())[0]
        db.child('interest').child(k).update(interest.to_dict())
        print('updating interest....')

        return {'status': 'UPDATED'}


# ルームの参加者を登録
@deco_api
@app.route('/api/set-room', methods=['POST'])
def api_set_room():

    payload = {key: request.json[key] for key in [
            'name',
            'zoom_id'
        ]}

    room = Room.from_dict(payload)
    print(f'{room=}')

    db.child('room').push(room.to_dict())

    return {'status': 'SUCCESS', 'res': room.to_dict()}


# 参加者の発言を受信し保存
@deco_api
@app.route('/api/save-speech', methods=['POST'])
def api_save_speech():

    payload = {key: request.json[key] for key in [
            'name',
            'zoom_id',
            'text'
        ]}

    speech = Speech.from_dict(payload)
    print(f'{speech=}')

    db.child('speech').push(speech.to_dict())

    return {'status': 'SAVED', 'res': speech.to_dict()}


def get_interest_df(zoom_id: str):

    # ルーム参加者の名前を全件取得
    names = db.child('room')\
            .order_by_child('zoom_id')\
            .equal_to(zoom_id)\
            .get().to_df()['name']
    print('names=')
    print(names)

    # ルーム参加者全員の中で最も人気があるニュースを持ってくる
    interest_df = pd.DataFrame(index=[], columns=['name', 'news_id', 'degree'])
    for name in names:
        try:
            _interest_df = db.child('interest')\
                    .order_by_child('name')\
                    .equal_to(name)\
                    .get().to_df()
        except:
            continue

        interest_df = pd.concat([interest_df, _interest_df])

    interest_df['degree'] = interest_df['degree'].astype(int)

    return interest_df


# 登録参加者の興味に応じて初期のニュースを送信
@deco_api
@app.route('/api/set-news', methods=['POST'])
def api_set_news():

    zoom_id = request.json['zoom_id']

    interest_df = get_interest_df(zoom_id)

    popular_news_id = interest_df.groupby('news_id').sum('degree').idxmax()[0]

    # 最も人気があるニュースを呼び出す
    news_df = db.child('news')\
            .order_by_child('news_id')\
            .equal_to(popular_news_id)\
            .get().to_df()

    res = dict(news_df.iloc[0])
    print(f'{res=}')

    return {'status': 'SUCCESS', 'res': res}


# 興味に応じてニュースを変える
@deco_api
@app.route('/api/change-topic', methods=['POST'])
def api_change_topic():

    zoom_id = request.json['zoom_id']
    news_id = request.json['news_id']
    title   = request.json['title']

    speech_df = db.child('speech')\
            .order_by_child('zoom_id')\
            .equal_to(zoom_id)\
            .get().to_df()
    speech_df['timestamp'] = pd.to_datetime(
            speech_df['timestamp'],
            format='%y-%m-%d %H:%M:%S'
        )

    # 直近の発言を見る
    # 一応15秒で30文字以上と設定
    delta, cos_threshold = 15, 1 / 2 ** .5
    speech_df = speech_df[
            speech_df['timestamp'] > datetime.now() - timedelta(seconds=delta)
        ]

    # 何も話さないと値がintの0になる
    text = speech_df['text'].sum()

    # 自然言語処理で興味度を推定
    # TODO: もしかしたらMeCabにするかも
    if isinstance(text, str):
        doc = nlp(text)

        text = ''
        for sent in doc.sents:
            for token in sent:
                if token.pos_ in ['NOUN', 'PROPN', 'VERB']:
                    text += str(token)

        doc       = nlp(text)
        title_doc = nlp(title)
        # 興味がありそうなため変えない
        if (similarity := doc.similarity(title_doc)) > cos_threshold:
            print(f'{similarity=}. remain....')
            return {'status': 'REMAIN'}

    # 興味がないため、変える
    interest_threshold = 5   # 一応興味度の平均の閾値を5とした

    interest_df = get_interest_df(zoom_id)
    interest_df = interest_df[interest_df['news_id'] != news_id]

    groupby_news_df   = interest_df.groupby('news_id').mean().reset_index()
    print(groupby_news_df)
    suggested_news_df = groupby_news_df[
            groupby_news_df['degree'] > interest_threshold
        ]
    if len(suggested_news_df) > 0:
        suggested_news_id = list(suggested_news_df.sample()['news_id'])[0]
    else:
        suggested_news_id = list(groupby_news_df.sample()['news_id'])[0]

    news_df = db.child('news')\
            .order_by_child('news_id')\
            .equal_to(suggested_news_id)\
            .get().to_df()

    news = list(news_df.to_dict(orient='index').values())[0]

    print(news_df)
    print('changing topic....')

    return {'status': 'CHANGE', 'res': news}


# 参加者の名前を表示
@deco_api
@app.route('/api/set-names', methods=['POST'])
def api_set_names():

    zoom_id = request.json['zoom_id']

    try:
        room_df = db.child('room')\
            .order_by_child('zoom_id')\
            .equal_to(zoom_id)\
            .get().to_df()
    except IndexError: # 指定のzoom_idがデータベース上に存在しない時、404を返す
        return '', 404
    else:
        names = list(room_df['name'])
        return {'status': 'SUCCESS', 'res': names}


# 動画音声のアップロード・解析・評価保存
@deco_api
@app.route('/api/save-evaluation', methods=['POST'])
def api_save_evaluation():

    payload = eval(str(request.form.to_dict()))
    print(f'{payload=}')

    zoom_id = payload['zoom_id']
    names   = payload['names'].split(',')[1:]

    # 各参加者の音声を設置
    sounds = {}
    tmp_sound_fname = 'tmp.m4a'
    print(f'{request.files.keys()=}')
    for name in names:
        print(f'{name=}')
        sound = request.files.get(f'sound-{name}', None)
        print(sound)
        with open(tmp_sound_fname, mode='wb') as f:
            f.write(sound.read())

        y, _ = librosa.load(tmp_sound_fname)
        print(f'{name=}, {type(y)=}, {y=}')
        sounds[name] = y
        plt.plot(y, label=name)
        os.remove(tmp_sound_fname)

    plt.legend()
    tmp_graph_fname = 'tmp.png'
    plt.savefig(tmp_graph_fname)
    with open(tmp_graph_fname, mode='rb') as f:
        b64str = base64.b64encode(f.read()).decode('utf-8')
        speaking_im_b64 = f'data:image/png;base64,{b64str}'

    os.remove(tmp_graph_fname)

    # 動画を設置
    movie = request.files.get('movie', None)
    _tmp_movie_fname = 'pretmp.mp4'
    with open(_tmp_movie_fname, mode='wb') as f:
        f.write(movie.read())

    # 0.2 fpsに一応設定　
    tmp_movie_fname = 'tmp.mp4'
    ffmpeg.input(_tmp_movie_fname)\
        .filter('fps', fps=.2)\
        .output(tmp_movie_fname).run()
    os.remove(_tmp_movie_fname)

    cap = cv2.VideoCapture(tmp_movie_fname)
    os.remove(tmp_movie_fname)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    fers = {name: {emotion: 0 for emotion in emotions}
            for name in names
        } # facial emotion rate

    """
    positions:
    +--------+-------+
    |   0    |   1   |
    +--------+-------+
    |   2    |   3   |
    +--------+-------+
    """
    # ここは必ず変わる

    positions = [
            (range(        0, height//2), range(       0, width//2)),
            (range(        0, height//2), range(width//2, width   )),
            (range(height//2, height   ), range(       0, width//2)),
            (range(height//2, height   ), range(width//2, width   ))
        ]

    ranges = {
            name: position for name, position in zip(names, positions)
        }
    ix = 0
    start = time()
    while True:
        ix += 1
        ret, img = cap.read()
        if img is None:
            break

        img = np.fliplr(img).astype(np.uint8)
        results = movie_model.detect_emotion_for_single_frame(img)
        for result in results:
            xmin, ymin = result['xmin'], result['ymin']
            emotion = result['emo_label']
            for name, (ry, rx) in ranges.items():
                if xmin in rx and ymin in ry:
                    fers[name][emotion] += 1
                    break

        print(f'{ix=}, elapsed={time()-start:4.4f} sec.')
        pp(fers)

    for name in names:
        ev_payload = {
                'name'           : name,
                'zoom_id'        : zoom_id,
                'speaking_im_b64': speaking_im_b64
            } | fers[name]
        evaluation = Evaluation.from_dict(ev_payload)
        db.child('evaluation').push(evaluation.to_dict())

    return {'status': 'SAVED'}


# TODO: 評価を表示
@deco_api
@app.route('/api/set-evaluation', methods=['POST'])
def api_set_evaluation():

    zoom_id = request.json['zoom_id']

    evaluation_df = db.child('evaluation')\
            .order_by_child('zoom_id')\
            .equal_to(zoom_id)\
            .get().to_df()

    emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    res = {}
    for name in evaluation_df['name']:
        _res = {}
        df = evaluation_df[evaluation_df['name'] == name]
        for emotion in emotions:
            _res[emotion] = int(df[emotion])

        _res['speaking_im_b64'] = list(df['speaking_im_b64'])[0]
        res[name] = _res

    return {'status': 'SUCCESS', 'res': res}


@app.route('/')
def page_index():

    return render_template('index.html')


@app.route('/torrap')
def page_torrap():

    return render_template('torrap.html')


@app.route('/news')
def page_news():

    return render_template('news.html')


@app.route('/enquete')
def page_question_news():

    return render_template('enquete.html')


@app.route('/room')
def page_room():

    return render_template('room.html')


@app.route('/suggestion')
def page_suggestion():

    return render_template('suggestion.html')


@app.route('/computing')
def page_computing():

    return render_template('computing.html')


@app.route('/analysis')
def page_analysis():

    return render_template('analysis.html')


if __name__ == '__main__':

    app.run(debug=True)
