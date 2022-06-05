import json

import requests

from config import vk
from utils.decorators import command_handler, search_command_handler, json_command_handler
from utils.functional import return_error, isMember
from utils.schedulehelper import insert_into_peer, get_page_groups, insert_keyboard, set_page
from commands.text import json_group_keyboard, get_text

from vk_methods_handler import EventInformation


@command_handler('Помощь', 'help', 'помощь')
def help_command(vk_object: EventInformation, ):
    vk.messages.send(**vk_object.send_id, message=get_text('help_text'), random_id=0, disable_mentions=1)


@command_handler('zoom', 'коды zoom')
def zoom_codes(vk_object: EventInformation, ):
    if not vk_object.group:
        return_error('Данная функция работает только в беседах ❌.', send_id=vk_object.send_id)
    vk.messages.send(chat_id=vk_object.chat_id, random_id=0, message=get_text('zoom'))


@command_handler('все_группы', 'all groups', 'группы')
def all_groups(vk_object: EventInformation, ):
    response = '\n'.join(requests.get('https://time.ulstu.ru/api/1.0/groups').json()['response'])
    vk.messages.send(**vk_object.send_id, message=response, random_id=0)


@json_command_handler("group")
def groups(vk_object: EventInformation, ):
    isMember(vk_object.from_id, vk_object.send_id)
    response = requests.get('https://timetable.athene.tech/api/1.0/groups')
    groups_list = [item.lower() for item in response.json()['response']]

    if not vk_object.payload.lower() in groups_list:
        return_error(send_id=vk_object.send_id, error=get_text('group_not_found'))
    vk.messages.send(**vk_object.send_id, random_id=0, message=get_text('successful_add_group', vk_object.payload))
    insert_into_peer(vk_object.payload, str(vk_object.chat_id))


@json_command_handler("page")
def page(vk_object: EventInformation, ):
    groups = get_page_groups(int(vk_object.payload))
    keyboards = json_group_keyboard()
    insert_keyboard(keyboards, groups)
    set_page(int(vk_object.payload) - 1, int(vk_object.payload) + 1, keyboards)

    vk.messages.delete(peer_id=vk_object.peer_id, cmids=vk_object.conversation_message_id - 1, delete_for_all=1)
    vk.messages.delete(peer_id=vk_object.peer_id, cmids=vk_object.conversation_message_id, delete_for_all=1)
    vk.messages.send(**vk_object.send_id, message=".", random_id=0, keyboard=json.dumps(keyboards))


@search_command_handler(['добавить группу', ' '])
def add_chat_perfect(vk_object: EventInformation, ):
    isMember(vk_object.from_id, vk_object.send_id)
    keyboards = json_group_keyboard()
    insert_keyboard(keyboards, get_page_groups(0))
    set_page(0, 1, keyboards)
    vk.messages.send(**vk_object.send_id, message=".", random_id=0, keyboard=json.dumps(keyboards))


@search_command_handler(['добавь группу', ' '])
def add_chat(vk_object: EventInformation, ):
    group = vk_object.text[14:]
    response = requests.get('https://time.ulstu.ru/api/1.0/groups')
    groups_list = [item.lower() for item in response.json()['response']]
    if not group.lower() in groups_list:
        return_error(send_id=vk_object.send_id, error=get_text('group_not_found'))
    vk.messages.send(**vk_object.send_id, random_id=0, message=get_text('successful_add_group', group))
    insert_into_peer(group, str(vk_object.chat_id))
