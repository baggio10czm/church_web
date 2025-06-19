"""
 Author: Czm
 Date: 2021/11/15
 Time: 14:52
 Describe:图书标签跟书籍对应关系
"""
from sqlalchemy import Column, orm, Integer
from app.models.base import Base, db
from sqlalchemy.dialects.mysql import INTEGER


class ResourceTag(Base):
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    resource_id = Column(Integer, nullable=False, index=True, comment='关联书籍id')
    tag_id = Column(Integer, nullable=False, index=True, comment='关联标签id')

    @orm.reconstructor
    def __init__(self):
        """
            @orm.reconstructor
            这个装饰,可以让模型每次被调用是执行构造函数(默认是不执行的)
            不能更改类变量,会影响所有实例化对象
            最终形态: 配合base基类中的 keys、hide、append
        """
        super().__init__()
        self.fields = ['id', 'resource_id', 'tag_id', 'status', 'update_time', 'create_time']

    @classmethod
    def create_all(cls, resource_id, tag_ids):
        if isinstance(tag_ids, list):
            for tag_id in tag_ids:
                model = ResourceTag()
                model.resource_id = resource_id
                model.tag_id = tag_id
                db.session.add(model)
