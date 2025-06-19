import os
import uuid
from PIL import Image
from io import BytesIO
from flask import current_app, g
from app.libs.error_code import ImageFormatNotAllow, UploadFileSizeError, UploadFileTypeError


def image_processing(file, is_avatar):
    if file:
        # file_size = len(file.read())
        file_size = os.fstat(file.fileno()).st_size
        # 光标回到开始
        file.seek(0)
        if file.filename != 'blob' and not allowed_file(file.filename):
            raise ImageFormatNotAllow()
        # 文件大小不能超过10m太多
        if current_app.config['MAX_IMAGE_LENGTH'] < file_size:
            raise UploadFileSizeError()
        # 缩放图片
        img = image_resize(file, is_avatar)
        # 获取图片类型
        file_type = file.mimetype.rsplit("/", 1)[1]
        # 貌似会遇到RGBA转换RGB的错误,但没找到出现的条件就一杆子打死吧 if img.mode in ('RGBA', 'P'):
        if file_type in ['jpg', 'jpeg']:
            img = img.convert('RGB')
        # 貌似用jpeg也可以,但某些操作系统可能不支持超过三个字符以上的后缀名
        file_type = 'jpg' if file_type == 'jpeg' else file_type
        if is_avatar:
            filename = f"avatar-{g.user.id}-{uuid.uuid1().hex}.{file_type}"
        else:
            filename = f"cover-{g.user.id}-{uuid.uuid1().hex}.{file_type}"
        # 获取项目根目录
        project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        save_file_dir = os.path.join(project_path, current_app.config['IMG_FILES_DIR'])
        will_save_file_dir = os.path.join(save_file_dir, filename)
        img.save(will_save_file_dir)
        img.close()
        return filename
    else:
        raise UploadFileTypeError()


def allowed_file(filename):
    file_type = '.' in filename and filename.rsplit('.', 1)[1].lower()
    return file_type in current_app.config['ALLOWED_IMG_FORMAT']


def image_resize(file, is_avatar=False):
    try:
        img = Image.open(BytesIO(file.read()))
    except IOError as e:
        current_app.logger.error(f'打开图片错误:{e}')
        return ImageFormatNotAllow()
    width, height = img.size
    # 图片最大像素(分封面和头像两种情况)
    if is_avatar:
        max_image_size = current_app.config['AVATAR_IMAGE_SIZE']
    else:
        max_image_size = current_app.config['MAX_IMAGE_SIZE']
    allowed_width = min(max_image_size, width)
    allowed_height = min(max_image_size, height)
    # 同比例缩放高度，取较大作为缩放参照
    if width >= height:
        allowed_height = int(allowed_width / width * height)
    else:
        allowed_width = int(allowed_height / height * width)
    # 缩放尺寸和缩减图片大小
    img = img.resize((allowed_width, allowed_height), Image.LINEAR)
    return img
