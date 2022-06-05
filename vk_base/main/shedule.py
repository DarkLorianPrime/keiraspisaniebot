import datetime
import json

from config import vk, weeks
from models.models import Group
from parser import parsed
from utils.decorators import json_command_handler, command_handler
from utils.functional import isMember, return_error
from utils.schedulehelper import get_info, week_company, get_week
from commands.text import json_keyboard, get_text
from vk_methods_handler import EventInformation


@json_command_handler('Сегодня', 'today')
def today(vk_object: EventInformation) -> None:
    info = get_info(send_id=vk_object.send_id, chat_id=vk_object.chat_id, notsunday=True)
    timetable = info['timetable']['weeks'][info["to_days"]["week_num"]]['days'][info["to_days"]["day_int"]]
    vk.messages.send(**vk_object.send_id, message=week_company(**info["to_days"], timetable=timetable), random_id=0)


def send_tommorow_or_updated(vk_object: EventInformation, number_company: int) -> None:
    parsed_info = []
    isMember(vk_object.from_id, vk_object.send_id)
    info = get_info(send_id=vk_object.send_id, chat_id=vk_object.chat_id)
    if info["to_days"]["day_int"] == 6:
        return_error(error="Завтра воскресение 🤔", send_id=vk_object.send_id)

    group = Group.where(chat_id=str(vk_object.chat_id)).first().group
    timetable = info['timetable']['weeks'][info["to_days"]["week_num"]]['days'][info["to_days"]["day_int"]]
    updates = []
    if number_company in [0, 1]:
        info["to_days"]["day_int"] += 1

    if number_company != 1:
        parsed_info = parsed.send_pars(group=group, chat_id=vk_object.chat_id, dont_send=True)
        updates = [list(i.items()) for i in parsed_info[0]]

    if number_company == 0:
        if str(datetime.datetime.now().day) in parsed_info[1]:
            return_error(error=get_text("not_updated"), send_id=vk_object.send_id)

    if number_company == 2:
        if str(datetime.datetime.now().day) not in parsed_info[1]:
            return_error(error=get_text("already_updated"), send_id=vk_object.send_id)

    clear_company = week_company(**info["to_days"], timetable=timetable, updates=updates)
    vk.messages.send(**vk_object.send_id, message=clear_company, random_id=0)


@json_command_handler('Завтра', 'tommorow')
def tomorrow(vk_object: EventInformation) -> None:
    send_tommorow_or_updated(vk_object, 1)


@json_command_handler("СИ", "сегодня изменения")
def tommorow_with_updates(vk_object: EventInformation) -> None:
    send_tommorow_or_updated(vk_object, 2)


@json_command_handler("ЗИ", "завтра изменения")
def tommorow_with_updates(vk_object: EventInformation) -> None:
    send_tommorow_or_updated(vk_object, 0)


@json_command_handler('Следующая', 'Следующая неделя')
def next_week(vk_object: EventInformation) -> None:
    isMember(vk_object.from_id, vk_object.send_id)
    vk.messages.send(**vk_object.send_id, message=get_week(send_id=vk_object.send_id, chat_id=vk_object.chat_id),
                     random_id=0)


@json_command_handler('Эта', 'Эта неделя')
def this_week(vk_object: EventInformation) -> None:
    vk.messages.send(**vk_object.send_id, random_id=0,
                     message=get_week(that_week=True, send_id=vk_object.send_id, chat_id=vk_object.chat_id))


@command_handler('расписание')
def button_get_lessons(vk_object: EventInformation) -> None:
    payload = json.dumps(json_keyboard())
    vk.messages.send(**vk_object.send_id, message='Расписание:', keyboard=payload, random_id=0)


@command_handler("понедельник", "вторник", "среда", "четверг", "пятница", "суббота")
def one_of_the_day(vk_object: EventInformation) -> None:
    isMember(vk_object.from_id, vk_object.send_id)
    info = get_info(send_id=vk_object.send_id, chat_id=vk_object.chat_id)
    days = weeks.index(vk_object.text.capitalize())
    timetable = info['timetable']['weeks'][info["to_days"]["week_num"]]['days'][days]
    info["to_days"].pop("day_int")
    vk.messages.send(**vk_object.send_id, random_id=0,
                     message=week_company(**info["to_days"], timetable=timetable, day_int=days))


@json_command_handler('Изменения', 'изменение расписания')
def changes_lesson(vk_object: EventInformation) -> None:
    isMember(vk_object.from_id, vk_object.send_id)
    group = Group.where(chat_id=str(vk_object.chat_id)).first().group
    parsed.send_pars(group=group, chat_id=vk_object.chat_id)


@json_command_handler('время', 'Звонки', 'конец пары')
def get_time(vk_object: EventInformation) -> None:
    vk.messages.send(**vk_object.send_id, message=get_text('time'), random_id=0)
