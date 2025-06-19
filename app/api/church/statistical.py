"""
 Author: Czm
 Date: 2023/2/1
 Describe:
"""
from flask import g, jsonify, current_app
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.book_record import BookRecord
from app.models.resource import Books
from app.models.redis_cache.statistical import NumberOfOnlineCache, NumberOfDataCache
from datetime import datetime, timedelta

from app.models.user import User

api = Redprint('statistical')


@api.route('/get_overall', methods=['GET'])
@auth.login_required
def get_overall():
    # 基础统计数据：用户数+书籍数量
    data = {
        'allBooks': NumberOfDataCache("books").get(), 
        'allUsers': NumberOfDataCache('users').get(),
        'allOnline': NumberOfOnlineCache().get()
    }
    return jsonify(data)


@api.route('/get_overdue_borrowing_record', methods=['GET'])
@auth.login_required
def get_overdue_borrowing_record():
    # 当前时间减去一个月的时间
    one_month_ago = int((datetime.now() - timedelta(days=30)).timestamp())
    # 筛选一个月前借书(还没还)的数据,联图书和用户表查询
    overdue_books = db.session.query(BookRecord, Books, User).join(Books, BookRecord.book_id == Books.id).join(User, BookRecord.user_id == User.id).filter(
        BookRecord.operation_date < one_month_ago,
        BookRecord.church_id == g.user.church_id,
        BookRecord._fettle == 2,
        BookRecord.is_borrowed == 1
    ).all()
    result = []
    for record, book, user in overdue_books:
        result.append({
            'user_name': user.username,
            'user_mobile': user.mobile,
            'book_id': record.book_id,
            'book_name': book.name,
            'book_cover': book.cover,
            'operation_date': record.operation_date,
            'fettle': record._fettle,
            'is_borrowed': record.is_borrowed
        })
    return result
