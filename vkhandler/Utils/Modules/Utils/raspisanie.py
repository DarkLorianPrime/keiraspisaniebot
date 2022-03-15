from datetime import datetime, timedelta, date

import requests

from vkhandler.Utils.Modules.Config import weeks, time_list
from vkhandler.Utils.Modules.Utils.functional import return_error
from vkhandler.Utils.commands.errors import get_error_text
from vkhandler.models import Group, Settings


def week_company(week_num, timetable, setup, day_int=0, group=0, week=False):
    lesson = 0
    text = f'✅Расписание на {weeks[day_int]}✅\n\n' if week else f"Расписание группы {group}\nСейчас {1 if week_num == 0 else 2} неделя.\n Расписание на {weeks[day_int]}\n Пары:\n"
    for lessons in timetable['lessons']:
        if not lessons:
            lesson += 1
            continue
        text += f'{lesson + 1} пр. - ' + lessons[0]['nameOfLesson']
        if len(lessons) > 1:
            if setup.add_class:
                text += f"\nАудитория: {lessons[0]['room']} / {lessons[1]['room']}"
            if setup.add_teacher:
                text += f"\nУчитель: {lessons[0]['teacher']} / {lessons[1]['teacher']}"
        else:
            if setup.add_class:
                text += f"\nАудитория: {lessons[0]['room']}"
            if setup.add_teacher:
                text += f"\nУчитель: {lessons[0]['teacher']}"
        if setup.add_time:
            text += f"\nОна начнется в {time_list[lesson][lesson][0]}"
            text += f"\nОна будет идти до {time_list[lesson][lesson][1]}"
        text += '\n\n'
        lesson += 1
    return text


def get_info(chat_id, notsunday=False):
    info = dict()

    info['time_now'] = (datetime.now() + timedelta(hours=4, minutes=0)).time()
    group = Group.objects.filter(chat_id=chat_id)
    if not group.exists():
        return_error(error=get_error_text('not_group'), chat_id=chat_id)
    group = group.first().group
    response = requests.get(f'https://time.ulstu.ru/api/1.0/timetable?filter={group}')
    if response.status_code == 400 or response.status_code == 404:
        response = requests.get(f'https://timetable.athene.tech/api/1.0/timetable?filter={group}')
    info['timetable'] = response.json()['response']
    week_int = 1 if datetime.now().isocalendar()[1] % 2 == 0 else 0
    week_int = 1 - week_int if date.today().weekday() == 6 else week_int

    info["to_days"] = {"week_num": week_int, "setup": Settings.objects.filter(chat_id=chat_id).first(),
                       "day_int": date.today().weekday() if date.today().weekday() != 6 else -1, "group": group}
    if notsunday:
        if info["to_days"]["day_int"] == 6 or info["to_days"]["day_int"] == -1:
            return_error("Так воскресение же 🤔\nА воскресение не считается 😉", chat_id)
    return info

def get_week(that_week=False, chat_id=0):
    info = get_info(chat_id)
    week_number = info["to_days"]["week_num"]
    week = 'эту' if that_week else 'следующую'
    if not that_week:
        week_number = 1 - week_number
    text = f"Группа {info['to_days']['group']}\nРасписание на {week} ({week_number + 1}) неделю:\n"
    day = 0
    del info["to_days"]["day_int"]
    timetable = info['timetable']['weeks'][week_number]
    for days in timetable['days']:
        text += week_company(**info["to_days"], timetable=days, day_int=day, week=True) + '\n=========\n\n'
        day += 1
    return text