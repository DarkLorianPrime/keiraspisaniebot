from django.utils.deprecation import MiddlewareMixin


class MiddlewareResponse(MiddlewareMixin):
    def process_response(self, request, response):
        response.status_code = 200
        response.content_type = 'application/text'
        response.data = 'ok'
        return response
