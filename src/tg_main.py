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

    if last_check_hour == time.localtime().tm_hour:
        time.sleep(60)
        continue
    last_check_hour = time.localtime().tm_hour

    mods = {}
    mods_to_remove = {}

    for user in data:
        for mod in data[user]:
            mods.update({data[user][mod]['id']: data[user][mod]['loader']})

    versions = asyncio.run(api.create_processes(mods))

    for user in data:
        for mod in data[user]:
            if data[user][mod]["version"] in versions[data[user][mod]["id"]]:
                requests.post(
                    f'https://api.telegram.org/bot{private.tg_token}/sendMessage?chat_id={private.tg_chat_id}&text='
                    f'Мод {mod} из Вашего списка ожидания обновили на {data[user][mod]["version"]}')
                mods_to_remove.update({mod: user})

    for i in mods_to_remove:
        del data[mods_to_remove[i]][i]

    with open("../data/data.json", 'w') as file:
        json.dump(data, file)
