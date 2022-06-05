from config import vk
from parser import parser_method
from utils.validators import is_bot


def send_pars(group: str, chat_id: int, dont_send: bool = False):
    bot = is_bot(int(chat_id))
    vk.messages.send(**bot[0]["chat_dict"], message="Это может занять какое-то время..", random_id=0)
    data = parser_method.parser(group)

    if not data[0]:
        text = f'{data[1]}❌ Изменений на завтра нет. ❌'
        text += '\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼'
        vk.messages.send(**bot[0]["chat_dict"], message=text, random_id=0)
        return

    if dont_send:
        return data[1], data[2]

    if not data[0]:
        data[0] = f'{data[2]}\n❌ Изменений на завтра нет. ❌\n'
        data[0] += '\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼'

    vk.messages.send(**bot[0]["chat_dict"], message=data[0], random_id=0)
    return
