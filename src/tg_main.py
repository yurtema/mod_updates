import json
import time
import api
import asyncio
import requests
import data.private as private

last_check_hour = None

with open("../data/data.json") as file:
    data = json.load(file)

while True:

    # Если последняя проверка была меньше часа назад, подождать еще минуту
    if last_check_hour == time.localtime().tm_hour:
        time.sleep(60)
        continue
    last_check_hour = time.localtime().tm_hour

    mods = {}

    # Создать словарь типа {id мода: требуемый загрузчик}
    for user in data:
        for mod in data[user]:
            mods.update({data[user][mod]['id']: data[user][mod]['loader']})

    # Передать этот словарь в api.py, получить словарь типа {id мода: суещствующие версии}
    versions = asyncio.run(api.create_processes(mods))

    mods_to_remove = {}
    mods_to_remove_for_user = []

    for user in data:

        for mod in data[user]:
            # Для каждого мода каждого пользователя проверить, есть ли требуемая версия в списке доступных
            if data[user][mod]["version"] in versions[data[user][mod]["id"]]:
                # Если есть, кинуть сообщение пользователю и добавить мод в список на удаление из бд
                requests.post(
                    f'https://api.telegram.org/bot{private.tg_token}/sendMessage?chat_id={private.tg_chat_id}&text='
                    f'Мод {mod} из Вашего списка ожидания обновили на {data[user][mod]["version"]}')
                mods_to_remove_for_user.append(mod)

        # Создать словарь тиа {пользователь: [список модов, которые надо удалить из бд]}
        mods_to_remove[user] = mods_to_remove_for_user
        mods_to_remove_for_user = []

    # Удалить все моды из списка
    for user in mods_to_remove:
        for mod in mods_to_remove[user]:
            del data[user][mod]

    with open("../data/data.json", 'w') as file:
        json.dump(data, file)


