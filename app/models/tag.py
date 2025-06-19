"""
 Author: Czm
 Date: 2023/03/1
 Describe:书籍标签
"""
from sqlalchemy import Column, String, orm
from sqlalchemy.dialects.mysql import INTEGER
from app.libs.error_code import Duplicate
from app.models.base import Base, db


class Tag(Base):
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(100), index=True, nullable=False, comment='标签名')
    remark = Column(String(200), comment='备注')

    @orm.reconstructor
    def __init__(self):
        """
            @orm.reconstructor
            这个装饰,可以让模型每次被调用是执行构造函数(默认是不执行的)
            不能更改类变量,会影响所有实例化对象
            最终形态: 配合base基类中的 keys、hide、append
        """
        super().__init__()
        self.fields = ['id', 'name', 'remark', 'status', 'update_time', 'create_time']

    @classmethod
    def create(cls, form):
        with db.auto_commit():
            model = Tag()
            model.name = form.name.data
            model.remark = form.remark.data
            db.session.add(model)

    @classmethod
    def edit(cls, form, model):
        # 检查名是否已经存在
        one = Tag.query.filter_by(name=form.name.data).first()
        # 当修改的数据与one不是同一数据才需要判断
        if one and form.id.data != one.id:
            raise Duplicate('名称已存在,请不要重复添加!')
        with db.auto_commit():
            model.name = form.name.data
            model.remark = form.remark.data
