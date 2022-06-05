import json


def get_text(need_error: str, *args) -> str:
    """
    :param need_error: ключ для текста
    :param args: аргументы для заполнения текста
    :return: обработанный текст
    """
    with open("commands/commands.json", "r") as js:
        command_dict = json.load(js)
    return command_dict["texts"].get(need_error).format(*args)


def json_keyboard():
    return {
        "inline": True,
        "buttons": [[
            {"action": {"type": "text", "payload": "{\"button\": \"Сегодня\"}", "label": "Сегодня"},
             "color": "primary"},
            {"action": {"type": "text", "payload": "{\"button\": \"Завтра\"}", "label": "Завтра"},
             "color": "primary"}], [
            {"action": {"type": "text", "payload": "{\"button\": \"Эта\"}", "label": "Эта неделя"},
             "color": "primary"},
            {"action": {"type": "text", "payload": "{\"button\": \"Следующая\"}", "label": "Следующая неделя"},
             "color": "primary"}], [
            {"action": {"type": "text", "payload": "{\"button\": \"Изменения\"}", "label": "Изменения"},
             "color": "primary"},
            {"action": {"type": "text", "payload": "{\"button\": \"Звонки\"}", "label": "Звонки"},
             "color": "primary"}], [
            {"action": {"type": "text", "payload": "{\"button\": \"ЗИ\"}", "label": "(НЕ РАБОТАЕТ)Завтра [С изменениями]"},
             "color": "primary"},
            {"action": {"type": "text", "payload": "{\"button\": \"СИ\"}", "label": "(НЕ РАБОТАЕТ) Сегодня [С изменениями]"},
             "color": "primary"}]
        ]
    }


def json_group_keyboard():
    return {
        "inline": True,
        "buttons": [[
            {"action": {"type": "text", "label": "NF", "payload": "{\"button\": \"NF\"}"}, "color": "primary"},
            {"action": {"type": "text", "label": "NF", "payload": "{\"button\": \"NF\"}"}, "color": "primary"},
            {"action": {"type": "text", "label": "NF", "payload": "{\"button\": \"NF\"}"}, "color": "primary"},
        ], [
            {"action": {"type": "text", "label": "NF", "payload": "{\"button\": \"NF\"}"}, "color": "primary"},
            {"action": {"type": "text", "label": "NF", "payload": "{\"button\": \"NF\"}"}, "color": "primary"},
            {"action": {"type": "text", "label": "NF", "payload": "{\"button\": \"NF\"}"}, "color": "primary"},
        ], [
            {"action": {"type": "text", "label": "<-", "payload": "{\"button\": \"NF\"}"}, "color": "primary"},
            {"action": {"type": "text", "label": "->", "payload": "{\"button\": \"NF\"}"}, "color": "primary"},
        ]],
    }
