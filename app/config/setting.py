"""
 Author: Czm
 Date: 2023/03/1
 Time: 15:00
 Describe:
"""
from datetime import timedelta

HOST = '127.0.0.1'
# token 过期时间
TOKEN_EXPIRATION = 3 * 24 * 60 * 60
# 验证码session过期时间(包括手机验证码)
PERMANENT_SESSION_LIFETIME = timedelta(minutes=1)
# 数据每页显示条数
PER_PAGE = 15
# 图片上传允许的格式
ALLOWED_IMG_FORMAT = {'jpeg', 'jpg', 'png', 'gif'}
# 最大的上传文件大小(Flask 会拒绝内容长度大于 此值的请求进入，并返回一个 413 状态码)
MAX_CONTENT_LENGTH = 12 * 1024 * 1024
# 最大的上传文件大小(Flask 会拒绝内容长度大于 此值的请求进入，并返回一个 413 状态码)
MAX_IMPORT_DATA_FILE_LENGTH = 10.3 * 1024 * 1024
# 导入数据文件临时存放目录
IMPORT_DATA_FILES_DIR = 'temp_files/'
# 图片存储目录
IMG_FILES_DIR = 'images/'
# 最大的图片文件大小
MAX_IMAGE_LENGTH = 10.3 * 1024 * 1024
# 图片的最大像素
MAX_IMAGE_SIZE = 1200
# 头像的最大像素
AVATAR_IMAGE_SIZE = 300
# 接口1分钟内尝试最大次数
MAX_TRY_TIME_OF_INTERFACE = 5
# 频繁访问接口触发记录ip的次数
MAX_TRY_TIME_OF_RECORD = 60
# 管理员手机
ADMIN_OF_MOBILE = 15677309009
# 平台教会(id)
PLATFORM_ID = 1

# redis
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0


IMPORT_DATA_TITLE = ['序号', '书名', '分类', '价格', '作者', '出版社', '出版时间', '版次', 'ISBN', '图书简介', '独一码', '自编条码', '中图法', '索书号', '借阅次数', '创建时间', '当前借阅者', '共享者', '存放家庭', '失踪书籍']
