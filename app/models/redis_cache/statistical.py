"""
 Author: Czm
 Date: 2023/03/1
 Time: 18:03
 Describe:统计相关的缓存处理
"""
import json
from flask import current_app
from redis import RedisError
from app.libs.cache_ttl import OneDayOfCacheTTL, SevenDayOfCacheTTL, OneMonthOfCacheTTL
from app.models.resource import Books
from app.models.redis_cache.base import Base
from app.models.user import User


class NumberOfPlatformCache(Base):
    """
        平台专用:
        统计用户+教会
    """

    model_map = {
        'allChurch': Church,
    }

    def __init__(self, type_name):
        self.key = 'xa-books_num_of_{}'.format(type_name)
        self.type_name = type_name

    def save(self):
        count = self.model_map[self.type_name].query.count()
        self.set(count)
        return count

    def set(self, count):
        try:
            current_app.redis_cache.setex(self.key,
                                          OneMonthOfCacheTTL.get_val(),
                                          json.dumps(count))
        except RedisError as e:
            current_app.logger.error(e)

    def clear(self):
        current_app.redis_cache.delete(self.key)


class NumberOfOnlineCache(Base):
    """
        统计在线人数+对应的资料
    """

    def __init__(self):
        self.key = 'xa-books_num_of_online'

    def save(self):
        all_online = current_app.redis_cache.keys('xa-books_user*')
        # 得到所有在线user的key
        key_list = []
        for online in all_online:
            key_list.append(online)
        # 通过key得到user数据
        user_data_list = []
        for key in key_list:
            user_data_list.append(json.loads(current_app.redis_cache.get(key)))
        self.set(user_data_list)
        return user_data_list

    def set(self, user_data_list):
        try:
            current_app.redis_cache.setex(self.key,
                                          OneDayOfCacheTTL.get_val(),
                                          json.dumps(user_data_list))
        except RedisError as e:
            current_app.logger.error(e)

    def clear(self):
        current_app.redis_cache.delete(self.key)


class NumberOfDataCache(Base):
    """
        数据相关统计
    """

    model_map = {
        'users': User,
        'books': Books,
    }

    def __init__(self, type_name):
        self.key = 'xa-books_num_of_{}'.format(type_name)
        self.type_name = type_name
        self.model = self.model_map[type_name]

    def save(self):
        # 获取所有有效数据的统计
        count = self.model.query.filter(self.model.status == 1).count()
        self.set(self.key, count)
        return count

    @staticmethod
    def set(key, count):
        try:
            current_app.redis_cache.setex(key,
                                          SevenDayOfCacheTTL.get_val(),
                                          json.dumps(count))
        except RedisError as e:
            current_app.logger.error(e)

    def clear(self):
        current_app.redis_cache.delete(self.key)
