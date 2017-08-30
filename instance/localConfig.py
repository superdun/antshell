# -*- coding: utf-8 -*-
from flask import Flask

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost:3306/antshell'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = '123456'

QINIU_ACCESS_KEY = 'u1M-QQ-m0ciNAhDn2AZ6iODyKnjUmY7EW1uH2ZiZ'
QINIU_SECRET_KEY = 'QN3dDZvbX5MdDxfWsf4vua774Wz_5JFCZP78PGTU'
QINIU_BUCKET_NAME = 'makerimg'
QINIU_BUCKET_DOMAIN = 'http://oc1is8h9w.bkt.clouddn.com/'

TAG=[('mach', u'机械'), ('auto', u'自动化'), ('elec', u'电子'), ('IT', u"编程")]
DEBUG = True
SQLALCHEMY_ECHO = False
POST_PER_PAGE = 20
UPLOAD_URL = 'static/upload'
CAROUSEL_THUMBNAIL = ''
PREVIEW_THUMBNAIL = '-preview'

