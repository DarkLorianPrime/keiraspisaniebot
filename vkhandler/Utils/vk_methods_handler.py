import requests

v = '5.130'
token = ''
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
            self.return_traceback('Method not entered')
        kwargs['v'] = v
        kwargs['access_token'] = token
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
                text_s = rw.json()["error"]["error_msg"]
                self.return_traceback(text_s)
        except Exception:
            pass
        return rw.json()

    def return_traceback(self, text_s):
        print('error:', text_s)


class message_handler(object):
    def connect_to_methods(self):
        return methods(self)
