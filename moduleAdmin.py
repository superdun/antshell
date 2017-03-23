# -*- coding: utf-8 -*-

from flask_admin.contrib.sqla import ModelView
from dbORM import db, User, Post
from wtforms import TextAreaField, SelectField
from wtforms.widgets import TextArea
import thumb
from flask_admin import form
import flask_login
import os
import os.path as op
from moduleGlobal import app, admin, qiniu_store, QINIU_DOMAIN, TAG, UPLOAD_URL
import shutil
from flask_admin._compat import  urljoin

def dashboard():
    admin.add_view(UserView(User, db.session))
    admin.add_view(PostView(Post, db.session))


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class ImgageUploadTemplate(form.ImageUploadInput):
    def get_url(self, field):
        if field.thumbnail_size:
            filename = field.thumbnail_fn(field.data)
        else:
            filename = field.data

        if field.url_relative_path:
            filename = urljoin(field.url_relative_path, filename)
        return QINIU_DOMAIN+filename
class ImageUpload(form.ImageUploadField):
    widget = ImgageUploadTemplate()
    def _save_file(self, data, filename):
        path = self._get_path(filename)
        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path), self.permission | 0o111)

        data.seek(0)
        data.save(path)
        with open(path, 'rb') as fp:
            ret, info = qiniu_store.save(fp, filename)
            if 200 != info.status_code:
                raise Exception("upload to qiniu failed", ret)
            shutil.rmtree(os.path.dirname(path))
            return filename


class PostView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    # Override displayed fields
    column_list = ("name", "created_at", "view_count",
                   "tag", "status")

    form_overrides = {
        'content': CKTextAreaField
    }
    form_extra_fields = {
        'img': ImageUpload('Image', base_path=QINIU_DOMAIN, relative_path=thumb.relativePath()),
        'tag': SelectField(u'category', choices=TAG),
        'status': SelectField(u'status', choices=[('published', u'发布'), ('deleted', u'删除')]),
    }
    form_columns = ("name",
                    "tag", "status", "content", "img")
    form_excluded_columns = ('created_at')
    create_template = 'admin/post/create.html'
    edit_template = 'admin/post/edit.html'


class UserView(ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated
