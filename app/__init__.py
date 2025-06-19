"""
 Author: Czm
 Date: 2023/03/1
 Describe:
"""
import redis
from app.app import Flask
from app.models.base import db
from app.api.church import create_blueprint
import logging
from logging.handlers import TimedRotatingFileHandler
# from logging.handlers import SMTPHandler
import datetime


def create_app():
    application = Flask(__name__)
    application.config.from_object('app.config.setting')
    application.config.from_object('app.config.secure_test')

    # 注册蓝图
    application.register_blueprint(create_blueprint(), url_prefix='/church')

    # 注册db
    db.init_app(application)
    with application.app_context():
        db.create_all()

    # redis
    application.redis_cache = redis.Redis(host=application.config['REDIS_HOST'],
                                          port=application.config['REDIS_PORT'],
                                          db=application.config['REDIS_DB'],
                                          decode_responses=True)

    # 日志

    formatter = logging.Formatter(
        "[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s] - %(message)s")
    # when='D':按天分割    interval=1:1天     backupCount=15:备份15天
    handler = TimedRotatingFileHandler(
        f"logs/{datetime.datetime.now().strftime('%Y-%m-%d')}.log", when="D", interval=1, backupCount=15,
        encoding="UTF-8", delay=False, utc=True)

    application.logger.addHandler(handler)
    handler.setFormatter(formatter)

    # Email Handler
    # mail_handler = SMTPHandler(
    #     mailhost='smtp.qq.com',
    #     fromaddr='admin@officeTool.com',
    #     toaddrs=['122300413@qq.com'],
    #     subject='Flask Application Error'
    # )
    # mail_handler.setLevel(logging.ERROR)
    # mail_handler.setFormatter(logging.Formatter(
    #     "[%(asctime)s][%(module)s:%(lineno)d][%(levelname)s] - %(message)s"
    # ))
    # application.logger.addHandler(mail_handler)

    return application
