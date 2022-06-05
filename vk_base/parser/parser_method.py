import os
import re
from urllib.parse import urlencode

import requests
import shutil
import zipfile

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


def parser(group):
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

        with open(f'{standard_path_renamed}schedule.txt', 'r') as schedule:

            date = schedule.readline()
            while "изменения" not in date.lower():
                date = schedule.readline()

            for line in schedule.readlines():
                groups2 = group if re.search(group.split(',')[0], line.lower()) is not None else group.replace("-", " ")

                if re.search(groups2, line.lower()) is not None:
                    splited = line.split('|')

                    if len(splited) < 4:
                        returned_string += " ".join(splited)
                        continue

                    if re.search('Нет', splited[3]):
                        returned_string += f"{splited[2].rsplit()[0]} пр. - Пары нет. - Преподаватель: ❌\n"
                        updated.append({splited[2]: ['Нет', 'Нет']})
                        continue

                    returned_string += f"{splited[2].rsplit()[0]} пр. - Пара: {splited[3]} - Аудитория: {splited[5]} - Преподаватель: {splited[4]}\n"
                    updated.append({splited[2].rsplit()[0]: [splited[3], splited[5], splited[4]]})

        if returned_string == "":
            return False, date

        returned_string += "\n\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼"
        return f"{date}\n{returned_string}", updated, date
