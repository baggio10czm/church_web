"""
 Author: Czm
 Date: 2023/03/1
 Time: 18:03
 Describe:用户相关的缓存处理
"""
import json
from flask import current_app
from redis import RedisError
from app.libs.cache_ttl import UserProfileCacheTTL, LoginAndMobileCodeTryTimesTTL
from app.models.redis_cache.base import Base
from app.models.user import User


class UserCache(Base):

    def __init__(self, user_id):
        self.key = 'xa-books_user:{}:profile'.format(user_id)
        self.user_id = user_id

    def save(self):
        user = User.query.filter_by(id=self.user_id).first()
        if user:
            # 调用模型的方法处理和保存在缓存
            return User.get_profile(user)
        else:
            return None

    def set(self, user_data):
        try:
            current_app.redis_cache.setex(self.key,
                                          UserProfileCacheTTL.get_val(),
                                          json.dumps(user_data))
        except RedisError as e:
            current_app.logger.error(e)

    def clear(self):
        current_app.redis_cache.delete(self.key)

    def exists(self):
        pass


class AllTryTimes(Base):
    """
        记录一些接口的访问次数
    """

    def __init__(self, ip, times_of_type):
        self.key = 'times_of_{}:{}'.format(times_of_type, ip)

    def save(self):
        return 0

    def incr(self):
        try:
            current_app.redis_cache.incrby(self.key)
            current_app.redis_cache.expire(self.key,
                                           LoginAndMobileCodeTryTimesTTL.get_val())
        except RedisError as e:
            current_app.logger.error(e)
