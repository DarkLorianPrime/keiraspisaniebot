import json
import re
import sys
import time
from datetime import datetime, timedelta, date
from typing import Callable, Optional

sys.path.append("..")
from utils.validators import is_bot
from models.models import Settings, Group
from parser.parsed import send_pars

import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from main import group_settings, common_raspisanie, usual_functionality
from models import models
from config import vk
from utils.decorators import json_commands, commands, search_commands
from commands.text import get_text_text


def check_new_lessons() -> None:
    """
    Работает во 2 потоке, проверяет обновление изменений на сайте.
    """
    while True:
        if date.today().weekday() == 6:
            continue
        users = Settings.where(autosend=True).all()
        time_now = (datetime.now() + timedelta(hours=4, minutes=0)).time()
        for i in users:
            if time_now.replace(microsecond=0) == datetime.strptime(i.autosend_time, '%H:%M').time():
                group = Group.where(chat_id=i.chat_id).first()
                if group is None:
                    continue
                send_pars(group.group, i.chat_id)
        time.sleep(1)


def create_thread(target: Callable[[Optional[bytes]], None], *args) -> None:
    """
    Создание нового потока
    :param target: Функция для которой будет создан поток
    :param args: Аргументы этой функции (пока конкретно только байты).
    """
    thread = Thread(target=target, args=args)
    thread.start()


def new_message(response: dict) -> None:  # Если пришло новое сообщение - вторичная обработка запроса
    """

    :param response: Тело присланного запроса, превращенное в словарь
    Задает все нужные далее переменные, смотрит, была ли вызвана хоть одна команда. Если вызвана - то идет дальше.
    """
    text = response['object']['message']['text']
    lower = text.lower()
    chat_id = response['object']['message']['peer_id'] - 2000000000
    peer_id = response['object']['message']['peer_id']
    user_id = response['object']['message']['from_id']
    conversation_message_id = response['object']['message']['conversation_message_id']
    print(str(chat_id) + ' : ' + text)
    bot = True if peer_id != user_id else False
    if commands.get(lower) is not None:
        commands[lower](chat_id=chat_id, peer_id=peer_id, text=text, user_id=user_id, bot=bot)
        return

    for i in search_commands:
        if re.search(i, lower):
            splited = text.split(search_commands[i][1])
            if len(splited) > 1:
                search_commands[i][0](chat_id=chat_id, peer_id=peer_id, text=text, user_id=user_id, bot=bot,
                                      splited=splited, conversation_message_id=conversation_message_id)
                return

    if response['object']['message'].get('payload') is not None:
        payload_data = response['object']['message'].get('payload')
        load = json.loads(payload_data)
        button = load.get("button")
        if button is None:
            button = "page"
        if load.get("button") is None and load.get(button) is None:
            button = "group"
        if json_commands.get(button) is not None:
            json_commands[button](chat_id=chat_id, peer_id=peer_id, text=text, user_id=user_id, bot=bot,
                                  payload=load.get(button), conversation_message_id=conversation_message_id)
            return
    if response['object']['message'].get('action') is not None:
        action = response['object']['message']['action']
        if action['type'] == 'chat_invite_user' and action['member_id'] == -169175932:
            print('invited in new chat')
            vk.messages.send(chat_id=chat_id, random_id=0, message=get_text_text('hello'))


def standart_handler(body: bytes) -> None:  # Первичная обработка присланного запроса
    response = json.loads(body.decode())
    type_response = response.get('type')
    try:
        if type_response == 'message_new':
            new_message(response)
    except Exception as e:
        traceback.print_exc()
        bot = is_bot(chat_id=response['object']['message']['peer_id'] - 2000000000)
        if "SendedMessage" not in traceback.format_exc():  # Костыль TO-DO
            vk.messages.send(**bot[0]["chat_dict"], random_id=0,
                             message="При обработке возникла ошибка.\nЗапрос уже передан тех. администратору.")
            vk.messages.send(chat_id=14, message=f"ДАЛБАЕБ, ТЫ ЧЕТ СЛОМАЛ. ЛОГ ОШИБКИ: \n{e}\n", random_id=0)


class HttpProcessor(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        """
        Получает запросы, возвращает 200 "ок" и отправляет дальше на обработку. Сердце сервера.
        """
        self.send_response(200, "ok")
        self.send_header("content-type", "application/text")
        self.end_headers()
        self.wfile.write(b"ok")
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        create_thread(standart_handler, post_data)


create_thread(check_new_lessons)  # Создание потока авто-получения изменений
print("start server")
server = HTTPServer(("127.0.0.1", 5020), HttpProcessor)
server.serve_forever()  # Запуск сервера для получения обновлений
