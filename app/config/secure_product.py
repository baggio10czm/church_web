"""
 Author: Czm
 Date: 2023/03/1
 Time: 15:00
 Describe:涉及安全等重要的配置
"""

DEBUG = False
PORT = 7000

SECRET_KEY = '709CAasYTg7e@q215xz7vd_Cmx7&y09hDe_Cjq7&WT7DS_Yyy7&HF7%#GK548_Czm7&6VB7MGF45@_%$@!'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:zs258369@localhost:3306/xianBooks?charset=utf8mb4'
# ‘SQLALCHEMY_TRACK_MODIFICATIONS’ 这项配置在未来的版本中会被默认为禁止状态，
# 把它设置为True即可取消warning。
SQLALCHEMY_TRACK_MODIFICATIONS = False
# 连接池最大数量200,连接最多200秒
# SQLALCHEMY_ENGINE_OPTIONS = {
#     'pool_size': 200,
#     'pool_recycle': 200
# }

