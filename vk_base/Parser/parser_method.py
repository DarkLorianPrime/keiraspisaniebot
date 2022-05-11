import os
import re
from urllib.parse import urlencode

import requests
import shutil
import zipfile

standart_path = '/root/vk_base/changes/'
standart_path_renamed = standart_path + "path_of_rename/"


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
    download_response = get_from_yadisk()
    with open(standart_path + 'downloaded_file.zip', 'wb') as f:
        f.write(download_response.content)
        shutil.rmtree(standart_path_renamed, ignore_errors=True)
        with zipfile.ZipFile(standart_path + 'downloaded_file.zip', 'r') as docfile:
            docfile.extractall(standart_path)
        os.rename(standart_path + 'Изменения в расписании на день', standart_path_renamed)
        file = os.listdir(standart_path_renamed)[1] if len(os.listdir(standart_path_renamed)) > 1 else \
            os.listdir(standart_path_renamed)[0]
        os.rename(f'{standart_path_renamed}{file}', f'{standart_path_renamed}raspisanie.docx')
        zip_to_txt()
        updated = []
        group = group.lower()
        group = group.split(' ')[0]
        with open(f'{standart_path_renamed}raspisanie.txt', 'r') as f:
            while True:
                date = f.readline()
                if "Изменения" in date:
                    break

            for i in f.readlines():
                groups2 = group if re.search(group.split(',')[0], i.lower()) is not None else group.replace("-", " ")

                if re.search(groups2, i.lower()) is not None:
                    splited = i.split('|')
                    pars = splited[2] if len(splited[2].split(',')) == 0 else splited[2].split(',')

                    for i in pars:
                        if re.search('Нет', splited[3]):
                            updated.append({i.rsplit()[0]: ['Нет', 'Нет', splited[4]]})
                        else:
                            if len(i.rsplit()) == 0:
                                updated.append({"": [splited[3], splited[5], splited[4]]})
                            else:
                                updated.append({i.rsplit()[0]: [splited[3], splited[5], splited[4]]})
    return updated, date


def parser_main(data):
    text = f"{data[1]}"
    z = 0
    for k in data[0]:
        if list(k.values())[0][0] == 'Нет':
            if len(list(k.keys())[0].split(" ")) > 1:
                lesson = list(k.keys())[0].split(" ")[1] if list(k.keys())[0].split(" ")[0] == '' else \
                    list(k.keys())[0].split(" ")[0]
            else:
                lesson = list(k.keys())[0].split(" ")[0]

            text += f'\n{lesson} пр. - Пары нет. - Препод: {list(k.values())[0][2]} ❌'
        else:
            text += f'\n{list(k.keys())[0].split(" ")[0]} пр. - Пара: {list(k.values())[0][0]} - Аудитория: {list(k.values())[0][1].split(" ")[0]} - Препод: {list(k.values())[0][2]}'
        z += 1
    text += '\n\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼'
    return text
