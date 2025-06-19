"""
 Author: Czm
 Date: 2023/03/1
 Time: 15:02
 Describe:
"""
from flask import request
from wtforms import Form, StringField, IntegerField
from wtforms.validators import DataRequired, length, NumberRange, Optional
from app.libs.error_code import ParameterException


def listMap(errors_text, msgList):
    for msg in msgList:
        if isinstance(msg, list):
            listMap(errors_text, msg)
        else:
            errors_text.append(msg)


class BaseForm(Form):
    def __init__(self):
        # 在内部调用,在外部就不用每次都传了
        # data = request.json
        # 用get_json 如果传过来的json是空的也不会报错
        data = request.get_json(silent=True)
        # 获取url?后面的参数
        args = request.args.to_dict()
        super(BaseForm, self).__init__(data=data, **args)

    def validate_for_api(self):
        # 调用父类的validate方法进行参数验证
        valid = super(BaseForm, self).validate()
        if not valid:
            # 取得form.errors 的错误信息
            msgList = list(self.errors.values())
            # 用递归得到信息的一维数组
            errors_text = []
            listMap(errors_text, msgList)
            # 错误信息是多维list 需要sum()变为一维,再转字符串
            # raise ParameterException(msg=",".join(sum(msgList, [])))
            raise ParameterException(msg=",".join(errors_text))
        # 返回form 外部就可以链式调用(简化代码)
        return self


class IDForm(BaseForm):
    id = IntegerField(validators=[DataRequired("请传入id")])


class CreateForm(BaseForm):
    name = StringField(validators=[DataRequired("请输入名称"), length(min=1, max=100, message='名称长度为1-100位')])
    remark = StringField(validators=[Optional(), length(max=255, message='备注不能超过255位')])


class EditForm(IDForm):
    name = StringField(validators=[DataRequired("请输入名称"), length(min=1, max=100, message='名称长度为1-100位')])
    remark = StringField(validators=[Optional(), length(max=255, message='备注不能超过255位')])


class SearchForm(BaseForm):
    query = StringField(validators=[Optional(), length(max=50, message='搜索关键字过长')], default='')
    page = IntegerField(validators=[NumberRange(min=1, max=100000, message='页码值错误')], default=1)
    page_size = IntegerField(validators=[NumberRange(min=1, max=1000, message='每页显示数错误')], default=15)

