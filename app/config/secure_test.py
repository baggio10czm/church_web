"""
 Author: Czm
 Date: 2023/03/1
 Time: 15:00
 Describe:涉及安全等重要的配置
"""

DEBUG = True
PORT = 7000
HOST = '127.0.0.1'

SECRET_KEY = 'AasYTg1eq985cjq_dcmx7&yhDEcjq7&WTDSyyy7&HFGK618Czm7&6VBMGF4%$@!'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:cs258369@localhost:3306/church_official?charset=utf8mb4'
# ‘SQLALCHEMY_TRACK_MODIFICATIONS’ 这项配置在未来的版本中会被默认为禁止状态，
# 把它设置为True即可取消warning。
SQLALCHEMY_TRACK_MODIFICATIONS = False
# 连接池最大数量200,连接最多200秒
# SQLALCHEMY_ENGINE_OPTIONS = {
#     'pool_size': 200,
#     'pool_recycle': 200
# }
