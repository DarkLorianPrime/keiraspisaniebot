import json

import requests

from vkhandler.Utils.Modules.Config import vk
from vkhandler.Utils.Modules.Utils.decorators import command_handler, search_command_handler, json_command_handler
from vkhandler.Utils.Modules.Utils.functional import in_group_chat_error, return_error, isMember
from vkhandler.Utils.Modules.Utils.validators import is_bot
from vkhandler.Utils.commands.errors import get_error_text
from vkhandler.Utils.commands.text import get_text_text, json_group_keyboard
from vkhandler.models import Group, Settings
from bs4 import BeautifulSoup


@command_handler('Помощь', 'help', 'помощь')
def help_command(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    vk.messages.send(**chat_id, message=get_text_text('help_text'), random_id=0, disable_mentions=1)


@command_handler('zoom', 'коды zoom')
def zoom_codes(**kwargs):
    in_group_chat_error(kwargs["bot"], kwargs["user_id"])
    vk.messages.send(chat_id=kwargs["chat_id"], random_id=0, message=get_text_text('zoom'))


@command_handler('все_группы', 'all groups', 'группы')
def all_groups(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    response = '\n'.join(requests.get('https://timetable.athene.tech/api/1.0/groups').json()['response'])
    vk.messages.send(**chat_id, message=response, random_id=0)


def get_page_groups(number):
    groups, groups_0, groups_1 = [], 0, 0
    page = requests.get("https://lk.ulstu.ru/timetable/shared/schedule/Часть%203%20–%20МФ,%20КЭИ/raspisan.html").content
    groups.append([])
    for element in BeautifulSoup(page, "lxml").find_all("font"):
        if element.text != "":
            if groups_1 != 6:
                groups[groups_0].append(element.text)
                groups_1 += 1
                continue
            groups_1 = 0
            groups_0 += 1
            groups.append([])
    del groups[0]
    return groups[number + 1]


def insert_keyboard(keyboard, groups):
    json_line = 0
    json_row = 0
    if len(groups) < 6:
        return
    for group in groups:
        keyboard["buttons"][json_line][json_row]["action"]["label"] = group
        keyboard["buttons"][json_line][json_row]["action"]["payload"] = '{\"group\": \"%s\"}' % group
        if json_row == 2:
            json_line += 1
            json_row = 0
            continue
        json_row += 1


def set_page(first, second, keyboard):
    keyboard["buttons"][-1][0]["action"]["payload"] = '{\"page\": \"%s\"}' % first
    keyboard["buttons"][-1][1]["action"]["payload"] = '{\"page\": \"%s\"}' % second


@json_command_handler("group")
def groups(**kwargs):
    isMember(kwargs["user_id"], kwargs["chat_id"])
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]["chat_id"]
    response = requests.get('https://timetable.athene.tech/api/1.0/groups')
    groups_list = [item.lower() for item in response.json()['response']]
    if not kwargs["payload"].lower() in groups_list:
        return_error(chat_id=chat_id, error=get_error_text('group_not_found'))
    vk.messages.send(**bot[0]["chat_dict"], random_id=0, message=get_error_text('succ_group', kwargs["payload"]))
    Group.objects.update_or_create(chat_id=chat_id, defaults={'group': kwargs["payload"], 'chat_id': chat_id})
    Settings.objects.get_or_create(chat_id=bot[0]["chat_id"])


@json_command_handler("page")
def page(**kwargs):
    isMember(kwargs["user_id"], kwargs["chat_id"])
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    groups = get_page_groups(int(kwargs["payload"]))
    keyboards = json_group_keyboard()
    insert_keyboard(keyboards, groups)
    set_page(int(kwargs["payload"]) - 1, int(kwargs["payload"]) + 1, keyboards)
    vk.messages.delete(peer_id=kwargs["peer_id"], cmids=kwargs["conversation_message_id"] - 1, delete_for_all=1)
    vk.messages.delete(peer_id=kwargs["peer_id"], cmids=kwargs["conversation_message_id"], delete_for_all=1)
    vk.messages.send(**bot[0]["chat_dict"], message=".", random_id=0, keyboard=json.dumps(keyboards))


@search_command_handler(['добавить группу', ' '])
def add_chat_perfect(**kwargs):
    isMember(kwargs["user_id"], kwargs["chat_id"])
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    keyboards = json_group_keyboard()
    insert_keyboard(keyboards, get_page_groups(0))
    set_page(0, 1, keyboards)
    vk.messages.send(**bot[0]["chat_dict"], message=".", random_id=0, keyboard=json.dumps(keyboards))


@search_command_handler(['добавь группу', ' '])
def add_chat(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    chat_bd = bot[0]['chat_id']
    group = kwargs["text"][14:]
    response = requests.get('https://timetable.athene.tech/api/1.0/groups')
    groups_list = [item.lower() for item in response.json()['response']]
    if not group.lower() in groups_list:
        return_error(chat_id=chat_bd, error=get_error_text('group_not_found'))
    vk.messages.send(**chat_id, random_id=0, message=get_error_text('succ_group', group))
    Group.objects.update_or_create(chat_id=chat_bd, defaults={'group': group, 'chat_id': chat_bd})
    Settings.objects.get_or_create(chat_id=chat_bd)


@search_command_handler(['уведомление:', ' '])
def send_notify_all(*args):
    # text = args[2][13:]
    # text += '\n\n🔁 если вы не подписаны на группу, то подпишитесь: @keiraspisanie (Бот расписания) 🔁\n❗ Уведомление о обновлении можно отключить в настройках ❗'
    # settings_chats = Settings.objects.filter(notify_update=True).values_list('chat_id')
    # for chat in settings_chats:
    #     chats = {'chat_id': chat[0]} if int(chat[0]) < 2000000 else {'user_id': chat[0]}
    #     print(chat[0])
    #     vk.messages.send(**chats, message=text, random_id=0)
    return
