"""
 Author: Czm
 Date: 2023/03/1
 Describe:
"""
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, length
from app.validators.base import BaseForm as Form


class IDForm(Form):
    id = IntegerField(validators=[DataRequired("请传入id")])


class TypeForm(Form):
    name = StringField(validators=[DataRequired("请输入名称"), length(min=2, max=50, message='名称长度为2-50位')])
    remark = StringField(validators=[length(max=255, message='备注不能超过255位')])


class EditCategoryForm(TypeForm, IDForm):
    ...


class ManagerIdForm(Form):
    manager_id = IntegerField(validators=[DataRequired("请传入小组管理id")])


class GroupForm(TypeForm, ManagerIdForm):
    ...


class EditGroupForm(IDForm, TypeForm, ManagerIdForm):
    ...
