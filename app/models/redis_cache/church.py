"""
 Author: Czm
 Date: 2023/03/1
 Time: 18:03
 Describe:教会相关的缓存处理
"""
import json
from flask import current_app
from redis import RedisError
from app.libs.cache_ttl import FifteenHoursCacheTTL
from app.models.redis_cache.base import Base


class ChurchCache(Base):

    def __init__(self, church_id):
        self.key = 'xa-books_church:{}:profile'.format(church_id)
        self.church_id = church_id

    def save(self):
        from app.models.church import Church
        church_profile = Church.query.filter_by(id=self.church_id).first()
        if church_profile:
            self.set({
                'id': church_profile.id,
                'name': church_profile.name,
                'init_pwd': church_profile.init_pwd})
            return church_profile
        else:
            return None

    def set(self, data):
        try:
            current_app.redis_cache.setex(self.key,
                                          FifteenHoursCacheTTL.get_val(),
                                          json.dumps(data))
        except RedisError as e:
            current_app.logger.error(e)

    def clear(self):
        current_app.redis_cache.delete(self.key)

    def exists(self):
        pass
