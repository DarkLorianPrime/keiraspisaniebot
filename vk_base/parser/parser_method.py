import os
import re
from urllib.parse import urlencode

import requests
import shutil
import zipfile

standart_path = 'changes/'
standart_path_renamed = standart_path + "changes/"


def zip_to_txt():
    os.system(f'sudo lowriter --convert-to doc {standart_path_renamed}raspisanie.docx --outdir {standart_path_renamed}')
    os.system(f'sudo antiword {standart_path_renamed}raspisanie.doc > {standart_path_renamed}raspisanie.txt')


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

    with open(standart_path + 'downloaded_file.zip', 'wb') as f:
        f.write(download_response.content)
        shutil.rmtree(standart_path_renamed, ignore_errors=True)

        with zipfile.ZipFile(standart_path + 'downloaded_file.zip', 'r') as docfile:
            docfile.extractall(standart_path)

        os.rename(standart_path + 'Изменения в расписании на день', standart_path_renamed)
        listdir_standart = os.listdir(standart_path_renamed)
        file = listdir_standart[1] if len(os.listdir(standart_path_renamed)) > 1 else listdir_standart[0]
        os.rename(f'{standart_path_renamed}{file}', f'{standart_path_renamed}raspisanie.docx')
        zip_to_txt()
        group = group.lower().split(' ')[0]

        with open(f'{standart_path_renamed}raspisanie.txt', 'r') as f:

            date = f.readline()
            while "изменения" not in date.lower():
                date = f.readline()

            for i in f.readlines():
                groups2 = group if re.search(group.split(',')[0], i.lower()) is not None else group.replace("-", " ")

                if re.search(groups2, i.lower()) is not None:
                    splited = i.split('|')

                    if len(splited) < 4:
                        returned_string += " ".join(splited)
                        continue

                    if re.search('Нет', splited[3]):
                        returned_string += f"{splited[2].rsplit()[0]} пр. - Пары нет. - Препод: ❌\n"
                        updated.append({splited[2]: ['Нет', 'Нет']})
                        continue

                    returned_string += f"{splited[2].rsplit()[0]} пр. - Пара: {splited[3]} - Аудитория: {splited[5]} - Препод: {splited[4]}\n"
                    updated.append({splited[2].rsplit()[0]: [splited[3], splited[5], splited[4]]})

        if returned_string == "":
            return False, date

        returned_string += "\n\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼"
        return f"{date}\n{returned_string}", updated, date
