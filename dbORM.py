from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('localConfig.py')
db = SQLAlchemy(app)


# db




class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    auth = db.Column(db.String(120))
    password = db.Column(db.String(120))
    mobile = db.Column(db.String(120))
    def __init__(self, name='', auth=1, password='',mobile=''):
        self.name = name
        self.auth = auth
        self.password = password
        self.mobile=mobile
    def __repr__(self):
        return '<User %r>' % self.name

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    tag = db.Column(db.String(80))
    img = db.Column(db.String(120))
    content = db.Column(db.String(5000))
    created_at=db.Column(db.String(120))
    status=db.Column(db.String(120))
    view_count = db.Column(db.Integer)
    def __init__(self,name='',tag='',img='',content='',created_at='',status='',view_count=0):
        self.name = name
        self.tag = tag
        self.img = img
        self.content=content
        self.created_at = time.time()
        self.tag=tag
        self.view_count=view_count
        self.status=status

    def __repr__(self):
        return '<Post name %r>' % self.source
