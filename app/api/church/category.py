"""
 Author: Czm
 Date: 2023/03/1
 Describe:
"""
from flask import g, jsonify
from sqlalchemy import desc
from app.libs.error_code import Success, NotFound, PermissionDenied
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.category import Category
from app.validators.base import IDForm, CreateForm, EditForm, SearchForm


api = Redprint('category')


@api.route('/create', methods=['POST'])
@auth.login_required
def create():
    form = CreateForm().validate_for_api()
    Category.create(form)
    return Success()


@api.route('/edit', methods=['PUT'])
@auth.login_required
def edit():
    form = EditForm().validate_for_api()
    model = base_check(form)
    Category.edit(form, model)
    return Success()


@api.route('/set_status', methods=['PUT'])
@auth.login_required
def set_status():
    form = IDForm().validate_for_api()
    model = base_check(form)
    with db.auto_commit():
        if model.status == 0:
            model.activation()
        else:
            model.delete()
    return Success()


def base_check(form):
    model = Category.query.filter(Category.id == form.id.data).first()
    if not model:
        raise NotFound('分类不存在/或被禁用')
    return model


@api.route('/get', methods=['GET'])
@auth.login_required
def get():
    form = SearchForm().validate_for_api()
    query = '%' + form.query.data + '%'
    data = Category.query.filter(Category.name.like(query), Category.status == 1) \
        .order_by(desc(Category.create_time)).paginate(page=form.page.data, per_page=form.page_size.data, error_out=False)
    return jsonify(data)
