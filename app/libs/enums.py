"""
 Author: Czm
 Date: 2023/03/1
 Time: 22:47
 Describe:
"""
from enum import Enum


# 权限:平台管理/图书馆管理/教会成员
class AuthTypeEnum(Enum):
    PlatformAdminScope = 1
    AdminScope = 2
    BookAdminScope = 3
    MemberScope = 4


class BookStatusEnum(Enum):
    Return = 1
    Borrow = 2
    Lost = 3
    Gift = 4
