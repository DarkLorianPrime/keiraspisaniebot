from commands.text import get_text
from config import vk
from utils.scheduleExceptions import SendedMessage


def send_text(error, send_id):
    vk.messages.send(**send_id, message=error, random_id=0, disable_mentions=1)
    raise SendedMessage('send message')


def is_member(user_id: int, send_id: dict) -> bool:
    json_member = vk.groups.isMember(group_id='145807659', user_id=user_id)
    if json_member.get('response') == 1:
        return True
    send_text(send_id=send_id, error=get_text("not_member"))


def is_admin(peer_id: int, user_id: int) -> bool:
    users = vk.messages.getConversationMembers(peer_id=peer_id)
    for user in users.get('response')['items']:
        if user_id == user['member_id']:
            if user.get('is_admin') is not None or user.get('is_admin'):
                return True
    return False
