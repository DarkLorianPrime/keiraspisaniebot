import os
import re
from typing import Union, Any
from urllib.parse import urlencode

import requests
import shutil
import zipfile

from config import vk

standard_path = 'changes/'
standard_path_renamed = standard_path + "changes/"


def zip_to_txt():
    os.system(f'sudo lowriter --convert-to doc {standard_path_renamed}schedule.docx --outdir {standard_path_renamed}')
    os.system(f'sudo antiword {standard_path_renamed}schedule.doc > {standard_path_renamed}schedule.txt')


def get_from_yadisk():
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = 'https://yadi.sk/d/flWvOqsC3Woqfe'

    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']
    return requests.get(download_url)


def parser(group: str) -> Union[tuple[bool, str], tuple[str, list[dict[Any, Any]], str]]:
    updated = []
    returned_string = ""
    download_response = get_from_yadisk()
    with open(standard_path + 'downloaded_file.zip', 'wb') as f:
        f.write(download_response.content)
        shutil.rmtree(standard_path_renamed, ignore_errors=True)

        with zipfile.ZipFile(standard_path + 'downloaded_file.zip', 'r') as docfile:
            docfile.extractall(standard_path)

        os.rename(standard_path + 'Изменения в расписании на день', standard_path_renamed)
        listdir_standard = os.listdir(standard_path_renamed)
        file = listdir_standard[1] if len(os.listdir(standard_path_renamed)) > 1 else listdir_standard[0]
        os.rename(f'{standard_path_renamed}{file}', f'{standard_path_renamed}schedule.docx')
        zip_to_txt()
        group = group.lower().split(' ')[0]
        continued = False
        with open(f'{standard_path_renamed}schedule.txt', 'r') as schedule:

            date = schedule.readline()
            while "изменения" not in date.lower():
                date = schedule.readline()

            for line in schedule.readlines():
                groups2 = group if re.search(group.split(',')[0], line.lower()) is not None else group.replace("-", " ")
                splited = line.split('|')
                if re.search(groups2, line.lower()) is not None:

                    if len(splited) < 4:
                        returned_string += " ".join(splited)
                        continue

                    if re.search('Нет', splited[3]):
                        returned_string += f"{splited[2].rsplit()[0]} пр. - Пары нет. - Преподаватель: ❌\n"
                        updated.append({splited[2]: ['Нет', 'Нет']})
                        continue
                    continued = True
                    returned_string += f"{splited[2].rsplit()[0]} пр. - Пара: {splited[3]}" + "{0}" + f"- Аудитория: {splited[5]} - Преподаватель: {splited[4]}\n"
                    updated.append({splited[2].rsplit()[0]: [splited[3], splited[5], splited[4]]})
                    continue
                if continued:
                    continued = False
                    split_data = splited[1].rsplit()
                    if not split_data:
                        returned_string = returned_string.format("")
                        continue
                    if split_data[0].lower() in ["1п/г", "2п/г", "1п\\г", "2п\\г"]:
                        returned_string = returned_string.format(f"{splited[3]} {splited[1]}")
                        continue
                    returned_string = returned_string.format("")
        if returned_string == "":
            return False, date

        returned_string += "\n\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼"
        return f"{date}\n{returned_string}", updated, date


def send_changes(group: str, chat_id: int, dont_send: bool = False):
    send_id = {"user_id": chat_id} if chat_id > 2000 else {"chat_id": chat_id}
    vk.messages.send(**send_id, message="Это может занять какое-то время..", random_id=0)
    data = parser(group)

    if not data[0]:
        text = f'{data[1]}❌ Изменений на завтра нет. ❌'
        text += '\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼'
        vk.messages.send(**send_id, message=text, random_id=0)
        return

    if dont_send:
        return data[1], data[2]

    if not data[0]:
        data[0] = f'{data[2]}\n❌ Изменений на завтра нет. ❌\n'
        data[0] += '\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼'

    vk.messages.send(**send_id, message=data[0], random_id=0)
    return
