import requests

v = '5.130'
token = "b745b9145286c4c97f8d136f944f6bca7f7dd0c2817fe20c222d70a8c1e7a12a7bf0d0a9595604f5ce0df"
vk_api_url = "https://api.vk.com/method/"


class methods(object):
    __slots__ = '_method'

    def __init__(self, method=None):
        self._method = method

    def __getattr__(self, method):
        return methods(method=f'{self._method}.{method}')

    def __call__(self, **kwargs):
        """
        :param method: Метод выполняемый в вк апи
        :param kwargs: Аргументы для этого метода
        :return: https://vk.com/dev/methods
        """
        if self._method is None:
            print("error", "Method not entered")
            self.return_traceback('Method not entered')
        kwargs.update({"v": v, "access_token": token})
        method = self._method.split('>.')[1]
        if method == "messages.send":
            if len(kwargs['message']) > 3000:
                first_message = kwargs['message'][:len(kwargs['message']) // 2]
                second_message = kwargs['message'][len(kwargs['message']) // 2:]
                kwargs['message'] = first_message
                requests.get(vk_api_url + method, params=kwargs)
                kwargs['message'] = second_message
                rw = requests.get(vk_api_url + method, params=kwargs)
                return rw.json()
        rw = requests.get(vk_api_url + method, params=kwargs)
        try:
            if rw.json().get('error'):
                print('error:', rw.json()["error"]["error_msg"])
        except Exception as e:
            print(e)
        return rw.json()


class message_handler(object):
    def connect_to_methods(self):
        return methods(self)

class EventInformation:
    __slots__ = ["payload", "clear_query", "group_id", "chat_id", "message", "type", "text", "from_id", "peer_id",
                 "conversation_message_id", "send_id", "splited_text", "lower", "group"]

    def __init__(self, raw_query: dict, splited_text: list = None):
        if splited_text is not None:
            self.splited_text = splited_text
        self.clear_query = raw_query["object"]
        self.type = raw_query['type']
        self.group_id = raw_query["group_id"]
        self.chat_id = self.clear_query['message']['peer_id']
        self.from_id = self.clear_query["message"]["from_id"]
        if self.chat_id > 2000000000:
            self.chat_id = self.chat_id - 2000000000
        self.peer_id = self.clear_query['message']['peer_id']
        self.message = self.clear_query['message']
        self.text = self.clear_query['message']['text']
        self.lower = self.text.lower()
        self.payload = self.clear_query['message'].get("payload")
        self.conversation_message_id = self.clear_query["message"]["conversation_message_id"]
        self.group = False if self.peer_id == self.from_id else True
        self.send_id = {"user_id": self.chat_id} if self.peer_id == self.from_id else {"chat_id": self.chat_id}
