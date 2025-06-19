"""
 Author: Czm
 Date: 2023/03/1
 Time: 22:47
 Describe: 重写覆盖flask的错误处理
"""
from flask import request, json
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    code = 500
    msg = '抱歉!服务器出错,请稍后再试。'
    error_code = 999

    def __init__(self, msg=None, code=None, error_code=None,
                 headers=None):
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if msg:
            self.msg = msg
        super(APIException, self).__init__(msg, None)

    def get_body(self, environ=None, scope=None):
        """
            重写get_body方法
        """
        body = dict(
            msg=self.msg,
            error_code=self.error_code,
            request=request.method + ' ' + self.get_url_no_param()
        )
        text = json.dumps(body)
        return text

    def get_headers(self, environ=None, scope=None):
        """
            重写get_headers方法
            返回json格式的数据
        """
        return [('Content-Type', 'application/json')]

    @staticmethod
    def get_url_no_param():
        """
            得到没有参数的完整url
        """
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]
