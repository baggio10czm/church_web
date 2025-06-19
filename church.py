from flask import current_app
from app import create_app
from werkzeug.exceptions import HTTPException
from app.libs.error import APIException
from app.libs.error_code import ServerError

app = create_app()


@app.errorhandler(Exception)
def framework_error(e):
    """
        全局异常处理:
        e 可能是 APIException,HTTPException
        或 Exception, 但都需要返回JSON格式的数据
    """
    if isinstance(e, APIException):
        return e
    if isinstance(e, HTTPException):
        code = e.code
        msg = e.description
        error_code = 7979
        return APIException(msg, code, error_code)
    else:
        # 调试模式可能需要返回详细信息就不抛出 ServerError 了
        if not app.config['DEBUG']:
            # 记录日志
            current_app.logger.error(f'服务器错误:{e}')
            return ServerError()
        else:
            raise e


if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])

