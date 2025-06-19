"""
 Author: Czm
 Date: 2023/03/1
 Describe:
"""
from datetime import date
from enum import Enum
from flask import Flask as _Flask
from flask.json.provider import DefaultJSONProvider as _JSONEncoder
from flask_sqlalchemy import Pagination
from app.libs.error_code import ServerError


class JSONEncoder(_JSONEncoder):
    @staticmethod
    def default(o):
        """
            default 本身支持递归处理
            类变量无法用__dict__获取,需要在构造函数里赋值(实例变量)
            dict()可拿到类变量和实例变量(但要改变对象一些方法)
        """
        # return o.__dict__
        # 检查 o 是否包含 keys 和 __getitem__ 属性
        if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        # 可能遇到复杂的情况,对象属性中有无法格式化的 dete 类型处理
        # 利用default自身递归调用的特性
        # 如果遇到其他无法处理的类型 就加 if…… 针对性的处理
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d  %H:%M')
        # user类的'auth'读取是枚举类型
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Pagination):
            return {'page': o.page, 'total': o.total, 'items': o.items}
        if isinstance(o, bytes):
            # 格式化字节数据
            return o.decode("utf-8")
        # 处理类对象
        if hasattr(o, '__dict__'):
            return o.__dict__
        # 如果传进来的对象没有 keys 和 __getitem__ 就报服务器错误
        # 开发人员将不合规的对象传入,不需要让客户端知道
        raise ServerError()


class Flask(_Flask):
    json_provider_class = JSONEncoder
