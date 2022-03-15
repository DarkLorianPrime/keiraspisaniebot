from vkhandler.Utils.Modules.Config import vk
from vkhandler.Utils.Modules.Utils.decorators import search_command_handler, command_handler
from vkhandler.Utils.Modules.Utils.functional import in_group_chat_error, return_error
from vkhandler.models import PushGroup


@search_command_handler(['!новаягруппа', ' '], ['!добавитьгруппу', ' '])
def add_push_group(**kwargs):
    in_group_chat_error(kwargs["bot"], kwargs["user_id"])
    text = kwargs["text"].lower().split(' ')
    if len(text) <= 2:
        return_error('Вы должны указать хотя бы 1 ID ❌.', chat_id=kwargs["chat_id"])
    ids = []
    for i in range(2, len(text)):
        user_id = text[i].split('|')
        if len(user_id) < 2:
            return_error(f'Все пользователи должны быть указаны @ ❌.\nНапример: {"@" + text[i]}',
                         chat_id=kwargs["chat_id"])
        user_id = user_id[1].replace(']', '')
        ids.append(user_id)
    if PushGroup.objects.filter(name=text[1], chat_id=kwargs["chat_id"]).exists():
        return_error(f'Такая группа уже существует ❌.', chat_id=kwargs["chat_id"])
    PushGroup.objects.create(name=text[1], chat_id=kwargs["chat_id"], users=ids)
    vk.messages.send(chat_id=kwargs["chat_id"], message=f'Группа {text[1]} успешно создана.', random_id=0)


@search_command_handler(['!удалитьгруппу', ' '], ['!удалигруппу', ' '], ['!забудьгруппу', ' '])
def del_push_groups(**kwargs):
    in_group_chat_error(kwargs["bot"], kwargs["user_id"])
    text = kwargs["text"].lower().split(' ')
    PushGroup.objects.filter(chat_id=kwargs["chat_id"], name=text[1]).delete()
    vk.messages.send(chat_id=kwargs["chat_id"], message='Группа успешно удалена', random_id=0)


@command_handler('!группы')
def get_push_groups(**kwargs):
    in_group_chat_error(kwargs["bot"], kwargs["user_id"])
    push = PushGroup.objects.filter(chat_id=kwargs["chat_id"])
    if not push.exists():
        return_error(f'Группы в беседе не найдены ❌.', chat_id=kwargs["chat_id"])
    text = ''
    for i in push.all():
        text += f'Группа: {i.name},\n Пользователей в ней: {len(i.users)}\n'
    vk.messages.send(chat_id=kwargs["chat_id"], message=text, random_id=0)


@search_command_handler(['!уведомление', ' '])
def push_group(**kwargs):
    in_group_chat_error(kwargs["bot"], kwargs["user_id"])
    name = kwargs["text"].lower().split(' ')
    if len(name) < 2:
        return_error('Укажите название группы ❌.', kwargs["chat_id"])
    users = PushGroup.objects.filter(chat_id=kwargs["chat_id"], name=name[1])
    if not users.exists():
        return_error(f'Группы в беседе не найдены ❌.', chat_id=kwargs["chat_id"])
    users = users.first().users
    text = ''
    for user in users:
        text += f'{user} (🌠)'
    vk.messages.send(chat_id=kwargs["chat_id"], message=text, random_id=0)
