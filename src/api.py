import asyncio
import requests


async def parse_modrinth(id_, loader_):
    """Возвращает словарь типа {id мода: [список версий]}"""
    versions = []
    link = f'https://api.modrinth.com/v2/project/{id_}/version?loaders=["{loader_}"]'

    loop = asyncio.get_event_loop()
    r = (await loop.run_in_executor(None, requests.get, link)).json()

    for version in r:
        versions += version['game_versions']

    return {id_: list(set(versions))}


async def create_processes(data: dict):
    tasks = []
    result_dict = {}

    for mod_id in data:
        tasks.append(asyncio.create_task(parse_modrinth(mod_id, data[mod_id])))

    result_list = await asyncio.gather(*tasks)
    [result_dict.update(i) for i in result_list]

    return result_dict

