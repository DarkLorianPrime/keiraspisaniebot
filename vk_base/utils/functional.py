from commands.text import get_text
from config import vk
from utils.scheduleExceptions import SendedMessage


def return_error(error, send_id):
    vk.messages.send(**send_id, message=error, random_id=0, disable_mentions=1)
    raise SendedMessage('send message')


def isMember(user_id, send_id: dict):
    json_member = vk.groups.isMember(group_id='145807659', user_id=user_id)
    if json_member.get('response') == 1:
        return True
    return_error(send_id=send_id, error=get_text("not_member"))
