"""
 Author: Czm
 Date: 2023/03/1
 Time: 20:24
 Describe:
"""
import json
from flask import current_app
from redis import RedisError


class Base:
    key = ''

    def save(self):
        pass

    def get(self):
        """ 信息缓存数据 string类型 """
        try:
            data = current_app.redis_cache.get(self.key)
        except RedisError as e:
            current_app.logger.error('%r' % e)
            data = None

        if data is not None:
            return json.loads(data)
        else:
            return self.save()
