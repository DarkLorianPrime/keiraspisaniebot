import vk_methods_handler
import parser_method

vk = vk_methods_handler.message_handler().connect_to_methods()


def send_pars(group, chat_id):
    data = parser_method.parser(group)
    text = data[1]
    if not data[0]:
        text = '❌ Изменений на завтра нет. ❌'
        text += '\n‼ Изменения находятся в тестировании и могут содержать ошибки. Перепроверяйте их на сайте:\nhttps://disk.yandex.ru/d/flWvOqsC3Woqfe ‼'
        if int(chat_id) <= 20000000:
            vk.messages.send(chat_id=chat_id, message=text, random_id=0)
            return
        vk.messages.send(user_id=chat_id, message=text, random_id=0)
        return
    text = parser_method.parser_main(text, data)
    if int(chat_id) <= 20000000:
        vk.messages.send(chat_id=chat_id, message=text, random_id=0)
        return
    vk.messages.send(user_id=chat_id, message=text, random_id=0)
    return
