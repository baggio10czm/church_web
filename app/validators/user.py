"""
 Author: Czm
 Date: 2023/03/1
 Time: 21:10
 Describe:
"""
from wtforms import StringField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Regexp, length, NumberRange, EqualTo, AnyOf, Optional, Email
from app.validators.base import BaseForm as Form


class IDForm(Form):
    id = IntegerField(validators=[DataRequired("请传入用户id")])


class EmailForm(Form):
    email = StringField('邮箱', validators=[DataRequired("请输入邮箱"), Email(message='请输入正确的邮箱格式')])


class AuthForm(Form):
    auth = StringField(validators=[DataRequired("用户权限不能为空"), AnyOf(['PlatformAdminScope', 'AdminScope', 'BookAdminScope', 'MemberScope'], message='用户权限值错误')])


class VerifyEmailCodeForm(EmailForm):
    code = IntegerField(validators=[DataRequired("请输入验证码"), NumberRange(min=10000, max=99999, message='验证码为5位随机数字')])


class LoginForm(EmailForm):
    password = StringField(validators=[
        DataRequired(message='请输入密码'),
        Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}$', 0, "密码格式不对(密码长度是6-22位)")
    ])
    captcha = IntegerField(validators=[DataRequired("请输入验证码"), NumberRange(min=10000, max=99999, message='验证码为5位随机数字')])


class BaseUserForm(AuthForm):
    username = StringField(validators=[DataRequired("请输入用户名"), length(min=2, max=20, message='用户名长度为2-20位')])
    avatar = StringField(validators=[Optional()], default="")
    gender = StringField(validators=[DataRequired("性别不能为空"), AnyOf(['male', 'female'], message='性别值错误')])
    remark = StringField(validators=[length(max=255, message='备注不能超过255位')])


class EditUserForm(IDForm, BaseUserForm):
    pass


class EditUserAuthForm(IDForm, AuthForm):
    pass


class UserForm(EmailForm, BaseUserForm):
    password = StringField(validators=[
        DataRequired(message='请输入密码'),
        Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}$', 0, "密码格式不对(密码长度是6-22位)")
    ])


class BassChangePasswordForm(Form):
    # 密码
    new_password = StringField(validators=[
        DataRequired(message='请输入新密码'),
        Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}$', 0, "密码格式不对(密码长度是6-22位)"),
        EqualTo('repeat_password', message='两次输入密码不相同')
    ])
    repeat_password = StringField(validators=[
        DataRequired(message='请输入确认密码'),
        length(6, 32, message='6-32位密码')
    ])


class ChangePasswordForm(BassChangePasswordForm):
    old_password = StringField(validators=[
        DataRequired(message='请输入原密码'),
        Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}$', 0, "原密码格式不对(密码长度是6-22位)")
    ])


class AdminChangePasswordForm(IDForm, BassChangePasswordForm):
    pass


class EditUserRemarkForm(IDForm):
    remark = StringField(validators=[length(max=255, message='备注不能超过255位')])


class SearchForm(Form):
    query = StringField(length(max=50, message='搜索关键字过长'), default='')
    page = IntegerField(validators=[NumberRange(min=1, max=100000, message='页码值错误')], default=1)
    page_size = IntegerField(validators=[NumberRange(min=1, max=1000, message='每页显示数错误')], default=15)


class SearchChurchUserForm(SearchForm):
    pass


class ChangeUsernameForm(IDForm):
    username = StringField(validators=[DataRequired("请输入用户名"), length(min=2, max=20, message='用户名长度为2-20位')])
