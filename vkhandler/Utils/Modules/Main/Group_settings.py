import re

from vkhandler.Utils.Modules.Config import vk
from vkhandler.Utils.Modules.Utils.decorators import command_handler, search_command_handler
from vkhandler.Utils.Modules.Utils.functional import return_error
from vkhandler.Utils.Modules.Utils.validators import is_bot, check_admin
from vkhandler.Utils.commands.errors import get_error_text
from vkhandler.Utils.commands.text import get_text_text
from vkhandler.models import Settings, Group


@command_handler('настройки', 'настр', 'settings')
def settings(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    chat_bd = bot[0]['chat_id']
    if bot[1]:
        if Settings.objects.filter(chat_id=chat_bd).exists():
            if Settings.objects.filter(chat_id=chat_bd).first().admin_access:
                if not check_admin(kwargs["peer_id"], kwargs["user_id"]):
                    return_error(**chat_id, error=get_error_text('access'))
    setup = Settings.objects.filter(chat_id=chat_bd).first()
    group = Group.objects.filter(chat_id=chat_bd).first()
    if group is None:
        return_error(error=get_error_text('need_group'), chat_id=chat_bd)
    template = get_text_text('settings', group.group, setup.admin_access, setup.add_time, setup.add_teacher,
                             setup.add_class, setup.autosend, setup.autosend_time, setup.notify_update)
    vk.messages.send(**chat_id, message=template, random_id=0)
    return


@search_command_handler(['ts ', ' '], ['as ', ' '], ['btn ', ' '], ['nu ', ' '],
                        ['cr ', ' '], ['tc ', ' '], ['tm ', ' '], ['oa ', ' '])
def change_settings(**kwargs):
    dict_with_names = {'ts': 'autosend_time', 'as': 'autosend', 'nu': 'notify_update', 'cr': 'add_class',
                       'tc': 'add_teacher', 'tm': 'add_time', 'oa': 'admin_access'}
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    chat_bd = bot[0]['chat_id']
    if bot[1]:
        check = Settings.objects.filter(chat_id=kwargs["chat_id"]).first().admin_access
        if check:
            if not check_admin(kwargs["peer_id"], kwargs["user_id"]):
                return_error(get_error_text('access'), kwargs["chat_id"])
    text = kwargs["splited"][1].lower()
    command = dict_with_names[kwargs["splited"][0].lower()]
    if re.match('^\\d\\d:\\d\\d$', text) is not None and command == 'autosend_time':
        splited_time = text.split(':')
        h = splited_time[0] if int(splited_time[0]) < 24 else 23
        m = splited_time[1] if int(splited_time[1]) < 60 else 59
        Settings.objects.filter(chat_id=chat_bd).update(**{command: str(f'{h}:{m}')})
    elif text.find(':') == -1 and command != 'autosend_time':
        command_update = True if text == 'true' else False
        Settings.objects.filter(chat_id=chat_bd).update(**{command: command_update})
    else:
        return_error(error=get_error_text('ts'), chat_id=chat_bd)
    vk.messages.send(**chat_id, message='Обновлено ✅', random_id=0)