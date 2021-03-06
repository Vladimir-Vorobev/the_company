# -*- coding: utf-8 -*-
import numpy as np
from copy import deepcopy

events = [
    {
        'task': 'Хорошая новость! Шаномонтаж "Железный конь" завтра будет праздновать открытие, я договорился с его владельцем об уникальной возможности покупки акций специально для нашей компании.',
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
        'image': 'tire_service',
    },
    {
        'task': 'Босс, сотрудники хотят, чтобы наш офис переехал в новое более просторное, комфортабельное и современное здание, готовы ли вы вложить в это 1.000.000?',
        'variants': [
            'Да, давно пора!',
            'Хмм, нет, нам и так хорошо.',
        ],
        'consequences': [
            ['Все сотрудники счастливы! Да и работать стали лучше, вы в итоге получили 100.000', 100000],
            ['Сотрудники в ярости, ведь в старом здании даже свет не всегда работал! Часть из них уволилась, '
             'репутационные потери составляют 1.500.000!', -1500000],
        ],
        'image': 'office',
    },
    {
        'task': 'Босс, не хотите ли вы купить пентхаус в ближайшем казино?',
        'variants': [
            'Да, буду там иногда оттягиваться. Цена в 5.000.000 меня не пугает!',
            'Нет, не то время сейчас, чтобы пентхаусы покупать...',
        ],
        'consequences': [
            ['Сотрудники недовольны! Вместо решения проблем компании вы тратите целое состояние, часть специалистов уволилась, репутационные потери и траты на пентхаус 5.500.000', -5500000],
            ['Верно, надо работать не ради пентхауса, а ради компании! Вы ничего не потеряли.', 0],
        ],
        'image': 'casino',
    },
    {
        'task': 'Псс, шеф, у меня есть одно достаточно рискованное предложение: если мы вложимся в новую криптовалюту моего знакомого, то мы сможем быстро разбогатеть... или потерять, вам решать!',
        'variants': [
            'Была не была, вкладываю 3.000.000!',
            'Друг говоришь... давай выделим 1.000.000.',
            'Да, потерять можем, поэтому выделяем лишь 250.000.',
            'Нет, риски я не люблю.'
        ],
        'consequences': [
            ['Да, вы сорвали куш! 5.000.000!!!', 5000000],
            ['Эх, могли бы и побольше вложить, но вы выручили 500.000.', 500000],
            ['Криптой никто не заинтересовался, слишком мало инвестиций... вы потеряли вложения.', -250000],
            ['Кто не инвестирует, тот не рискует. Я смотрю, это про вас. Конкуренты пользуются вашим бездействием, '
             'репутационные потери в 50.000', -50000],
        ],
        'image': 'stock_market',
    },
    {
        'task': 'Какой-то вандал побил ваш элитный спорткар! Что будете делать?',
        'variants': [
            'Срочно его в автомастерскую, да заплати механику, чтобы без очереди!',
            'Пусть починят, как смогут.',
            'Я сам потом им займусь, сейчас работать надо.',
        ],
        'consequences': [
            ['Все в офисе переполошились из-за вашей машины, да и ремонт влетел в копеечку... расходы на механика и '
             'репутационные потери составляют 1.000.000!', -1000000],
            ['Что ж, ваш спорткар как новенький, но это обошлось в 350.000', -350000],
            ['Сотрудники восхищены вашим спокойствием и прибытием на работу на автобусе, но ваш доход оценивают всего в 10.000. Видимо, не ваш день.', 10000],
        ],
        'image': 'tire_service',
    },
    # 5
    {
        'task': 'Местное казино предложило нам совместную промо-акцию, примем предложение?',
        'variants': [
            'Да, конечно!',
            'Нет, здесь какой-то подвох.',
        ],
        'consequences': [
            ['Отличное предложение, совместная промо-акция привела в наше агенство новых клиентов! Выручка 1.500.000.', 1500000],
            ['Подвоха не было, предложением воспользовались конкуренты, наши потери 2.500.000.', -2500000],
        ],
        'image': 'casino',
    },
    {
        'task': 'У нас скоро встреча с инвесторами, а у вас нет подходящего костюма, что будем делать?!',
        'variants': [
            'Выбери мне самый дорогой костюм, аксессуары и смени интерьер в зале, где будет проходить встреча, надо впечатлить инвесторов!',
            'Ну, купи что-нибудь приличное, а там посмотрим.',
            'Зачем мне костюм, только лишние расходы!',
            'Нет костюма - отмени встречу!'
        ],
        'consequences': [
            ['Плохие новости! Дорогой костюм и ремонт обошлись в 5.000.000, но инвесторы почти сразу ушли со встречи, посчитав, что они не хотят инвестировать в тех, у кого и так много денег.', -5000000],
            ['Отлично, вы выглядели как настоящий управленец, но без лишнего пафоса, мы привлекли 2.000.000 инвестиций.', 2000000],
            ['Инвесторы смотрели на ваш неряшливый вид с большим подозрением, в итоге они сказали, что перезвонят.', 0],
            ['Зря вы так, к нам должен был прийти известный инвестор, наш отказ оскорбил его, репутационные потери 1.000.000', -1000000],
        ],
        'image': 'office',
    },
    {
        'task': 'Время заняться основным делом компании - инвестициями! Вложим средства в ПИФ с доходностью 70% годовых?',
        'variants': [
            'Ого, 70% годовых? Вложи 4.500.000!',
            'Звучит неплохо, инвестируй 1.500.000.',
            'Для начала давай попробуем 500.000.',
            'Звучит подозрительно как-то, пока вкладываться не будем.'
        ],
        'consequences': [
            ['Теряете хватку! Вы вложились в слишком рискованный ПИФ! Потери вложенных средств и репутационные потери составляют 6.000.000.', -6000000],
            ['Риски были слишком высоки! Теперь мы несколько упали в глазах других, общие потери 3.000.000', -3000000],
            ['500.000 было не жалко... но не стоит так больше вкладываться. Общие потери 1.500.000', -1500000],
            ['Ого, как хорошо, что мы не вложили в этот ПИФ деньги, это были мошенники!', 0],
        ],
        'image': 'stock_market',
    },
    {
        'task': 'Босс, а помните, с чего вы начали свой путь? С выигрыша в казино! Не хотите испытать удачу еще раз?',
        'variants': [
            'Да! Я сыграю на 5.000.000, наверняка что-то выиграю!',
            'Да, сыграю на 1.000.000.',
            'Да, сыграю на 500.000.',
            'Нет, для моей удачи вхатит испытаний!',
        ],
        'consequences': [
            ['Эх-эх-эх, ваша удача не прошла испытания второй раз, вы потеряли все и понесли репутационные потери. Общие потери 6.000.000.', -6000000],
            ['Надеюсь, вы хорошо провели время... ведь оно обошлось вам в 2.000.000 с репутационными потерями!', -2000000],
            ['Удача отвернулась от вас, вы потеряли 500.000, хорошо, что не играли на большие суммы.', -500000],
            ['Хорошее решение. Обычно такого рода удача бывает раз в жизни!', 0],
        ],
        'image': 'casino',
    },
    {
        'task': 'Время заняться основным делом компании - инвестициями! Вложим средства в ПИФ с доходностью 20% годовых?',
        'variants': [
            'Почему бы и нет? Вложи 4.500.000!',
            'Звучит неплохо, инвестируй 1.500.000.',
            'Для начала давай попробуем 500.000.',
            'Звучит подозрительно как-то, пока вкладываться не будем.'
        ],
        'consequences': [
            ['Отличное вложение! Наша прибыль 900.000.', 900000],
            ['Можно было бы и побольше вложить, но и так неплохо: прибыль 300.000.', 300000],
            ['Вложили немного - получили немного. Прибыль 100.000.', 100000],
            ['Ну и зря, стоило попробовать, как это сделали конкуренты! Наши потери 1.000.000.', -1000000],
        ],
        'image': 'stock_market',
    },
    # 10
    {
        'task': 'Вы заработались допоздна, желаете пойти спать и оставить все на завтра или сегодня закончите?',
        'variants': [
            'Пойду посплю, утро вечера мудренее.',
            'Нет, никогда не оставлю на завтра то, что можно сделать сегодня!',
        ],
        'consequences': [
            ['Отличное вложение! Вы успели отдохнуть и на следующий день сделали больше дел. Прибыль 100.000.', 100000],
            ['Вы доделали все дела в этот вечер, но из-за усталости перепутали получателя письма, и важная информация ушла к конкурентам! Потери 5.000.000!', -5000000],
        ],
        'image': 'office',
    },
    {
        'task': 'Время инвестиций! Желаете инвестировать в строящееся казино?',
        'variants': [
            'Да! Вложи 7.500.000, разбогатеем!',
            'Инвестируй 5.000.000.',
            'Инвестируй 2.500.000, они пока только на этапе котлована.',
            'Ничего не вкладывай, не нравится мне эти люди.',
        ],
        'consequences': [
            ['Вы нарвались на мошенников! Но, к счастью, с такой крупной суммой им сбежать не удалось, мы вернули свои вложения и дополнительно отсудили 100.000.', 100000],
            ['Вы нарвались на мошенников! Но, к счастью, с такой крупной суммой им сбежать не удалось, мы вернули свои вложения и дополнительно отсудили 50.000.', 50000],
            ['Вы нарвались на мошенников, и они сумели скрыться со всей суммой вложения. Очень жаль, но вы потеряли 2.500.000.', -2500000],
            ['Ладно, ничего не вложили - ничего не потеряли. Но и не заработали...', 0],
        ],
        'image': 'casino',
    },
    {
        'task': 'Фирма, занимающаяся образованием, предлагает скидки на корпоративные курсы. Хотите повысить квалификацию сотрудников?',
        'variants': [
            'Да, конечно, выдели 1.500.000.',
            'Нет, наши сотрудники и так самые лучшие.',
        ],
        'consequences': [
            ['Мудрое перспективное решение! Повышение квалификации сотрудников уже дало свои плоды, поэтому итоговые потери всего 100.000', -100000],
            ['Рынок стремительно меняется, наши сотрудники старой закалки перестали выдерживать конкуренцию. Потери 1.500.000.', -1500000],
        ],
        'image': 'office',
    },
    {
        'task': 'К нам с внезапной проверкой инспекция по ценным бумагам, у нас точно с отчетностью все гладко, что будем делать?',
        'variants': [
            'Дай им 3.000.000 и пусть отвяжутся, я занят!',
            'Скажи, что мы сегодня не работаем.',
            'А что у нас может быть не так? Пусть делают свою работу, окажи им содействие.',
        ],
        'consequences': [
            ['Это была роковая ошибка! За дачу взятки наши потери составили 8.000.000!', -8000000],
            ['Инспекторы заподозрили неладное и провели более тщательную проверку, выписали штраф на 3.000.000', -3000000],
            ['Инспекторы выявили нарушения, но за их быстрое устранение и оказанное содействие штраф нам не выписали', 0],
        ],
        'image': 'stock_market',
    },
    {
        'task': 'Делегация дружественной иностранной компании-партнера прибывает к нам с визитом. Предоставить ей кортеж?',
        'variants': [
            'Конечно! Только сначала приведите его в порядок, я выделяю на это 500.000.',
            'Да, но не стоит проводить техническую проверку, подумаешь, не пользовался им никто давно, и так доедут, зато почти бесплатно.',
            'Нет, кортеж им не нужен, сами доберутся.',
        ],
        'consequences': [
            ['Партнеры рады вашему гостеприимству, вы успешно заключили контракт на 2.000.000.', 2000000],
            ['Неисправленное транспортное средство кортежа попало в аварию, делегация возмущенно покинула нашу страну, разорвав с нами контракт на 1.000.000', -1000000],
            ['Делегация долго стояла в пробках на такси, очень устала, и вы в итоге не заключили никаких новых контрактов.', 0],
        ],
        'image': 'tire_service',
    },
    # 15

]
events_len = len(events)

time_out_texts = [
    'Ваша долгая  нерешительность вынудила совет директоров самостоятельно принять решение по текущему вопросу...',
    'Компания не может так долго ждать! Совет директоров принял решение за вас...',
    'Что с вами? Ау. Мы принимем решение без вас...',
]


class game_events:
    @staticmethod
    def get_new_event(exceptions):
        index = int(np.random.choice([i for i in range(len(events)) if i not in exceptions]))
        return deepcopy(events[index]), index

    @staticmethod
    def get_time_out_text():
        return time_out_texts[np.random.randint(0, len(time_out_texts))]


ge = game_events()
