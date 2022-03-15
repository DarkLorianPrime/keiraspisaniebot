import time
from datetime import datetime, timedelta

import psycopg2

import vk_methods_handler
from parsed_auto import send_pars

vk = vk_methods_handler.message_handler().connect_to_methods()
connection = psycopg2.connect(user='darklorian', database='postgres', password='root', host='darklorian.space')
cursor = connection.cursor()
while True:
    cursor.execute('SELECT * from vkhandler_settings where autosend=True')
    settings = cursor.fetchall()
    time_now = (datetime.now() + timedelta(hours=4, minutes=0)).time()
    for i in settings:
        if time_now.replace(microsecond=0) == datetime.strptime(i[-2], '%H:%M').time():
            cursor.execute('SELECT * from vkhandler_group where chat_id=%s', (i[1],))
            group = cursor.fetchone()
            if group is None:
                continue
            send_pars(group[1], i[1])
    time.sleep(1)
