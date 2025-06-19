"""
 Author: Czm
 Date: 2023/03/1
 Time: 22:47
 Describe:
"""
from collections import namedtuple
from flask import current_app, g, request
from flask_httpauth import HTTPTokenAuth
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, BadTimeSignature
from app.libs.error_code import AuthFailed, Forbidden, AccountIsDisable, DuplicateLogin
from app.libs.scope import is_in_scope
from app.models.redis_cache.user import UserCache

auth = HTTPTokenAuth()

# namedtuple 支持.访问不需['']
user_nt = namedtuple('User', ['id', 'username', 'scope', 'login_key'])


@auth.verify_token
def verify_password(token):
    user_info = verify_auth_token(token)
    if not user_info:
        return False
    else:
        # 用g变量保存,方面全局调用(方便、安全)
        g.user = user_info
        return True


def verify_auth_token(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        user_info = s.loads(token, max_age=current_app.config['TOKEN_EXPIRATION'])
    except BadTimeSignature:
        raise AuthFailed(msg='您的登录已经失效', error_code=1003)
    except BadSignature:
        raise AuthFailed(msg='授权token错误', error_code=1002)
    user_id = user_info['id']
    # 检查账户是否有效
    user_profile = UserCache(user_id).get()
    if not user_profile:
        raise AccountIsDisable()
    # 重复登录(如果账户被禁用,又激活也会导致重复登录的报错,
    # 因为redis缓存被删除,login_key会重新生成)
    if user_profile['login_key'] != user_info['login_key']:
        raise DuplicateLogin()
    # user_info
    user_id = user_info['id']
    username = user_info['username']
    login_key = user_info['login_key']
    scope = user_info['scope']
    # 判断用户是否用权限访问改api
    allow = is_in_scope(scope, request.endpoint)
    if not allow:
        raise Forbidden()
    # 用namedtuple 保存在g里的数据可用.的方式访问(方便)
    return user_nt(user_id, username, scope, login_key)
