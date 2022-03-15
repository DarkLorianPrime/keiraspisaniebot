import json
import re
import traceback

from django.http import HttpResponse
from django.views import View

from vkhandler.Utils.commands.text import *
from .Utils.Modules.Config import vk
from .Utils.Modules.Main import Group_settings, Groups_users, Notifies_text, Common_raspisanie, Usual_functionality
from .Utils.Modules.Utils.decorators import search_commands, commands, json_commands


class EventHandler(View):
    def post(self, request, *args, **kwargs):
        response = json.loads(request.body)
        type_response = response.get('type')
        if type_response == 'confirmation':
            return HttpResponse('5cd0f49b')
        try:
            if type_response == 'message_new':
                text = response['object']['message']['text']
                lower = text.lower()
                chat_id = response['object']['message']['peer_id'] - 2000000000
                peer_id = response['object']['message']['peer_id']
                user_id = response['object']['message']['from_id']
                conversation_message_id = response['object']['message']['conversation_message_id']
                print(str(chat_id) + ' : ' + text)
                bot = True if peer_id != user_id else False

                if commands.get(lower) is not None:
                    commands[lower](chat_id=chat_id, peer_id=peer_id, text=text, user_id=user_id, bot=bot)
                    return

                for i in search_commands:
                    if re.search(i, lower):
                        splited = text.split(search_commands[i][1])
                        if len(splited) > 1:
                            search_commands[i][0](chat_id=chat_id, peer_id=peer_id, text=text, user_id=user_id, bot=bot,
                                                  splited=splited, conversation_message_id=conversation_message_id)
                            return

                if response['object']['message'].get('payload') is not None:
                    payload_data = response['object']['message'].get('payload')
                    load = json.loads(payload_data)
                    button = load.get("button")
                    if button is None:
                        button = "page"
                    if load.get("button") is None and load.get(button) is None:
                        button = "group"
                    if json_commands.get(button) is not None:
                        json_commands[button](chat_id=chat_id, peer_id=peer_id, text=text, user_id=user_id, bot=bot,
                                              payload=load.get(button), conversation_message_id=conversation_message_id)
                        return
                if response['object']['message'].get('action') is not None:
                    action = response['object']['message']['action']
                    if action['type'] == 'chat_invite_user' and action['member_id'] == -145807659:
                        print('invited in new chat')
                        vk.messages.send(chat_id=chat_id, random_id=0, message=get_text_text('hello'))
        except Exception:
            print(traceback.print_exc())
        finally:
            return HttpResponse('ok', content_type="application/text", status=200)
