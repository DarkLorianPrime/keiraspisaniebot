import os

import requests

from vk_base.Config import vk
from vk_base.Utils.validators import is_bot


class SendedMessage(Exception):
    def __init__(self, message):
        super().__init__(message)


def return_error(error, chat_id):
    bot = is_bot(chat_id)
    vk.messages.send(**bot[0]['chat_dict'], message=error, random_id=0, disable_mentions=1)
    raise SendedMessage('send message')


def get_message(*args):
    conversation_id = vk.messages.getByConversationMessageId(peer_id=args[1], conversation_message_ids=args[0])
    attachment_list = []
    for i in conversation_id['response']['items'][0]['attachments']:
        server = vk.photos.getMessagesUploadServer(group_id=145807659)
        with open(f'{os.getcwd()}/photos/file_{args[1]}.png', 'wb') as file:
            file.write(requests.get(i['photo']['sizes'][-1]['url']).content)
        with open(f'{os.getcwd()}/photos/file_{args[1]}.png', 'rb') as file:
            dr = requests.post(server['response']['upload_url'], files={'file1': file}).json()
        files = vk.photos.saveMessagesPhoto(**dr)
        attachment = f'photo{files["response"][0]["owner_id"]}_{files["response"][0]["id"]}'
        attachment_list.append(attachment)
        ids = NotifyUrls.objects.create(chat_id=args[1] - 2000000000, url=attachment)
        args[2][0].urls.add(ids)
    return attachment_list


def in_group_chat_error(bot, chat_id):
    if not bot:
        return_error('Данная функция работает только в беседах ❌.', chat_id=chat_id)


def isMember(user_id, chat_id):
    json_member = vk.groups.isMember(group_id='145807659', user_id=user_id)
    if json_member.get('response') == 1:
        return True
    return_error(chat_id=chat_id,
                 error='Вы не подписаны на группу. ❌ @keiraspisanie\nДля получения полного доступа нужно подписаться на группу.')