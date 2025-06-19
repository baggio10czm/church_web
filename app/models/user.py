"""
 Author: Czm
 Date: 2023/03/1
 Describe:
"""
import random
from sqlalchemy import Column, String, SmallInteger, orm, Enum, text
from sqlalchemy.dialects.mysql import INTEGER
from werkzeug.security import generate_password_hash, check_password_hash
from app.libs.enums import AuthTypeEnum
from app.libs.error_code import DuplicateUser, UserNotFound, UserPasswordError
from app.models.base import Base, db


class User(Base):
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, comment='用户名')
    gender = Column(Enum('male', 'female', name='gender'), server_default=text('"male"'), nullable=False, comment='性别')
    avatar = Column(String(120), nullable=False, server_default=text('""'), comment='头像')
    email = Column(String(120), unique=True, nullable=False, comment='邮箱作为用户账户')
    _auth = Column('auth', SmallInteger, nullable=False, server_default=text('4'), comment='教会管理员=1,教会成员=2')
    _password = Column('password', String(120))
    remark = Column(String(255), comment='备注')

    @orm.reconstructor
    def __init__(self):
        """
            最终形态: 配合base基类中的 keys、hide、append
            @orm.reconstructor
            这个装饰,可以让模型每次被调用是执行构造函数(默认是不执行的)
        """
        super().__init__()
        self.fields = ['id', 'username', 'gender', 'avatar', 'email', 'auth', 'status', 'remark', 'update_time', 'create_time']

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    # auth赋值对应的枚举,方面直接比较,不用.value
    @property
    def auth(self):
        return AuthTypeEnum(self._auth)

    # 改写auth设置时是设置的枚举对应的值
    @auth.setter
    def auth(self, auth_name):
        self._auth = auth_name.value

    @staticmethod
    def create(form):
        with db.auto_commit():
            model = User()
            write_data(model, form.data)
            db.session.add(model)

    @staticmethod
    def edit(user, form):
        with db.auto_commit():
            write_data(user, form.data)
        # 清空用户信息缓存
        from app.models.redis_cache.user import UserCache
        UserCache(form.id.data).clear()

    @classmethod
    def verify(cls, email, password):
        user = User.query.filter_by(email=email).first()
        if not user:
            raise UserNotFound()
        if not user.check_password(password):
            raise UserPasswordError(msg='账户或密码错误!')
        return cls.get_profile(user)

    @staticmethod
    def get_profile(user):
        # 生成scope level 对应的枚举值
        scope = user.auth.name
        # 生成随机的loginKey用以提醒重复登录
        user_profile = {'id': user.id,
                        'username': user.username,
                        'avatar': user.avatar,
                        'gender': user.gender,
                        'email': user.email,
                        'login_key': random_key(),
                        'scope': scope
                        }
        # 写入缓存,访问接口时比对login_key判断是否重复登录
        from app.models.redis_cache.user import UserCache
        UserCache(user.id).set(user_profile)
        return user_profile

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    @classmethod
    def check_duplicate(cls, email):
        # 用filter 包括被软删除的用户
        if cls.query.filter(cls.email == email, cls.status != 3).first():
            raise DuplicateUser()


def random_key(number=10):
    seed = 'ZFqVweGHJrtKyAui7465oplTkj9hBgfMNdsRazL283xEcvQbnCm10'
    return ''.join(random.choice(seed) for _ in range(number))


def write_data(model, data):
    for key, value in data.items():
        if key == 'auth':
            model.auth = AuthTypeEnum[data['auth']]
        elif value is not None:
            setattr(model, key, value)
