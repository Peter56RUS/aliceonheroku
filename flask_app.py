from flask import Flask, request
import logging
import os
import json
import sqlite3

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

places = [('Пешеходный мост через реку Урал', 'https://static-maps.yandex.ru/1.x/?ll=55.107619%2C51.753210&size=450,450&z=17&l=map&pt=55.107250%2C51.753077'),
          ('Памятник Пушкину и Далю', "https://static-maps.yandex.ru/1.x/?ll=55.099437%2C51.764943&size=450,450&z=18&l=map&pt=55.099437%2C51.764943"),
          ('Памятник Валерию Чкалову', 'https://static-maps.yandex.ru/1.x/?ll=55.106317%2C51.754628&size=450,450&z=18&l=map&pt=55.106317%2C51.754628'),
          ('Башня с курантами', 'https://static-maps.yandex.ru/1.x/?ll=55.1001008%2C51.764688&size=450,450&z=18&l=map&pt=55.100025%2C51.764688'),
          ('Детская железная дорога', 'https://static-maps.yandex.ru/1.x/?ll=55.105659%2C51.754003&size=450,450&z=17&l=map&pt=55.105659%2C51.753900'),
          ("Памятник Гагарину", 'https://static-maps.yandex.ru/1.x/?ll=55.167926%2C51.775930&size=450,450&z=16&l=map&pt=55.167800%2C51.775839'),
          ('Музей истории Оренбурга', 'https://static-maps.yandex.ru/1.x/?ll=55.107350%2C51.755227&size=450,450&z=17&l=map&pt=55.108311%2C51.755413')]
ssylka = ''


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    global ssylka
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Пешеходный мост",
                "Памятник Пушкину и Далю",
                "Памятник Чкалову",
                'Башня с курантами',
                'Детская железная дорога',
                'Памятник Гагарину',
                "Музей истории Оренбурга",
                "Помощь",
                'До свидания'
            ]
        }
        ssylka = ''

        res['response'][
            'text'] = f'''Добрый день! Вас приветствует навык "Достопримечательности Оренбурга"! О чём вы хотите узнать?
Выберите одну из плиток ниже'''

        res['response']['buttons'] = get_suggests(user_id)
        return

    if 'место' in req['request']['original_utterance'].lower():
        ssylka = ''
        res['response']['end_session'] = True

    rf = True
    ssylka = ''
    if 'пешеходный мост' in req['request']['original_utterance'].lower():
        place = places[0][0]
        ssylka = places[0][1]
        rf = False
    elif 'памятник чкалову' in req['request']['original_utterance'].lower():
        place = places[2][0]
        ssylka = places[2][1]
        rf = False
    elif 'памятник пушкину' in req['request']['original_utterance'].lower():
        place = places[1][0]
        ssylka = places[1][1]
        rf = False
    elif 'башня с курантами' in req['request']['original_utterance'].lower():
        place = places[3][0]
        ssylka = places[3][1]
        rf = False
    elif 'детская железная дорога' in req['request']['original_utterance'].lower():
        place = places[4][0]
        ssylka = places[4][1]
        rf = False
    elif 'памятник гагарину' in req['request']['original_utterance'].lower():
        place = places[5][0]
        ssylka = places[5][1]
        rf = False
    elif 'музей истории оренбурга' in req['request']['original_utterance'].lower():
        place = places[6][0]
        ssylka = places[6][1]
        rf = False
    elif 'помощь' in req['request']['original_utterance'].lower():
        res['response'][
            'text'] = 'Для того, чтобы узнать информацию о какой-либо достопримечательности города Оренбурга нажмите на плитку с его названием.'
        ssylka = ''
    elif 'что ты умеешь' in req['request']['original_utterance'].lower():
        res['response'][
            'text'] = 'Я рассказываю о различных достопримечательностях города Оренбурга и показываю, где они находятся'
        ssylka = ''
    elif 'до свидания' in req['request']['original_utterance'].lower() or 'пока' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Пока!'
        res['response']['end_session'] = True
    else:
        res['response']['text'] = 'Команда некорректна. Похоже, вы немного ошиблись.'
        ssylka = ''
    res['response']['buttons'] = get_suggests(user_id)

    if not rf:
        con = sqlite3.connect("bdfa.db")

        cur = con.cursor()

        result = cur.execute(f"""SELECT answer FROM places WHERE name = '{place}'""").fetchall()
        img = cur.execute(f"""SELECT img FROM places WHERE name = '{place}'""").fetchall()
        img = img[0][0]
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['image_id'] = img
        res['response']['text'] = result[0][0] + '\n' + \
                                            'Местоположение вы можете узнать, нажав на кнопку "Местоположение". Достопримечательность на карте обозначена белой меткой'


def get_suggests(user_id):
    global places, ssylka
    session = sessionStorage[user_id]
    if ssylka:
        suggests = [{
            "title": "Местоположение",
            "url": ssylka,
            "hide": True
        }]
        for suggest in session['suggests']:
            suggests.append({'title': suggest, 'hide': True})
    else:
        suggests = [
            {'title': suggest, 'hide': True}
            for suggest in session['suggests']
        ]
    return suggests



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
