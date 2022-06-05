import re

from config import vk
from models.models import Settings, Group
from utils.decorators import command_handler, search_command_handler
from utils.functional import return_error
from utils.validators import check_admin
from commands.text import get_text
from vk_methods_handler import EventInformation


@command_handler('настройки', 'настр', 'settings')
def settings(vk_object: EventInformation):
    if vk_object.group:
        if Settings.where(chat_id=str(vk_object.chat_id)).first() is not None:
            if Settings.where(chat_id=str(vk_object.chat_id)).first().admin_access:

                if not check_admin(vk_object.peer_id, vk_object.from_id):
                    return_error(**vk_object.send_id, error=get_text('access'))

    setup = Settings.where(chat_id=str(vk_object.chat_id)).first()
    group = Group.where(chat_id=str(vk_object.chat_id)).first()

    if group is None:
        return_error(error=get_text('need_group'), send_id=vk_object.send_id)
    setups = [group.group, setup.admin_access, setup.add_time, setup.add_teacher, setup.add_class, setup.autosend,
              setup.autosend_time, setup.notify_update]
    template = get_text('settings', *setups)
    vk.messages.send(**vk_object.send_id, message=template, random_id=0)
    return


@search_command_handler(['ts ', ' '], ['as ', ' '], ['btn ', ' '], ['nu ', ' '],
                        ['cr ', ' '], ['tc ', ' '], ['tm ', ' '], ['oa ', ' '])
def change_settings(vk_object: EventInformation):
    dict_with_names = {'ts': 'autosend_time', 'as': 'autosend', 'nu': 'notify_update', 'cr': 'add_class',
                       'tc': 'add_teacher', 'tm': 'add_time', 'oa': 'admin_access'}
    if vk_object.group:
        check = Settings.where(chat_id=str(vk_object.chat_id)).first().admin_access
        if check:
            if not check_admin(vk_object.peer_id, vk_object.from_id):
                return_error(get_text('access'), vk_object.chat_id)
    text = vk_object.splited_text[1].lower()
    command = dict_with_names[vk_object.splited_text[0].lower()]
    if re.match('^\\d\\d:\\d\\d$', text) is not None and command == 'autosend_time':
        splited_time = text.split(':')
        h = splited_time[0] if int(splited_time[0]) < 24 else 23
        m = splited_time[1] if int(splited_time[1]) < 60 else 59
        Settings.where(chat_id=str(vk_object.chat_id)).first().update(**{command: str(f"{h}:{m}")})

    elif text.find(':') == -1 and command != 'autosend_time':
        command_update = True if text == 'true' else False
        Settings.where(chat_id=str(vk_object.chat_id)).first().update(**{command: command_update})

    else:
        return_error(error=get_text('time_add_error'), send_id=vk_object.send_id)

    vk.messages.send(**vk_object.send_id, message='Обновлено ✅', random_id=0)
