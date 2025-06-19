"""
 Author: Czm
 Date: 2023/03/1
 Time: 21:10
 Describe:
"""
from wtforms import StringField, IntegerField, FieldList, BooleanField
from wtforms.validators import DataRequired, length, Optional, NumberRange, AnyOf
from app.validators.base import BaseForm as Form


class IDForm(Form):
    id = IntegerField(validators=[DataRequired("请传入id")])


class BaseBookForm(Form):
    ...


class BookForm(Form):
    name = StringField(validators=[DataRequired("请输入书名"), length(min=1, max=100, message='书名长度为1-100位')])
    desc = StringField(validators=[Optional(), length(min=1, max=255, message='书籍简介长度不超过255')])
    cover = StringField(validators=[Optional()])
    manager_id = IntegerField(validators=[DataRequired("请选择管理者")])
    unique = StringField(validators=[Optional()])
    author = StringField(validators=[Optional()])
    publish_id = IntegerField(validators=[Optional()])
    price = StringField(validators=[Optional()])
    isbn = StringField(validators=[Optional()])
    category_id = IntegerField(validators=[DataRequired("请选择分类")])
    recommend_id = IntegerField(validators=[Optional()])
    # 添加书籍时需要 tags_ids
    tags_ids = FieldList(IntegerField(validators=[Optional()]))
    count = IntegerField(validators=[NumberRange(min=1, message='数量不能小于1错误')], default=1)
    remark = StringField(validators=[length(max=255, message='备注不能超过255位')])


class EditBookForm(IDForm, BookForm):
    pass


class SetRecordStatusForm(Form):
    book_id = IntegerField(validators=[DataRequired("请传入id")])
    user_id = IntegerField(validators=[DataRequired("请选择操作对象")])
    operation_date = IntegerField(validators=[DataRequired("操作日期")])
    fettle = StringField(validators=[DataRequired("请设置书籍的状态"), AnyOf(['Return', 'Borrow', 'Lost', 'Gift'], message='书籍状态值错误')])
    remark = StringField(validators=[length(max=255, message='备注不能超过255位')])


class SearchBooksForm(Form):
    query = StringField(length(max=50, message='搜索关键字过长'), default='')
    category_id = IntegerField(validators=[Optional()])
    recommend_id = IntegerField(validators=[Optional()])
    tag_id = IntegerField(validators=[Optional()])
    is_edit = BooleanField(validators=[Optional()], default=False)
    page = IntegerField(validators=[NumberRange(min=1, message='页码值错误')], default=1)
    page_size = IntegerField(validators=[NumberRange(min=1, message='每页显示数错误')], default=15)


class SetTagForm(IDForm):
    add_ids = FieldList(IntegerField(validators=[Optional()]))
    reduce_ids = FieldList(IntegerField(validators=[Optional()]))


class SearchBookRecordForm(Form):
    book_id = IntegerField(validators=[DataRequired("请传入id")])
    page = IntegerField(validators=[NumberRange(min=1, message='页码值错误')], default=1)
    page_size = IntegerField(validators=[NumberRange(min=1, message='每页显示数错误')], default=15)

