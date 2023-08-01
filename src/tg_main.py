import json
import time
import asyncio
import requests
import urllib3.exceptions
from updates_manager import responde
from api import create_processes

last_check_hour = None

with open('../data/private.json') as file:
    private = json.load(file)

# Получить изначальный offset
r = requests.get(f'https://api.telegram.org/bot{private["tg_token"]}/getUpdates').json()['result']
if r:
    offset = r[-1]['update_id'] + 1
else:
    offset = 0


def handle_updates():
    """
    Функция запрашивает новые сообщения с апи тг с помощью offset, прогоняет по условиям для генерации ответа.
    Ничего не возвращает, в конце сама отсылает нужные сообщения.
    Работает с одним апдейтом за раз.
    """

    global offset

    # Попробовать тыкнуть апи телеги, чтобы получить новые сообщения.
    # Если чето пойдет не так, подождать минуту и тыкнуть снова.
    try:
        update = requests.get(f'https://api.telegram.org/bot{private["tg_token"]}/'
                              f'getUpdates?offset={offset}').json()['result']
    except urllib3.exceptions.ProtocolError:
        time.sleep(60)
        return

    # Если никаких новых сообщений нет, ничего не делать (нет, что вы, какая излишняя документация?)
    if not update:
        return

    update = update[0]
    offset = update['update_id'] + 1
    text = update['message']['text']
    author_id = str(update['message']['chat']['id'])

    print(f'[{time.asctime()}] {author_id}: {text}')

    # Прокатить команду по responde для получения строчки с ответом и отправить запрос на апи для публикации сообщения.
    requests.post(f'https://api.telegram.org/bot{private["tg_token"]}/sendMessage?chat_id={author_id}&'
                  f'text={responde(text, author_id)}')


while True:

    # Если последняя проверка была меньше часа назад, обработать входящие запросы
    if last_check_hour == time.localtime().tm_hour:
        handle_updates()
        continue

    # Если больше, запустить проверку обновлений для модов

    # Загруить список запрашиваемых модов
    with open("../data/data.json") as file:
        data = json.load(file)

    # Создать словарь типа {id мода: требуемый загрузчик}
    mods = {data[user][mod]['id']: data[user][mod]['loader'] for user in data for mod in data[user]}

    # Передать этот словарь в api.py, получить словарь типа {id мода: [существующие версии]}
    versions = asyncio.run(create_processes(mods))

    # {пользователь: [список модов, которые надо удалить из бд]}
    mods_to_remove = {}
    # временынй список, создаваемый для каждого пользователя
    mods_to_remove_for_user = []

    for user in data:

        for mod in data[user]:
            # Для каждого мода каждого пользователя проверить, есть ли требуемая версия в списке доступных
            if data[user][mod]["version"] in versions[data[user][mod]["id"]]:
                # Если есть, кинуть сообщение пользователю и добавить мод в список на удаление из бд
                requests.post(
                    f'https://api.telegram.org/bot{private["tg_token"]}/sendMessage?chat_id={user}&text='
                    f'Мод {mod} из Вашего списка ожидания обновили на {data[user][mod]["version"]}')
                mods_to_remove_for_user.append(mod)

        # Создать словарь тиа {пользователь: [список модов, которые надо удалить из бд]}
        mods_to_remove[user] = mods_to_remove_for_user
        mods_to_remove_for_user = []

    # Удалить все нужные моды из списка
    for user in mods_to_remove:
        for mod in mods_to_remove[user]:
            del data[user][mod]

    # Если чето удалили, обновить файл
    if mods_to_remove != {}:
        with open("../data/data.json", 'w') as file:
            json.dump(data, file)
