from typing import Optional

from vk_base.Config import vk
from vk_base.parser import parser_method
from vk_base.utils.validators import is_bot


def send_pars(group: str, chat_id: int, dont_send: bool = False) -> Optional[dict]:
    bot = is_bot(int(chat_id))
    vk.messages.send(**bot[0]["chat_dict"], message="Это может занять какое-то время..", random_id=0)
    data = parser_method.parser(group)
    
    if dont_send:
        return data

    if not data[0]:
        text = f'{data[1]}❌ Изменений на завтра нет. ❌'
        text += '\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼'
        vk.messages.send(**bot[0]["chat_dict"], message=text, random_id=0)
        return

    text = parser_method.parser_main(data)
    vk.messages.send(**bot[0]["chat_dict"], message=text, random_id=0)
    return
