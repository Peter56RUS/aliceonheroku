from flask import Flask, request
import logging
import os
import json
import sqlite3

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

places = [('Пешеходный мост через реку Урал', 'ссылка на геокодер'),
          ('Памятник Пушкину и Далю', "ссылка на геокодер"),
          ('Памятник Валерию Чкалову', 'ссылка на геокодер'),
          ('Башня с курантами', 'ссылка на геокодер'),
          ('Детская железная дорога', 'ссылка на геокодер'),
          ("Памятник Гагарину", 'ссылка на геокодер'),
          ('Музей истории Оренбурга', 'ссылка на геокодер')]


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
                "Помощь"
            ]
        }

        res['response'][
            'text'] = f'''Добрый день! Вас приветствует навык "Достопримечательности Оренбурга"! О чём вы хотите узнать?
Выберите одну из плиток ниже'''

        res['response']['buttons'] = get_suggests(user_id)
        return

    rf = True
    if 'пешеходный мост' in req['request']['original_utterance'].lower():
        place = places[0][0]
        rf = False
    elif 'памятник чкалову' in req['request']['original_utterance'].lower():
        place = places[1][0]
        rf = False
    elif 'памятник пушкину' in req['request']['original_utterance'].lower():
        place = places[2][0]
        rf = False
    elif 'башня с курантами' in req['request']['original_utterance'].lower():
        place = places[3][0]
        rf = False
    elif 'детская железная дорога' in req['request']['original_utterance'].lower():
        place = places[4][0]
        rf = False
    elif 'памятник гагарину' in req['request']['original_utterance'].lower():
        place = places[5][0]
        rf = False
    elif 'музей истории оренбурга' in req['request']['original_utterance'].lower():
        place = places[6][0]
        rf = False
    elif 'помощь' in req['request']['original_utterance'].lower():
        res['response'][
            'text'] = 'Для того, чтобы узнать информацию о какой-либо достопримечательности города Оренбурга нажмите на плитку с его названием.'
    elif 'что ты умеешь' in req['request']['original_utterance'].lower():
        res['response'][
            'text'] = 'Я рассказываю о различных достопримечательностях города Оренбурга и показываю, где они находятся'
    else:
        res['response']['text'] = 'Команда некорректна. Похоже, вы немного ошиблись.'
    res['response']['buttons'] = get_suggests(user_id)

    if not rf:
        con = sqlite3.connect("bdfa.db")

        # Создание курсора
        cur = con.cursor()

        # Выполнение запроса и получение всех результатов
        result = cur.execute(f"""SELECT answer FROM places WHERE name = '{place}'""").fetchall()
        res['response']['text'] = result[0][0]
    rf = True


def get_suggests(user_id):
    global places
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]
    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
