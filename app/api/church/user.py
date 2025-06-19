"""
 Author: Czm
 Date: 2023/03/1
 Describe:
"""
from flask import jsonify, current_app, session, g, request
from itsdangerous import URLSafeTimedSerializer
from sqlalchemy import or_, desc
from app.libs.captcha import captcha
from app.libs.enums import AuthTypeEnum
from app.libs.error_code import Success, CaptchaError, UserPasswordError, AccountIsDisable, \
    Forbidden, UserNotFound, NotFound, TryTimesIsTooMuch
from app.libs.image_processing import image_processing
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.redis_cache.statistical import NumberOfOnlineCache, NumberOfDataCache
from app.models.redis_cache.user import UserCache, AllTryTimes
from app.models.user import User
from app.validators.user import UserForm, LoginForm, ChangePasswordForm, AdminChangePasswordForm, IDForm, \
    SearchForm, SearchChurchUserForm, ChangeUsernameForm, EditUserRemarkForm, EditUserForm, EditUserAuthForm

api = Redprint('user')


# @api.route('/one_create', methods=['GET'])
# def one_create():
#     with db.auto_commit():
#         church = Church()
#         church.name = '图书馆平台'
#         church.mobile = '15677309009'
#         church.init_pwd = 'GL7xian'
#         db.session.add(church)
#         user = User()
#         user.username = '忠明哥'
#         user.mobile = '15677309009'
#         user.church_id = 1
#         user.password = 'xian7czm'
#         user.avatar = ""
#         user.gender = 'male'
#         user.group_id = 0
#         user.remark = 'xian7czm'
#         user.auth = AuthTypeEnum.PlatformAdminScope
#         db.session.add(user)
#     return Success()


@api.route('/create', methods=['POST'])
@auth.login_required
def create_user():
    form = UserForm().validate_for_api()
    # 检查此邮箱是否已经被注册
    User.check_duplicate(form.email.data)
    # 创建用户
    User.create(form)
    # 用户数统计缓存
    NumberOfDataCache('users').clear()
    return Success()


@api.route('/edit', methods=['PUT'])
@auth.login_required
def edit_user():
    form = EditUserForm().validate_for_api()
    user_id = form.id.data
    user = User.query.get(user_id)
    if not user:
        raise UserNotFound('用户不存在或已被禁用!')
    User.edit(user, form)
    return Success()


@api.route('/login', methods=['POST'])
def get_token():
    form = LoginForm().validate_for_api()
    email = form.email.data
    # 防止暴力破解处理
    all_try_times_manage(interface='login')
    # 获取用户输入的验证码
    code = form['captcha'].data
    # 获取session中的验证码
    s_code = session.get("captcha", None)
    if not s_code:
        raise CaptchaError(msg='验证码已过期')
    if not code or int(code) != int(s_code):
        raise CaptchaError(msg='验证码错误')
    identity = User.verify(email, form.password.data)
    # 验证通过,生成令牌
    token = generate_auth_token(identity['id'],
                                identity['username'],
                                identity['login_key'],
                                identity['scope']
                                )
    data = {
        'token': token
    }
    # 清除session中的验证码
    session.pop('captcha', None)
    # 清除在线人数的缓存
    NumberOfOnlineCache().clear()
    return jsonify(data), 201


def generate_auth_token(user_id, username, login_key, scope=None):
    """
        生成令牌
        id 用户id    ac_type用户登录类型
        scope 作用域  expiration 过期时间(秒)
    """
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    # token中保存用户id和登录类型
    return s.dumps({
        'id': user_id,
        'username': username,
        'login_key': login_key,
        'scope': scope
    })


def get_user_ip():
    try:
        if request.headers.get('X-Forwarded-For'):
            return request.headers['X-Forwarded-For']
        elif request.headers.get('X_Real_IP'):
            return request.headers.get('X_Real_IP')
        else:
            return request.remote_addr
    except Exception as e:
        current_app.logger.error(e)


def all_try_times_manage(interface, add=0):
    """
        通过用户ip
        记录ip总尝试数 / 记录ip接口总尝试数
        并响应处理=告警
    """
    user_ip = get_user_ip()
    if not user_ip or len(user_ip) < 3:
        current_app.logger.error('没有获取到IP?')
        return
    # 记录ip尝试总数
    interface_try_times = AllTryTimes(user_ip, interface).get()
    AllTryTimes(user_ip, interface).incr()
    # 达到尝试次数，就记录IP地址
    if interface_try_times >= (current_app.config['MAX_TRY_TIME_OF_RECORD'] + add):
        with open('script/blacklist.conf', 'a+', encoding='utf-8') as f:
            f.seek(0)
            already_exists = False
            contents = f.readlines()
            for content in contents:
                if user_ip in content:
                    already_exists = True
                    break
            if not already_exists:
                f.write('deny ' + user_ip + ';\n')
    if interface_try_times >= (current_app.config['MAX_TRY_TIME_OF_INTERFACE'] + add):
        raise TryTimesIsTooMuch()


@api.route('/info', methods=["GET"])
@auth.login_required
def get_info():
    user_profile = UserCache(g.user.id).get()
    del user_profile['login_key']
    return jsonify(user_profile)


@api.route('/get_captcha', methods=["GET"])
def get_captcha():
    # 防止暴力刷新
    all_try_times_manage(interface='captcha', add=10)
    """ 获取图形验证码 """
    # 获取图形验证码
    code, image = captcha.generate_captcha()
    # 存入session
    session["captcha"] = code
    # 使session有效期生效
    session.permanent = True
    headers = {
        'content-type': 'image/png'
    }
    return image, 200, headers


@api.route('/change_username', methods=['PUT'])
@auth.login_required
def change_username():
    form = ChangeUsernameForm().validate_for_api()
    user_id = g.user.id
    is_platform_admin = g.user.scope == 'PlatformAdminScope'
    username = form.username.data
    user = User.query.filter_by(id=form.id.data).first()
    if not user:
        raise UserNotFound()
    with db.auto_commit():
        user.username = username
    user_profile = UserCache(user_id).get()
    user_profile['username'] = username
    UserCache(user_id).set(user_profile)
    return Success()


@api.route('/change_self_password', methods=['PUT'])
@auth.login_required
def change_self_password():
    """
     修改自己的密码
    """
    form = ChangePasswordForm().validate_for_api()
    change_password(g.user.id, form, g.user.scope == 'PlatformAdminScope', True)
    return Success()


@api.route('/change_user_password', methods=['PUT'])
@auth.login_required
def change_user_password():
    """
     修改所有用户的密码(平台+管理用)
    """
    form = AdminChangePasswordForm().validate_for_api()
    user_id = form.id.data
    is_platform_admin = g.user.scope == 'PlatformAdminScope'
    change_password(user_id, form, is_platform_admin)
    return Success()


def change_password(user_id, form, is_platform_admin=False, check_password=False):
    user = User.query.get(user_id)
    if not user:
        raise AccountIsDisable()
    # 除了平台管理,其他人不能更改平台员工/管理的账户状态
    if not is_platform_admin and user.auth == AuthTypeEnum.PlatformAdminScope:
        raise Forbidden()
    if check_password and not user.check_password(form.old_password.data):
        raise UserPasswordError(msg='原密码错误!')
    with db.auto_commit():
        user.password = form.new_password.data


@api.route('/change_user_status', methods=['PUT'])
@auth.login_required
def change_user_status():
    form = IDForm().validate_for_api()
    user_id = form.id.data
    is_platform_admin = g.user.scope == 'PlatformAdminScope'
    # 超权检测 不是平台管理就只能修改本教会的
    not is_platform_admin and permission_check(user_id)
    change_status(user_id, is_platform_admin)
    return Success()


def change_status(user_id, is_platform_admin=False):
    if user_id == g.user.id:
        raise Forbidden(msg='您无法禁用自己的账户')
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise UserNotFound()
    # 除了平台管理,其他人不能更改平台员工/管理的账户状态
    if not is_platform_admin and user.auth == AuthTypeEnum.PlatformAdminScope:
        raise Forbidden()
    # 用户状态取反(软删除or激活)
    with db.auto_commit():
        if user.status == 0:
            user.activation()
        else:
            user.delete()
            # 清除缓存防止用户还可以继续使用
            UserCache(user.id).clear()


@api.route('/change_user_auth', methods=['PUT'])
@auth.login_required
def change_user_auth():
    form = EditUserAuthForm().validate_for_api()
    user_id = form.id.data
    is_platform_admin = g.user.scope == 'PlatformAdminScope'
    # 平台操作时不会permission_check,所以还是先检查用户是否存在
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise UserNotFound()
    change_auth(user)
    return Success()


def change_auth(user):
    user_id = user.id
    if user_id == g.user.id:
        raise Forbidden(msg='您无法改变自己的权限！')
    if user.auth == AuthTypeEnum.PlatformAdminScope:
        raise Forbidden(msg='平台管理权限无法更改！')
    # 用户权限取反(管理or员工)
    with db.auto_commit():
        user.auth = AuthTypeEnum.MemberScope if user.auth == AuthTypeEnum.AdminScope else AuthTypeEnum.AdminScope
    UserCache(user_id).clear()


@api.route('/get_platform_user', methods=['GET'])
@auth.login_required
def get_platform_user():
    # user模型类 是用 '_auth' 代替数据库中的
    form = SearchForm().validate_for_api()
    query = '%' + form.query.data + '%'
    users = User.query.filter(User._auth == 1, or_(User.email.like(query), User.username.like(query))) \
        .order_by(desc(User.create_time)).paginate(page=form.page.data, per_page=form.page_size.data, error_out=False)
    return jsonify(users)


@api.route('/get_church_user', methods=['GET'])
@auth.login_required
def get_church_user():
    form = SearchChurchUserForm().validate_for_api()
    query = '%' + form.query.data + '%'
    # 获取所有非平台管理员用户
    users = db.session.query(User)\
        .filter(User._auth != 1, or_(User.email.like(query), User.username.like(query))) \
        .order_by(desc(User.create_time)).paginate(page=form.page.data, per_page=form.page_size.data, error_out=False)
    return jsonify(users)


@api.route('/get_church_admin', methods=['GET'])
@auth.login_required
def get_church_admin():
    # 获取管理员用户
    users = db.session.query(User)\
        .filter(User._auth.in_([2, 3])) \
        .order_by(desc(User.create_time)).all()
    return jsonify(users)


@api.route('/logout', methods=['POST'])
@auth.login_required
def logout():
    # 清空用户缓存+在线人数缓存
    UserCache(g.user.id).clear()
    NumberOfOnlineCache().clear()
    return Success()


@api.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_user():
    form = IDForm().validate_for_api()
    user_id = form.id.data
    user = User.query.get(user_id)
    if not user:
        raise UserNotFound('用户不存在或已被删除!')
    if user_id == g.user.id:
        raise Forbidden(msg='您无法删除自己的账户')
    # 除了平台管理,其他人不能删除平台管理的账户
    if g.user.scope != 'PlatformAdminScope':
        if user.auth == AuthTypeEnum.PlatformAdminScope:
            raise Forbidden('你无权删除平台管理账户')
    with db.auto_commit():
        # 将用户真实删除
        db.session.delete(user)
    # 清空此用户 + 在线人数缓存信息
    UserCache(user_id).clear()
    NumberOfOnlineCache().clear()
    return Success()


@api.route('/edit_user_remark', methods=['PUT'])
@auth.login_required
def edit_user_remark():
    form = EditUserRemarkForm().validate_for_api()
    user_id = form.id.data
    user = User.query.get(user_id)
    if not user:
        raise UserNotFound('用户不存在或已被删除!')
    with db.auto_commit():
        user.remark = form.remark.data
    return Success()


@api.route('/avatar_upload', methods=['POST'])
@auth.login_required
def avatar_upload():
    file = request.files['avatar']
    return image_processing(file, is_avatar=True)
