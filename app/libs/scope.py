"""
 Author: Czm
 Date: 2023/03/1
 Time: 22:47
 Describe:
"""


class Scope:
    """
        Scope 基类
        使用set自动去重
        api 接口视图函数
        module 模块名
        forbidden 排除的接口视图函数
        set() 定义空的 set
    """
    allow_api = set()
    allow_module = set()
    forbidden = set()

    def __add__(self, other):
        """ 使对象支持相加操作 """
        self.allow_api = self.allow_api | other.allow_api
        self.allow_module = self.allow_module | other.allow_module
        self.forbidden = self.forbidden | other.forbidden

        # list 去重,直接用set就不需要去重了
        # self.allow_api = list(set(self.allow_api))

        # 返回自己可链式调用
        return self


class MemberScope(Scope):
    """
        教会员工权限
    """
    allow_api = {
        'church.user+logout',
        'church.user+get_info',
        'church.user+change_self_password',
        'church.statistical+get_overall',
        'church.resource+get_resources',
        'church.tag+get',
        'church.category+get',
    }


class BookAdminScope(Scope):
    """
        图书管理权限 = 教会成员 + 图书管理
    """
    allow_api = {
        'church.user+get_church_user',
        'church.user+get_church_admin',
        'church.resource+create_resource',
        'church.resource+edit_resource',
        'church.resource+delete_resource',
        'church.resource+cover_upload',
        'church.resource+set_tag',
        'church.category+create',
        'church.category+edit',
        'church.category+set_status',
        'church.tag+create',
        'church.tag+edit',
        'church.tag+set_status',
    }

    def __init__(self):
        self + MemberScope()


class AdminScope(Scope):
    """
        教会管理权限 = 教会成员 + 图书管理 + 教会管理
    """
    allow_api = {
        'church.user+create_user',
        'church.user+edit_user',
        'church.user+delete_user',
        'church.user+change_username',
        'church.user+change_user_password',
        'church.user+change_user_status',
        'church.user+change_user_auth',
        'church.user+edit_user_remark',
        'church.user+avatar_upload',
    }

    def __init__(self):
        self + MemberScope() + BookAdminScope()



def is_in_scope(scope, endpoint):
    # globals() 函数会以字典类型返回当前位置的全部全局变量。
    # 比如用户的权限是'PlatformAdminScope' 就等于 PlatformAdminScope()
    auth = globals()[scope]()
    # endpoint 因为视图是挂载在蓝图上的,所以会带有 church.xxx
    # 为了在 endpoint 中拿到模块名,
    # 需要在定义红图那里加上模块名self.name并用'+'分隔
    # 判断访用户是否有权限:
    # 先判断是否在排除名单
    # 在判断是否在对象的allow_api里
    # 最后判断是否在允许的模块中
    module = endpoint.split('+')[0]
    if endpoint in auth.forbidden:
        return False
    if endpoint in auth.allow_api:
        return True
    if module in auth.allow_module:
        return True
    else:
        return False
