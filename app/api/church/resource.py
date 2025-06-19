"""
 Author: Czm
 Date: 2023/03/1
 Describe:
"""

from sqlalchemy import desc
from sqlalchemy.orm import aliased
from app.libs.image_processing import image_processing
from app.libs.token_auth import auth
from app.libs.redprint import Redprint
from app.models.base import db
from app.models.resource_tag import ResourceTag
from app.models.resource import Resource
from flask import current_app, request, g, jsonify
from app.libs.error_code import Success, NotFound, PermissionDenied, NotEnough, DataFileFormatNotAllow, OpenDataFileError, DataFileTitleNotDifferent
from app.models.category import Category
from app.models.publish import Publish
from app.models.recommend import Recommend
from app.models.redis_cache.statistical import NumberOfDataCache
from app.models.tag import Tag
from app.models.user import User
from app.validators.resource import BookForm, EditBookForm, IDForm, SearchBooksForm, SetTagForm, SearchBookRecordForm

api = Redprint('resource')


@api.route('/create', methods=['POST'])
@auth.login_required
def create_resource():
    form = BookForm().validate_for_api()
    # 创建资源
    Resource.create(form)
    # 清空缓存
    NumberOfDataCache("books").clear()
    return Success()


@api.route('/get', methods=['GET'])
@auth.login_required
def get_resources():
    form = SearchBooksForm().validate_for_api()
    query = '%' + form.query.data + '%'
    filters = [Resource.name.like(query), Resource.status == 1]
    # 当开启编辑模式时,只能获取自己拥有修改权限的资源
    if form.is_edit.data and g.user.scope != 'AdminScope':
        filters.append(Resource.manager_id == g.user.id)
    if form.category_id.data:
        filters.append(Resource.category_id == form.category_id.data)
    if form.recommend_id.data:
        filters.append(Resource.recommend_id == form.recommend_id.data)
    
    # 别名定义
    UserManager = aliased(User)
    query = db.session.query(Resource, Category.name, Recommend.name, Publish.name, UserManager.username). \
        outerjoin(Category, Resource.category_id == Category.id). \
        outerjoin(Recommend, Resource.recommend_id == Recommend.id). \
        outerjoin(Publish, Resource.publish_id == Publish.id). \
        outerjoin(UserManager, Resource.manager_id == UserManager.id) \
        .filter(*filters) \
        .order_by(desc(Resource.update_time))
    # 检索查询结果
    resources = query.paginate(page=form.page.data, per_page=form.page_size.data, error_out=False)
    
    data = []
    for i, resource in enumerate(resources.items):
        # 获取资源所有标签对应关系
        resource_tags = ResourceTag.query.filter_by(resource_id=resource[0].id).all()
        # 得到资源所有标签id
        tags_ids = [tag.tag_id for tag in resource_tags]
        # 如果筛选标签,又不在资源标签中就跳过(不添加到data中)
        if form.tag_id.data and form.tag_id.data not in tags_ids:
            continue
        # 获取资源所有标签信息
        tags = Tag.query.filter(Tag.id.in_(tags_ids), Tag.status == 1).all()
        resource_data = {
            'resource': resource[0],
            'category_name': resource[1],
            'recommend_name': resource[2],
            'publish_name': resource[3],
            'manager_name': resource[4],
            'tags': tags
        }
        data.append(resource_data)

    return jsonify({
        'page': resources.page,
        'total': resources.total,
        'items': data
    })


@api.route('/edit', methods=['PUT'])
@auth.login_required
def edit_resource():
    form = EditBookForm().validate_for_api()
    resource = check_permissions(form.id.data)
    # 编辑资源
    Resource.edit(resource, form)
    return Success()


def check_permissions(resource_id):
    resource = Resource.query.filter_by(id=resource_id).first()
    if not resource:
        raise NotFound()
    # 检查资源管理员是否有该资源的权限（只有管理员和资源管理者可以操作）
    if g.user.scope == 'BookAdminScope' and resource.manager_id != g.user.id:
        raise PermissionDenied('对此资源没有权限')
    return resource


@api.route('/cover_upload', methods=['POST'])
@auth.login_required
def cover_upload():
    file = request.files['cover']
    return image_processing(file, is_avatar=False)


@api.route('/set_tag', methods=['PUT'])
@auth.login_required
def set_tag():
    form = SetTagForm().validate_for_api()
    current_resource_id = form.id.data
    check_permissions(current_resource_id)
    current_reduce_ids = form.reduce_ids.data
    with db.auto_commit():
        for add_id in form.add_ids.data:
            # 先判断添加的id是否"合法"
            tag = Tag.query.filter_by(id=add_id).first()
            if not tag:
                current_app.logger.warning(f'用户{g.user.username}想添加"非法"的tagID')
                continue
            resource_tag = ResourceTag()
            resource_tag.resource_id = current_resource_id
            resource_tag.tag_id = add_id
            db.session.add(resource_tag)
        if len(current_reduce_ids) > 0:
            will_delete_ResourceTags = ResourceTag.query \
                .filter(ResourceTag.tag_id.in_(current_reduce_ids), ResourceTag.resource_id == current_resource_id).all()
            for resource_tag in will_delete_ResourceTags:
                resource_tag.delete()
    return Success()


@api.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_resource():
    form = IDForm().validate_for_api()
    resource = check_permissions(form.id.data)
    with db.auto_commit():
        resource.delete()
    # 清空缓存
    NumberOfDataCache("books").clear()
    return Success()


@api.route('/book_record', methods=['GET'])
@auth.login_required
def get_book_record():
    form = SearchBookRecordForm().validate_for_api()
    query = db.session.query(BookRecord, User). \
        join(User, BookRecord.user_id == User.id). \
        filter(BookRecord.book_id == form.book_id.data) \
        .order_by(desc(BookRecord.create_time))
    # 检索查询结果
    book_records = query.paginate(page=form.page.data, per_page=form.page_size.data, error_out=False)
    data = []
    for item in book_records.items:
        record, user = item
        record_data = {
            'book_id': record.book_id,
            'user_id': record.user_id,
            'fettle': record.fettle,
            'is_borrowed': record.is_borrowed,
            'operation_date': record.operation_datetime,
            'remark': record.remark,
            'create_time': record.create_time,
            'username': user.username,
            # 其他 BookRecord 和 User 的字段
        }
        data.append(record_data)
    return jsonify(data)

