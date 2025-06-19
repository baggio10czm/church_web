"""
 Author: Czm
 Date: 2023/03/1
 Time: 22:47
 Describe:
"""
from app.libs.error import APIException


# 400 参数错误 401 未授权 403 禁止访问  404 找不到资源
# 500 服务器未知错误
# 200 请求成功 201 创建、更新成功 204 删除成功
# 301 302 重定向

class Success(APIException):
    code = 200
    msg = 'okay'
    error_code = 0


class ServerError(APIException):
    code = 500
    msg = '抱歉!服务器出错,请稍后再试。'
    error_code = 999


class NotFound(APIException):
    code = 404
    msg = '访问资源不存在！'
    error_code = 404


class NotEnough(APIException):
    code = 404
    msg = '资源不足！'
    error_code = 409


class DataError(APIException):
    code = 400
    msg = '数据出错!请联系管理员！'
    error_code = 40000


class ParameterException(APIException):
    """ 通用参数错误 """
    code = 400
    msg = '传入的参数错误'
    error_code = 4000


class CaptchaError(APIException):
    code = 400
    msg = '验证码过期或验证错误'
    error_code = 4001


class DuplicateUser(APIException):
    code = 400
    msg = '用户手机已被注册'
    error_code = 1001


class AuthFailed(APIException):
    code = 401
    msg = '授权失败'
    error_code = 1005


class Forbidden(APIException):
    code = 401
    msg = '你没有此操作的权限!'
    error_code = 1004


# 账户不存在或密码错误,提示信息保持一致
# 处于(安全考虑),不让用户知道具体的原因
class UserPasswordError(APIException):
    code = 401
    msg = '账户密码错误或被禁用'
    error_code = 1005


class UserNotFound(APIException):
    code = 400
    msg = '用户不存在或已被禁用'
    error_code = 1007


class AccountIsDisable(APIException):
    code = 401
    msg = '账户不存在或已被禁用'
    error_code = 1008


class DuplicateLogin(APIException):
    code = 403
    msg = '重复登录或是账户状态被更改'
    error_code = 1009


class TryTimesIsTooMuch(APIException):
    code = 403
    msg = '短时间内尝试过多，请1分钟之后再试！'
    error_code = 1010


class AuthProblem(APIException):
    code = 401
    msg = '已被禁用'
    error_code = 2001


class Duplicate(APIException):
    code = 400
    msg = '已存在,请不要重复添加!'
    error_code = 2002


class PermissionDenied(APIException):
    code = 4003
    msg = '你没有操作此资源的权限！'
    error_code = 2003


class ChurchIdIsDifferent(APIException):
    code = 4003
    msg = '教会Id不一致！'
    error_code = 2004


class ImageFormatNotAllow(APIException):
    code = 400
    msg = '图片格式不支持，只支持png、jpg、gif格式'
    error_code = 3001


class UploadFileSizeError(APIException):
    code = 400
    msg = '图片太大，已超过10M'
    error_code = 3002


class UploadFileTypeError(APIException):
    code = 400
    msg = '图片上传出错，请换一图片试试'
    error_code = 3003


class DataFileFormatNotAllow(APIException):
    code = 400
    msg = '数据格式不支持，只支持xls、xlsx格式'
    error_code = 4001


class OpenDataFileError(APIException):
    code = 400
    msg = '打开数据文件出错!'
    error_code = 4002


class DataFileTitleNotDifferent(APIException):
    code = 400
    msg = '数据文件标题与系统预置的不一致!'
    error_code = 4003
