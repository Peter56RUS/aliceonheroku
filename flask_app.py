from flask import Flask, request
import logging
import os
import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

places = [('Пешеходный мост через реку Урал',
           '''Красивый пешеходный мост соединяет два берега реки Урал, которая раньше считалась своеобразной разделительной чертой между Европейской и Азиатской частями света. Первое наплавное сооружение было построено здесь еще в 1835 году, вскоре его заменили на свайную конструкцию.

Свой современный вид мост приобрел в 1982 году, а использованные современные технологии позволили сделать его изящным, несмотря на большую — 220 метров — длину.

Середину моста отмечают своего рода пограничные столбы, на одной стороне которых написано «Азия», а на другой — «Европа». Перила украшены замочками, которые вешают сюда влюбленные, оборудован спуск к реке, есть подсветка.

Попасть на мост можно с Советской улицы, отсюда открывается красивый вид на детскую железную дорогу, Зауральную рощу, памятник Чкалову и набережную города.''',
           'ссылка на геокодер'),
          ('Памятник Пушкину и Далю',
           '''Парная скульптура, расположенная в центре сквера Полины Осипенко, была открыта в конце 20-го века, мастер — Надежда Петина. Мужчины изображены в пол-оборота друг к другу, во время беседы. Даль стоит с непокрытой головой, а на более низкого Пушкина одет цилиндр — так меньше бросается в глаза разница в росте.

Владимир Даль составлял компанию Пушкину во время его визита в Оренбург, предпринятого с целью узнать подробности о восстании Пугачева. Знакомые вместе побывали в церкви Петра и Павла, которая стояла на месте сквера до 30-х годов 20-го века. В память о ней основанию памятника была придана форма креста.''',
           "ссылка на геокодер"),
          ('Памятник Валерию Чкалову',
           '''Валерий Чкалов совершил множество испытательных полетов на различных самолетах, включая истребители и тяжелые бомбардировщики. Первым перелетел через Северный полюс, не совершив ни одной посадки, удостоен нескольких наград. Погиб во время очередного испытания, из-за неисправности.

Памятник летчику был установлен в 1953 году, спустя 15 лет после катастрофы. Скульптором выступил Исаак Менделеевич, архитектором — Виктор Андреев. 6-метровая бронзовая широкоплечая фигура возвышается на берегу Урала, лицом к летному училищу. Скульптор изобразил Валерия Чкалова в простой одежде и расслабленной позе, словно немного уставшим после очередного полета.''',
           'ссылка на геокодер')]


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
                "Памятник Пушкину",
                "Памятник Чкалову",
            ]
        }

        res['response'][
            'text'] = f'''Добрый день! Вас приветствует навык "Достопримечательности Оренбурга"! О чём вы хотите узнать?
Выберите одну из плиток ниже'''

        res['response']['buttons'] = get_suggests(user_id)
        return

    if 'пешеходный мост' in req['request']['original_utterance'].lower():
        res['response']['text'] = places[0][1]
    if 'памятник чкалову' in req['request']['original_utterance'].lower():
        res['response']['text'] = places[0][1]
    if 'памятник пушкину' in req['request']['original_utterance'].lower():
        res['response']['text'] = places[0][1]
    res['response']['buttons'] = get_suggests(user_id)


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
