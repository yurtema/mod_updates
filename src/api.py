import asyncio
import requests


async def parse_modrinth(id_, loader_):
    """Возвращает словарь типа {id мода: [список версий]}"""
    versions = []
    link = f'https://api.modrinth.com/v2/project/{id_}/version?loaders=["{loader_}"]'

    # Сделать асинхронный запрос на апи модринха
    loop = asyncio.get_event_loop()
    r = (await loop.run_in_executor(None, requests.get, link)).json()

    # Апи вернет структуру [{.... game_versions:[] .....},
    #                       {.... game_versions:[] .....}]
    # Из этого надо вытащить список всех доступных версий
    for version in r:
        versions += version['game_versions']

    # И вернуть словарь нужного формата с удалением дубликатов
    return {id_: set(versions)}


async def create_processes(data: dict):
    """Создать асинхронные процессы для каждого элемента из полученного словаря типа {id мода: требуемый загрузчик}"""
    tasks = []

    # Получить result_list, список словарей с результатами запросов типа [{id мода: [версии]}, {id мода: [версии]}]
    for mod_id in data:
        tasks.append(asyncio.create_task(parse_modrinth(mod_id, data[mod_id])))
    result_list = await asyncio.gather(*tasks)

    # Вот тут список словарей превращается в один большой словарь
    result_dict = {}
    [result_dict.update(i) for i in result_list]

    return result_dict
