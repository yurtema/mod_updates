import requests
import json

funcs = []


def message_handler(commands: list, strict=True):
    """
    Эаэ ну короче это типа декоратор, я сам уже не до конца помню как он работает.
    Если продекорированной функции дали в качестве text строку, в которой перый элемент есть в списке команд
    вернет результат выполнения этой продекорированной функции. Если нет, вернет нон.
    Если выключен стрикт, любое появление слова из списка команд в тексте стригерит обернутую функцию.
    """

    def _create_wrapper(f):
        def _wrapper(text, author_id):
            if strict:
                if text.split(' ')[0] in commands:
                    return f(text, author_id)
                return None
            else:
                if any([i in commands for i in text.split(' ')]):
                    return f(text, author_id)
                return None

        funcs.append(_wrapper)
        return _wrapper

    return _create_wrapper


@message_handler(commands=['/help'])
def send_help(text, author_id):
    """Отправить пользователю информацию по командам"""

    # Меня ужасно бесило что ide подчеркивал text и author_id как бессмысленные переменные.
    # Поэтому я дописал эту абсолютно бессмысленную строчку.
    text.find(author_id)

    return f'/add [id мода] [загрузчик] [версия] [название] \n/remove [название] \n/list'


@message_handler(commands=['/list'])
def list_mods(text, author_id):
    """Отправить список модов, за которыми попросил следить пользователь"""

    # Тут та же история с подчеркиванием
    text.find('')

    with open("../data/data.json") as file:
        data = json.load(file)

    # Я не буду объяснять этот катастрофический пиздец
    wait_list = "".join([f'{name} {" ".join(list(data[author_id][name].values()))} \n' for name in data[author_id]])

    return f'Ваш список ожидаемых модов: \n{wait_list}'


@message_handler(commands=['/add'])
def add(text, author_id):
    """
    /add id_мода нужный_загрузчик нужная_версия имя_мода
    После тонны проверок добавляет нужный мод со всей инфой в файл
    """
    # Проверка на наличие всех аргументов
    try:
        modid, loader, version = text.split(' ')[1:4]
        name = ' '.join(text.split(' ')[4:])
    except ValueError:
        return 'Вы неправильно внесли данные'

    # Проверка на наличие имени
    if name == '':
        return 'Вы не ввели название'

    # Проверка на наличие мода с нужным id на модринхе
    r = requests.get(f'https://api.modrinth.com/v2/project/{modid}')
    if r.status_code != 200:
        return 'Я не нашел мода с таким id'

    # Проверка на наличие нужного загрузчика у мода, найденного на прошлой проверке
    if loader not in r.json()['loaders']:
        return 'Такого загрузичка не существует для данного мода'

    # Загрузить файл, изменить там нужный мод и сохранить с изменениями
    with open("../data/data.json") as file:
        data = json.load(file)
    data[author_id][name.lower()] = {'id': modid, 'loader': loader, 'version': version}
    with open("../data/data.json", 'w') as file:
        json.dump(data, file)

    return f'Пришлю уведомление если мод {name} на загрузчике {loader} обновят до версии {version}'


@message_handler(commands=['/remove'])
def remove(text, author_id):
    """
    /remove имя_мода
    Проверить наличие мода с нужным именем в файле, удалить его
    """

    # Проверка на наличие агрумента
    if len(text.split(' ')) == 1:
        return 'Вы должна написать название мода после команды'

    # Достать из сообщения все слова после команды и объединить их в одну строку
    name = ' '.join(text.split(' ')[1:]).lower()

    # Проверить, есть ли запрошенный мод в файле. Если есть, удалить
    with open("../data/data.json") as file:
        data = json.load(file)
    if name in data[author_id]:
        del data[author_id][name]
    else:
        return 'Вы не просили уведомлять об обновлениях для этого мода'
    with open("../data/data.json", 'w') as file:
        json.dump(data, file)

    return f'Успешно удалил мод {name} из вашего списка ожидания'


def responde(text, author_id):
    """Функция, вызываемая снаружи. Прогоняет текст по всем функциям-хэндлерам, возвращает результат"""

    out = [res for i in funcs if (res := i(text, author_id))]

    if out:
        return out[0]
    else:
        return 'Нихера не понятно (команда не распознана)'
