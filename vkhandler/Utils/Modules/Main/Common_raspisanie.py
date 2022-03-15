import json

from vkhandler.Utils.Modules.Config import vk, weeks
from vkhandler.Utils.Modules.Utils.decorators import json_command_handler, command_handler
from vkhandler.Utils.Modules.Utils.functional import isMember
from vkhandler.Utils.Modules.Utils.raspisanie import get_info, week_company, get_week
from vkhandler.Utils.Modules.Utils.validators import is_bot
from vkhandler.Utils.Parser import parsed
from vkhandler.Utils.commands.text import get_text_text, json_keyboard
from vkhandler.models import Group


@json_command_handler('Сегодня', 'today')
def today(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    chat_bd = bot[0]['chat_id']
    info = get_info(chat_bd, notsunday=True)
    timetable = info['timetable']['weeks'][info["to_days"]["week_num"]]['days'][info["to_days"]["day_int"]]
    vk.messages.send(**chat_id, message=week_company(**info["to_days"], timetable=timetable, week=False), random_id=0)


@json_command_handler('время', 'Звонки', 'конец пары')
def get_time(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    vk.messages.send(**chat_id, message=get_text_text('time'), random_id=0)


@json_command_handler('Завтра', 'tommorow')
def tomorrow(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    chat_bd = bot[0]['chat_id']
    isMember(kwargs["user_id"], chat_bd)
    info = get_info(chat_bd)
    info["to_days"]["day_int"] += 1
    if info["to_days"]["day_int"] == 6:
        vk.messages.send(**chat_id, message="Завтра воскресение 🤔", random_id=0)
    timetable = info['timetable']['weeks'][info["to_days"]["week_num"]]['days'][info["to_days"]["day_int"]]
    vk.messages.send(**chat_id, message=week_company(**info["to_days"], timetable=timetable), random_id=0)


@json_command_handler('Следующая', 'Следующая неделя', 'След.')
def next_week(**kwargs):
    isMember(kwargs["user_id"], kwargs["chat_id"])
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    chat_bd = bot[0]['chat_id']
    vk.messages.send(**chat_id, message=get_week(that_week=False, chat_id=chat_bd), random_id=0)


@json_command_handler('Эта', 'Эта неделя', 'Расписание на неделю')
def this_week(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    vk.messages.send(**bot[0]["chat_dict"], message=get_week(that_week=True, chat_id=bot[0]["chat_id"]), random_id=0)


@command_handler('расписание', 'raspisan', 'расп')
def button_get_lessons(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    payload = json.dumps(json_keyboard())
    vk.messages.send(**bot[0]['chat_dict'], message='Расписание:', keyboard=payload, random_id=0)


@command_handler("понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресение")
def one_of_the_day(**kwargs):
    isMember(kwargs["user_id"], kwargs["chat_id"])
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    info = get_info(bot[0]['chat_id'])
    days = weeks.index(kwargs["text"].capitalize())
    timetable = info['timetable']['weeks'][info["to_days"]["week_num"]]['days'][days]
    del info["to_days"]["day_int"]
    vk.messages.send(**chat_id,
                     message=week_company(**info["to_days"], timetable=timetable, day_int=days, week=False),
                     random_id=0)


@json_command_handler('Изменения', 'изменение расписания')
def changes_lesson(**kwargs):
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    chat_bd = bot[0]['chat_id']
    isMember(kwargs["user_id"], chat_bd)
    vk.messages.send(**chat_id, message="Это может занять какое-то время..", random_id=0)
    group = Group.objects.filter(chat_id=chat_bd).first().group
    parsed.send_pars(group=group, chat_id=chat_id)