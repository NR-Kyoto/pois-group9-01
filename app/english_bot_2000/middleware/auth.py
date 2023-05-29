from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect

class AuthMiddleware(MiddlewareMixin):
    def process_response(self, request, response):

        # 未ログイン
        if not request.user.is_authenticated:

            # ログインと登録はOK
            if ('/login/' in request.path) or ('/login/signup/' in request.path): 
                return response

            return HttpResponseRedirect('/login/')


        return response