import os
import re
from urllib.parse import urlencode

import requests
import shutil
import zipfile


def parser(group):
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = 'https://yadi.sk/d/flWvOqsC3Woqfe'
    standart_path = '/root/vk_callback/changes/'
    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']
    download_response = requests.get(download_url)

    with open(standart_path + 'downloaded_file.zip', 'wb') as f:
        f.write(download_response.content)
        shutil.rmtree(standart_path + 'path_of_rename', ignore_errors=True)
        with zipfile.ZipFile(standart_path + 'downloaded_file.zip', 'r') as zipizm:
            zipizm.extractall(standart_path)
        os.rename(standart_path + 'Изменения в расписании на день', standart_path + 'path_of_rename')
        if len(os.listdir(standart_path + 'path_of_rename')) > 1:
            os.rename(standart_path + 'path_of_rename/' + os.listdir(standart_path + 'path_of_rename')[1],
                      standart_path + 'path_of_rename/raspisanie.docx')
        else:
            os.rename(standart_path + 'path_of_rename/' + os.listdir(standart_path + 'path_of_rename')[0],
                      standart_path + 'path_of_rename/raspisanie.docx')
        os.system(
            f'sudo lowriter --convert-to doc {standart_path}path_of_rename/raspisanie.docx --outdir {standart_path}path_of_rename/')
        os.system(
            f'sudo antiword {standart_path}path_of_rename/raspisanie.doc > {standart_path}path_of_rename/raspisanie.txt')
        group = group.lower()
        ds = []
        group = group.split(' ')[0]
        with open(standart_path + 'path_of_rename/raspisanie.txt', 'r') as f:
            f.readline()
            f.readline()
            date = f.readline()
            for i in f.readlines():
                if re.search(group.split(',')[0], i.lower()) is not None:
                    groups2 = group
                else:
                    groups2 = group.replace("-", " ")
                if re.search(groups2, i.lower()) is not None:
                    splited = i.split('|')
                    pars = splited[2].split(',')
                    if len(pars) == 0:
                        pars = splited[2]
                    for i in pars:
                        if re.search('Нет', splited[3]):
                            ds.append({i.rsplit()[0]: ['Нет', 'Нет']})
                        else:
                            if len(i.rsplit()) == 0:
                                ds.append({"": [splited[3], splited[5]]})
                            else:
                                ds.append({i.rsplit()[0]: [splited[3], splited[5]]})
    return ds, date


def parser_main(text, data):
    z = 0
    for k in data[0]:
        if list(k.values())[0][0] == 'Нет':
            if len(list(k.keys())[0].split(" ")) > 1:
                if list(k.keys())[0].split(" ")[0] == '':
                    lesson = list(k.keys())[0].split(" ")[1]
                else:
                    lesson = list(k.keys())[0].split(" ")[0]
            else:
                lesson = list(k.keys())[0].split(" ")[0]
            text += f'\n{lesson} пр. - Пары нет. ❌'
        else:
            text += f'\n{list(k.keys())[0].split(" ")[0]} пр. - Пара: {list(k.values())[0][0]} - Аудитория: {list(k.values())[0][1]}'
        z += 1
    text += '\n\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼'
    return text
