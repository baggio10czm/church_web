"""
 Author: Czm
 Date: 2021/03/1
 Describe:
"""
from flask import Blueprint
from app.api.church import user, statistical, category, resource, tag


def create_blueprint():
    blue_print = Blueprint('church', __name__)

    # 红图注册在蓝图里
    user.api.register(blue_print)
    statistical.api.register(blue_print)
    category.api.register(blue_print)
    resource.api.register(blue_print)
    tag.api.register(blue_print)

    return blue_print
