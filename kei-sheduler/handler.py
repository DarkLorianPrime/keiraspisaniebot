import json
import re
import sys
import time
from datetime import datetime, date
from typing import Callable, Optional

from colorama import Fore

from commands import text
from vk_methods_handler import EventInformation

sys.path.append("..")

from models import models # noqa
from main import settings, shedule, extrafeatures # noqa
from models.models import Settings, Group # noqa
from parser.schedulechanges import send_changes # noqa

import traceback # noqa
from http.server import BaseHTTPRequestHandler, HTTPServer # noqa
from threading import Thread # noqa

from config import vk # noqa
from utils.decorators import json_commands, commands, search_commands # noqa
from commands.text import get_text # noqa


def check_new_lessons() -> None:
    """
    Работает во 2 потоке, проверяет обновление изменений на сайте.
    """
    while True:
        if date.today().weekday() == 5:
            continue
        users = Settings.where(autosend=True).all()
        time_now = datetime.now().time()
        for i in users:
            if time_now.replace(microsecond=0) == datetime.strptime(i.autosend_time, '%H:%M').time():
                group = Group.where(chat_id=i.chat_id).first()
                if group is None:
                    continue
                send_changes(group.group, i.chat_id)
        time.sleep(1)


def create_thread(target: Callable[[Optional[bytes]], None], *args) -> None:
    """
    Создание нового потока\n
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
    vk_object = EventInformation(response)
    time = f"{Fore.RED}[{Fore.MAGENTA}{datetime.now().strftime('%d/%h/%Y %H:%M:%S')}{Fore.RED}]{Fore.RESET}"
    print(f"{time} {Fore.LIGHTCYAN_EX}{vk_object.chat_id}{Fore.RESET}: {Fore.WHITE}{vk_object.text}{Fore.RESET}")
    if commands.get(vk_object.lower) is not None:
        commands[vk_object.lower](vk_object)
        return

    for i in search_commands:
        if re.search(i, vk_object.lower):
            splited = vk_object.text.split(search_commands[i][1])
            if len(splited) > 1:
                vk_object.splited_text = splited
                search_commands[i][0](vk_object)
                return

    if response['object']['message'].get('payload') is not None:
        payload_data = vk_object.payload
        load = json.loads(payload_data)
        button = load.get("button")
        if button is None:
            button = "page"
        if load.get("button") is None and load.get(button) is None:
            button = "group"
        vk_object.payload = load.get(button)
        if json_commands.get(button) is not None:
            json_commands[button](vk_object)
            return

    if response['object']['message'].get('action') is not None:
        action = response['object']['message']['action']
        if action['type'] == 'chat_invite_user' and action['member_id'] == -145807659:
            vk.messages.send(chat_id=vk_object.chat_id, random_id=0, message=get_text('hello'))


def standart_handler(body: bytes) -> None:  # Первичная обработка присланного запроса
    """
    Разбирает байты на словарь и отправляет на дальнейшую обработку.
    """
    response = json.loads(body.decode())
    type_response = response.get('type')
    try:
        if type_response == 'message_new':
            new_message(response)
    except Exception as e:
        traceback.print_exc()
        if "SendedMessage" not in traceback.format_exc():  # Костыль TO-DO
            peer_id = response['object']['message']['peer_id']
            vk.messages.send(peer_id=peer_id, random_id=0, message=text.get_text("error"))
            vk.messages.send(chat_id=14, message=f"ДАЛБАЕБ, ТЫ ЧЕТ СЛОМАЛ. ЛОГ ОШИБКИ: \n{e}\n", random_id=0)


class HttpProcessor(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        """
        Получает запросы, возвращает 200 "ок" и отправляет дальше на обработку. Сердце сервера.
        """
        self.send_ok()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        create_thread(standart_handler, post_data)

    def send_ok(self) -> None:
        """
        Отправляет 200 ok в ответ.
        :return:
        """
        self.send_response(200, "ok")
        self.send_header("content-type", "application/text")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_request(self, *args, **kwargs) -> None:
        ...


create_thread(check_new_lessons)  # Создание потока авто-получения изменений
print("start server")
server = HTTPServer(("127.0.0.1", 5020), HttpProcessor)
server.serve_forever()  # Запуск сервера для получения обновлений
