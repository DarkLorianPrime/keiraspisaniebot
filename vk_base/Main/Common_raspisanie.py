import json

from vk_base.Config import vk, weeks
from vk_base.Models.models import Group
from vk_base.Parser import parsed
from vk_base.Utils.decorators import json_command_handler, command_handler
from vk_base.Utils.functional import isMember, return_error
from vk_base.Utils.raspisanie import get_info, week_company, get_week
from vk_base.Utils.validators import is_bot
from vk_base.commands.text import json_keyboard, get_text_text


@json_command_handler('Сегодня', 'today')
def today(**kwargs) -> None:
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    info = get_info(bot[0]['chat_id'], notsunday=True)
    timetable = info['timetable']['weeks'][info["to_days"]["week_num"]]['days'][info["to_days"]["day_int"]]
    vk.messages.send(**bot[0]['chat_dict'], message=week_company(**info["to_days"], timetable=timetable), random_id=0)


@json_command_handler('время', 'Звонки', 'конец пары')
def get_time(**kwargs) -> None:
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    vk.messages.send(**bot[0]['chat_dict'], message=get_text_text('time'), random_id=0)


def send_tommorow(kwargs: dict, number_company: int) -> None:
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    chat_bd = bot[0]['chat_id']
    isMember(kwargs["user_id"], chat_bd)
    info = get_info(chat_bd)
    info["to_days"]["day_int"] += 1
    if info["to_days"]["day_int"] == 6:
        return_error(error="Завтра воскресение 🤔", chat_id=chat_bd)
    group = Group.where(chat_id=str(chat_bd)).first().group
    timetable = info['timetable']['weeks'][info["to_days"]["week_num"]]['days'][info["to_days"]["day_int"]]
    updates = []

    if number_company == 0:
        parsed_info = parsed.send_pars(group=group, chat_id=chat_bd, dont_send=True)
        updates = [list(i.items()) for i in parsed_info[0]]

    clear_company = week_company(**info["to_days"], timetable=timetable, updates=updates)
    vk.messages.send(**chat_id, message=clear_company, random_id=0)


@json_command_handler('Завтра', 'tommorow')
def tomorrow(**kwargs) -> None:
    send_tommorow(kwargs, 1)


@command_handler("завтра изменения")
def tommorow_with_updates(**kwargs) -> None:
    send_tommorow(kwargs, 0)


@json_command_handler('Следующая', 'Следующая неделя')
def next_week(**kwargs) -> None:
    isMember(kwargs["user_id"], kwargs["chat_id"])
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    chat_bd = bot[0]['chat_id']
    vk.messages.send(**chat_id, message=get_week(chat_id=chat_bd), random_id=0)


@json_command_handler('Эта', 'Эта неделя')
def this_week(**kwargs) -> None:
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    vk.messages.send(**bot[0]["chat_dict"], message=get_week(that_week=True, chat_id=bot[0]["chat_id"]), random_id=0)


@command_handler('расписание', )
def button_get_lessons(**kwargs) -> None:
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    payload = json.dumps(json_keyboard())
    vk.messages.send(**bot[0]['chat_dict'], message='Расписание:', keyboard=payload, random_id=0)


@command_handler("понедельник", "вторник", "среда", "четверг", "пятница", "суббота")
def one_of_the_day(**kwargs) -> None:
    isMember(kwargs["user_id"], kwargs["chat_id"])
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_id = bot[0]['chat_dict']
    info = get_info(bot[0]['chat_id'])
    days = weeks.index(kwargs["text"].capitalize())
    timetable = info['timetable']['weeks'][info["to_days"]["week_num"]]['days'][days]
    info["to_days"].pop("day_int")
    vk.messages.send(**chat_id, random_id=0, message=week_company(**info["to_days"], timetable=timetable, day_int=days))


@json_command_handler('Изменения', 'изменение расписания')
def changes_lesson(**kwargs) -> None:
    bot = is_bot(kwargs["chat_id"], kwargs["user_id"])
    chat_bd = bot[0]['chat_id']
    isMember(kwargs["user_id"], chat_bd)
    group = Group.where(chat_id=str(chat_bd)).first().group
    parsed.send_pars(group=group, chat_id=chat_bd)
