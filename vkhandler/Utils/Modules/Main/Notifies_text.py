from vkhandler.Utils.Modules.Config import vk
from vkhandler.Utils.Modules.Utils.decorators import search_command_handler, command_handler
from vkhandler.Utils.Modules.Utils.functional import in_group_chat_error, return_error, get_message
from vkhandler.Utils.commands.errors import get_error_text
from vkhandler.models import Notify


@search_command_handler(['бот, запомни: ', ': '])
def create_notify(**kwargs):
    in_group_chat_error(kwargs["bot"], kwargs["user_id"])
    text_Body = ''
    if len(kwargs["splited"]) > 2:
        text_Body = kwargs["text"].lower().split(': ')[2]
    name = kwargs["text"].lower().split(': ')[1].split('\n')
    name = name[0] if len(name) > 1 else name[0].lstrip().rstrip()
    count = Notify.objects.filter(chat_id=kwargs["chat_id"])
    count = count.count() if count.exists() else 0
    if count + 1 == 25:
        return_error(get_error_text('limit'), chat_id=kwargs["chat_id"])
    notify = Notify.objects.update_or_create(chat_id=kwargs["chat_id"], count=int(count) + 1, name=name,
                                             text=text_Body)
    attach = get_message(kwargs["conversation_message_id"], kwargs["peer_id"], notify)
    add_to_photo = f'Добавлено {len(attach)} фотографий' if len(attach) > 0 else ''
    vk.messages.send(chat_id=kwargs["chat_id"], message=f'Запоминаю под названием "{name}" ✅\n {add_to_photo}',
                     random_id=0)


@search_command_handler(['бот, напомни', ': '], ['напомни', ': '])
def get_one_notify(**kwargs):
    in_group_chat_error(kwargs["bot"], kwargs["chat_id"])
    chat_id = kwargs["chat_id"]
    name = kwargs["splited"]
    if len(name) > 1:
        name = name[1]
    else:
        error = 'Команда не верна.❌\nбот, напомни: [название]\nВсе напоминания: Бот, напоминания'
        return_error(error=error, chat_id=chat_id)
    notifies = Notify.objects.filter(chat_id=chat_id, name=name).first()
    if notifies is None:
        return_error(error=f'Название "{name}" не найдено ❌', chat_id=chat_id)
    text = f'{notifies.name}\n{notifies.text}'
    vk.messages.send(chat_id=chat_id, message=text, random_id=0,
                     attachment=','.join(list(notifies.urls.values_list('url', flat=True))))


@command_handler('бот, напоминания', 'напоминания', 'все напоминания', 'напомин')
def notify_get(**kwargs):
    in_group_chat_error(kwargs["bot"], kwargs["chat_id"])
    d = Notify.objects.filter(chat_id=kwargs["chat_id"]).all().values_list('name', flat=True)
    count = Notify.objects.filter(chat_id=kwargs["chat_id"]).count()
    if len(d) != 0:
        text = 'Все что я помню:\n' + '\n'.join(d)
        text += f'\nОсталось {25 - count} записей.'
        vk.messages.send(chat_id=kwargs["chat_id"], message=text, random_id=0)


@search_command_handler(['бот, забудь', ': '], ['забудь', ': '])
def delete_notify(**kwargs):
    in_group_chat_error(kwargs["bot"], kwargs["chat_id"])
    chat_id, name = kwargs["chat_id"], kwargs["splited"]
    if len(name) > 1:
        name = name[1]
    else:
        error = 'Команда не верна.❌\nбот, забудь: [название]\nВсе напоминания: Бот, напоминания'
        return_error(error=error, chat_id=chat_id)
    notifies = Notify.objects.filter(chat_id=chat_id, name=name).first()
    if notifies is None:
        return_error(error=f'Название {name} не найдено ❌', chat_id=chat_id)
    notifies.delete()
    vk.messages.send(chat_id=chat_id, message=f'Напоминание удалено ✅', random_id=0)