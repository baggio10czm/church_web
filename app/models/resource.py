"""
 Author: Czm
 Date: 2023/03/1
 Describe:
"""
import uuid
from flask import g
from sqlalchemy import Column, String, SmallInteger, orm, text, TEXT
from sqlalchemy.dialects.mysql import INTEGER
from app.models.base import Base, db
from app.models.resource_tag import ResourceTag


class Resource(Base):
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(100), index=True, nullable=False, comment='书名')
    desc = Column(TEXT(100), nullable=True, comment='简介')
    unique = Column(String(100), unique=True, nullable=False, comment='唯一标识码')
    cover = Column(String(100), nullable=True, server_default=text('""'), comment='书籍封面')
    author = Column(String(200), index=True, nullable=True, server_default=text('""'), comment='作者')
    publish_id = Column(SmallInteger, index=True, nullable=True, comment='出版社id')
    price = Column(String(50), nullable=True, server_default=text('""'), comment='价格')
    isbn = Column(String(50), nullable=True, server_default=text('""'), comment='ISBN')
    category_id = Column(SmallInteger, index=True, nullable=False, comment='分类id')
    recommend_id = Column(SmallInteger, index=True, nullable=True, comment='推荐栏目id')
    manager_id = Column(SmallInteger, index=True, nullable=False, comment='管理员人id')
    count = Column(SmallInteger, nullable=False, server_default=text('1'), comment='书籍数量')
    remark = Column(String(200), comment='备注')

    @orm.reconstructor
    def __init__(self):
        """
            最终形态: 配合base基类中的 keys、hide、append
            @orm.reconstructor
            这个装饰,可以让模型每次被调用是执行构造函数(默认是不执行的)
        """
        super().__init__()
        self.fields = ['id', 'name', 'desc', 'unique', 'cover', 'author', 'publish_id', 'price', 'isbn', 'category_id', 'recommend_id',
                       'manager_id', 'count', 'status', 'remark', 'update_time', 'create_time']

    @staticmethod
    def create(form):
        with db.auto_commit():
            model = Resource()
            model.unique = 'resource-' + uuid.uuid1().hex
            write_data(model, form.data)
            db.session.add(model)
            # flush()执行SQL模拟生成数据,才可取model.id
            db.session.flush()
            # 指定书籍和标签关系
            ResourceTag.create_all(model.id, form.tags_ids.data)

    @staticmethod
    def edit(model, form):
        with db.auto_commit():
            write_data(model, form.data)


def write_data(model, data):
    for key, value in data.items():
        if value is not None:
            setattr(model, key, value)
