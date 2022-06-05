from datetime import datetime, date

import requests
from bs4 import BeautifulSoup

from config import weeks, time_list
from models.localorm import query_exists
from utils.functional import return_error
from commands.text import get_text
from models.models import Group, Settings


def week_company(week_num, timetable, setup, day_int=0, group=0, week=False, updates=None):
    updates = [] if updates is None else updates
    lesson = 0
    need_updates = True if updates else False
    text = f'✅Расписание на {weeks[day_int]}✅\n\n' if week else f"Расписание группы {group}\nСейчас {1 if week_num == 0 else 2} неделя.\n Расписание на {weeks[day_int]}{' | С изменениями' if need_updates else ''}\n Пары:\n"
    for lessons in timetable["lessons"]:
        exist_update = []
        room = ""
        teacher = ""
        lesson_name = ""

        if not lessons:
            lesson += 1
            continue

        if need_updates:
            exist_update = [k for k, i in enumerate(updates) if str(lesson + 1) in i[0]]

        if not exist_update:
            split_word = "✅" if not week else ""
            text += f'{split_word}{lesson + 1} пр. - {lessons[0]["nameOfLesson"]}{split_word}'

        else:
            lesson_name = updates[exist_update[0]][0][1][0].rstrip().lstrip()
            room = updates[exist_update[0]][0][1][1].rstrip().lstrip()
            teacher = updates[exist_update[0]][0][1][2].rstrip().lstrip()
            split_word = "✅" if lesson_name != "Нет" else "✖"
            text += f'{split_word}{lesson + 1} пр. - {lessons[0]["nameOfLesson"]} || {lesson_name}{split_word}'

        if len(lessons) > 1:
            if setup.add_class:
                text += f"\nАудитория: {lessons[0]['room']} / {lessons[1]['room']}"

            if setup.add_teacher:
                text += f"\nУчитель: {lessons[0]['teacher']} / {lessons[1]['teacher']}"

            if exist_update:
                if lesson_name != "Нет":
                    if setup.add_class:
                        text += f"\n\nАудитория: {room}"

                    if setup.add_teacher:
                        text += f"\nУчитель: {teacher}"
        else:
            if lessons[0]["teacher"].split(" ")[0] != teacher.split(" ")[0]:
                if setup.add_class:
                    text += f"\nАудитория: {lessons[0]['room']}"

                if setup.add_teacher:
                    text += f"\nУчитель: {lessons[0]['teacher']}"

            if exist_update:
                if lesson_name != "Нет":
                    if setup.add_class:
                        text += f"\n\nАудитория: {room}"

                    if setup.add_teacher:
                        text += f"\nУчитель: {teacher}"

        if setup.add_time:
            text += f"\n\nОна начнется в {time_list[lesson][lesson][0]}"
            text += f"\nОна будет идти до {time_list[lesson][lesson][1]}"

        text += '\n\n'
        lesson += 1

    if need_updates:
        text += '\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼'
        text += "\nКоманда может работать нестабильно. Пожалуйста, перепроверьте командой \"изменения\""

    return text


def get_info(send_id, chat_id, notsunday=False):
    info = dict()

    info['time_now'] = datetime.now().time()
    if not query_exists(Group.chat_id, str(chat_id)):
        return_error(error=get_text('not_group'), send_id=send_id)

    group = Group.where(chat_id=str(chat_id)).first().group
    response = requests.get(f'https://time.ulstu.ru/api/1.0/timetable?filter={group}')

    if response.status_code in [400, 404]:
        response = requests.get(f'https://timetable.athene.tech/api/1.0/timetable?filter={group}')

    info['timetable'] = response.json()['response']
    week_int = 0 if datetime.now().isocalendar()[1] % 2 == 0 else 1

    info["to_days"] = {"week_num": week_int, "setup": Settings.where(chat_id=str(chat_id)).first(),
                       "day_int": date.today().weekday() if date.today().weekday() != 6 else -1, "group": group}
    if notsunday:
        if info["to_days"]["day_int"] == 6 or info["to_days"]["day_int"] == -1:
            return_error("Так воскресение же 🤔\nА воскресение не считается 😉", chat_id)
    return info


def get_week(that_week=False, send_id=0, chat_id=0):
    info = get_info(send_id, chat_id)
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

    groups.pop(0)
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


def insert_into_peer(group, chat_id):
    if not query_exists(Settings.chat_id, str(chat_id)):
        Settings.create(chat_id=str(chat_id))

    if not query_exists(Group.chat_id, str(chat_id)):
        Group.create(**{"group": group, "chat_id": str(chat_id)})
        return

    Group.where(chat_id=str(chat_id)).first().update(**{'group': group, 'chat_id': str(chat_id)})
