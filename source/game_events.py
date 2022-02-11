# -*- coding: utf-8 -*-
import numpy as np

events = [
    {
        'task': 'Хорошая новость! Шаномонтаж "Железный конь" завтра будет праздновать открытие, я договорился с его '
                'владельцем об уникальной возможности покупки акций специально для "{}"',
        'variants': [
            'Купить все на 100.000! Шиномонтаж - дело прибыльное, особенно с нашей погодой.',
            'Давайте купим половину акций на 50.000, так мы будем иметь крупную долю, но рисков меньше.',
            'Вложи только 10.000, а там посмотрим, как пойдет.',
            'Нашу компанию шиномонтажи не интересуют.',
        ],
        'consequences': [
            ['Ой-ой-ой, а я и не заметил, что в том районе уже давно работал другой хороший шиномонтаж, '
             'зачем мы вложились в этот... вы потеряли 100.000!', -100000],
            ['Мда, клиентов у этого шиномонтажа было мало, конкуренции с другим популярным заведением он не выдержал, изюменки не хватило. Как хорошо, что мы вложили не максимум.', -50000],
            ['Очередная пустышка этот ваш новый шиномонтаж. Вы немного потеряли!', -10000],
            ['Этот проект оказался провальным, но мы ничего ему не отдали, ничего и не сгорело, так держать!', 0],
        ],
    },
    # {
    #     'task': 'Босс, сотрудники хотят, чтобы наш оффис переехал в новое более просторное, комфортабельное и '
    #             'современное здание, готовы ли вы вложить в это 1.000.000?',
    #     'variants': [
    #         '',
    #         'Давайте купим половину акций на 50.000, так мы будем иметь крупную долю, но рисков меньше.',
    #     ],
    #     'consequences': [
    #         ['Ой-ой-ой, а я и не заметил, что в том районе уже давно работал другой хороший шиномонтаж, '
    #          'зачем мы вложились в этот... вы потеряли 100.000!', -100000],
    #         ['Мда, клиентов у этого шиномонтажа было мало, конкуренции с другим популярным заведением он не выдержал, изюменки не хватило. Как хорошо, что мы вложили не максимум.', -50000],
    #     ],
    # },
]
events_len = len(events)

time_out_texts = [
    'Ваша долгая  нерешительность вынудила совет директоров самостоятельно принять решение по текущему вопросу...'
]


class game_events:
    @staticmethod
    def get_new_event(exceptions):
        index = np.random.choice([i for i in range(len(events)) if i not in exceptions])
        return events[index], index

    @staticmethod
    def get_time_out_text():
        return time_out_texts[np.random.randint(0, len(time_out_texts))]


ge = game_events()
