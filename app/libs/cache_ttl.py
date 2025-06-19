"""
 Author: Czm
 Date: 2023/03/1
 Describe:
"""
import random


class CacheTTLBase(object):
    """ 缓存有效期 单位：秒 """
    # 缓存有效期的基础值:用户token有效期(10小时)
    TTL = 10 * 60 * 60

    # 缓存有效期的偏差上限,防止缓存雪崩
    MAX_DELTA = 2 * 60

    @classmethod
    def get_val(cls):
        return cls.TTL + random.randint(0, cls.MAX_DELTA)


class UserProfileCacheTTL(CacheTTLBase):
    pass


class FifteenHoursCacheTTL(CacheTTLBase):
    # 15小时
    TTL = 15 * 60 * 60


class OneDayOfCacheTTL(CacheTTLBase):
    # 1天
    TTL = 1 * 24 * 60 * 60


class ThreeDayOfCacheTTL(CacheTTLBase):
    # 3天
    TTL = 3 * 24 * 60 * 60


class SevenDayOfCacheTTL(CacheTTLBase):
    # 7天
    TTL = 7 * 24 * 60 * 60


class OneMonthOfCacheTTL(CacheTTLBase):
    # 30天
    TTL = 30 * 24 * 60 * 60


class MobileVerifyCodeCacheTTL(CacheTTLBase):
    # 1分钟
    TTL = 60

    # 验证码不许需要防止雪崩,存活时间固定为60秒
    @classmethod
    def get_val(cls):
        return cls.TTL


class FormMobileVerifyCodeCacheTTL(CacheTTLBase):
    # 5分钟
    TTL = 60 * 5

    # 验证码不许需要防止雪崩,存活时间固定为60秒
    @classmethod
    def get_val(cls):
        return cls.TTL


class ConvertedCacheTTL(CacheTTLBase):
    # 2小时
    TTL = 2 * 60 * 60


class FormPwdTryTimesTTL(CacheTTLBase):
    # 固定2分钟
    TTL = 60 * 2

    @classmethod
    def get_val(cls):
        return cls.TTL


class LoginAndMobileCodeTryTimesTTL(CacheTTLBase):
    # 固定1分钟
    TTL = 60 * 1

    @classmethod
    def get_val(cls):
        return cls.TTL
