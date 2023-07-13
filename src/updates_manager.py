funcs = []


def message_handler(commands: list, strict=True):
    def _wrap(f):
        def _wrapper(text, author_id):
            if strict:
                if text in commands:
                    return f(text, author_id)
                return None
            else:
                if any([i in commands for i in text.split(' ')]):
                    return f(text, author_id)
                return None

        funcs.append(_wrapper)
        return _wrapper

    return _wrap


@message_handler(commands=['/start'])
def wtf(text, author_id):
    return f'{author_id} высрал {text}'


@message_handler(commands=['/finish'])
def wtf(text, author_id):
    return f'{author_id} высрал {text}'


@message_handler(commands=['почему'], strict=False)
def wtf(text, author_id):
    return f'{author_id} высрал {text}'


def responde(text, author_id):
    out = [i(text, author_id) for i in funcs]
    try:
        out = [i for i in out if i][0]
        return out
    except IndexError:
        return 'Нихера не понятно (команда не распознана)'
