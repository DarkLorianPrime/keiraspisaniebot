from vkhandler.Utils.Modules.Config import vk


def is_bot(chat_id=0, user_id=0):
    dict_id = {}
    if user_id > 0 or chat_id > 200000:
        chats = False
        dict_id['chat_id'] = user_id if chat_id < 200000 else chat_id
        dict_id['chat_dict'] = {'user_id': user_id} if chat_id < 200000 else {'user_id': chat_id}
    if 0 < chat_id < 200000:
        chats = True
        dict_id['chat_id'] = chat_id
        dict_id['chat_dict'] = {'chat_id': chat_id}
    return dict_id, chats


def check_admin(peer_id, user_id):
    users = vk.messages.getConversationMembers(peer_id=peer_id)
    for user in users.get('response')['items']:
        if user_id == user['member_id']:
            if user.get('is_admin') is not None or user.get('is_admin'):
                return True
    return False
