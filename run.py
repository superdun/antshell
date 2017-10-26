# -*- coding: utf-8 -*-
import random
from flask import Flask, render_template, redirect, jsonify, request, flash, url_for
from dbORM import db, User, Post
import thumb
from moduleGlobal import app, qiniu_store, QINIU_DOMAIN, TAG, UPLOAD_URL
import moduleAdmin as admin
import flask_login
from werkzeug.contrib.cache import FileSystemCache

cache = FileSystemCache(cache_dir='cache/', default_timeout=0)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/products')
def products():
    return render_template('index.html')


@app.route('/aboutus')
def aboutus():
    return render_template('index.html')


@app.route('/career')
def career():
    return render_template('index.html')


@app.route('/live')
def live():
    # return render_template('live.html')
    liveStat = cache.get('goalLiveStat')
    if liveStat:
        if liveStat['stat'] == "on":
            return render_template('live.html')

    filePath = url_for('static', filename='video/cat%d.mp4' % random.randint(1, 4))
    return render_template('nolive.html', filePath=filePath)


@app.route('/livecontroller')
def livecontroller():
    # return render_template('live.html')

    return render_template('livecontroller.html')


@app.route('/api/live', methods=['POST', 'GET'])
def setliveApi():
    if request.method == 'POST':
        X = int(request.form['X'])
        Y = int(request.form['Y'])
        stat = request.form['stat']
        source = request.form['source']
        if source == "U":
            cache.set('goalLiveStat', {"X": X, 'Y': Y, "stat": stat}, timeout=0)
            print {'current': cache.get('currentLiveStat'), 'goal': cache.get('goalLiveStat')}
            return jsonify(cache.get('currentLiveStat'))
        else:
            cache.set('currentLiveStat', {"X": X, 'Y': Y, "stat": stat}, timeout=0)
            return jsonify(cache.get('goalLiveStat'))

    if request.method == 'GET':
        return jsonify({'current': cache.get('currentLiveStat'), 'goal': cache.get('goalLiveStat')})


@app.route('/admin/upload', methods=['POST'])
def upload():
    file = request.files.to_dict()['files[]']
    result = thumb.upload_file(file, UPLOAD_URL, QINIU_DOMAIN, qiniu_store)
    return jsonify(result)


@app.route('/api/test', methods=['POST', 'GET'])
def testApi():
    if request.method == 'POST':
        uid = request.form['uid']
        name = request.form['name']
        cache.delete('testData')
        cache.set('testData', {"uid": uid, 'name': name})

        return jsonify({'status': 'ok', 'content': {"uid": uid, 'name': name}})
    if request.method == 'GET':
        rv = cache.get('testData')
        print 'get '
        if rv is None:
            return jsonify({'status': 'error'})
        uid = rv['uid']
        name = rv['name']
        return jsonify({'status': 'ok', 'content': {"uid": uid, 'name': name}})


@app.route('/api/verify', methods=['GET'])
def CheckTestApi():
    username = request.args.get('username')
    psswd = request.args.get('psswd')
    if username == 'LiDun' and psswd == "ZuiShuai":
        return jsonify({'status': 'ok', 'code': '200', 'content': {"uid": 123546, 'name': 'LiDun'}})

    return jsonify({'status': 'failed', 'code': '400'})


@app.route('/api/cat', methods=['POST', 'GET'])
def cat():
    if request.method == 'POST':

        quantity = request.form['quantity']
        password = request.form['password']

        if quantity == '1':
            quantityTime = 0.2
        elif quantity == '2':
            quantityTime = 0.3
        else:
            quantityTime = 0.4
        if password == 'cat123456':
            cache.delete('catData')
            cache.set('catData', [quantityTime, "open"])
            print cache.get('catData')
            return jsonify({'status': 'ok',
                            'content': {"quantityTime": cache.get('catData')[0], 'status': cache.get('catData')[1]}})
        else:
            return jsonify({'status': 'error', 'content': {}})

    if request.method == 'GET':
        rv = cache.get('catData')

        if rv is None:
            return jsonify({'status': 'close'})
        cache.delete('catData')
        return jsonify({"quantityTime": rv[0], 'status': rv[1]})


@app.route('/api/upload', methods=['POST'])
def uploadApi():
    if 'Photo' not in request.files:
        flash('No file part')
        return jsonify({"status": "failed", "msg": "No file part"})
    file = request.files['Photo']
    if file.filename == '':
        flash('No selected file')
        return jsonify({"status": "failed", "msg": "No selected file"})
    if file:
        result = thumb.upload_file(file, UPLOAD_URL, QINIU_DOMAIN, qiniu_store)
        if result['result'] != 1:
            return jsonify({"status": "failed", "msg": "server busy"})

        cache.set("PhotoUrl", result['localUrl'])
        return jsonify({"status": "ok", "msg": "ok"})


@app.route('/showphoto', methods=['GET'])
def showPhoto():
    url = cache.get("PhotoUrl")
    return render_template("ShowPhoto.html", photoUrl=url)


# exam
@app.route('/exam/login', methods=['GET'])
def examLogin():
    return render_template("exam/login.html")


@app.route('/api/exam/login', methods=['POST'])
def examLoginApi():
    username = request.form['username']
    gongHao = request.form['gonghao']



    if username == u"张三":
        return jsonify({"stat": "ok", "paperCode": "123"})
    else:
        return jsonify({"stat": "failed", "paperCode": ""})

@app.route('/api/exam/result', methods=['POST'])
def examResultApi():
    return jsonify({"stat":"ok"})
@app.route('/exam', methods=['GET'])
def exam():
    paperCode = request.args.get('papercode')

    if paperCode == "123":
        user = {'name':u"张三"}
        data = [
            {"title": u"现有一只自重为12吨宽度1.8米的卧式冷卷，请配置正式工索具，使其正常起吊", 'q':
                [{"id":"1","title": u"撑架", 'img': url_for("static",filename="img/exam/1.jpg"), 'c': [u"30T*1.6M", u"30T*4M", u"30T*3.2M", u"30T*6M"]},
                 {"id":"2","title": u"下吊线", 'img': url_for("static",filename="img/exam/2.jpg"), 'c': [u"28mm*3m", u"28mm*6m", u"332mm*3m", u"32mm*6m"]},
                 {"id":"3","title": u"吊钩", 'img': url_for("static",filename="img/exam/3.jpg"), 'c': [u"5T", u"7T", u"11T", u"15T"]},
                 {"id":"4","title": u"尼龙带", 'img': url_for("static",filename="img/exam/4.jpg"), 'c': [u"10T*3.5m", u"15T*4m", u"5T*6m", u"20T*5m"]},
                 {"id":"5","title": u"卸扣", 'img': url_for("static",filename="img/exam/5.jpg"), 'c': [u"3.75T", u"4.25T", u"6.5T", u"8.5T"]},
                 ]

             }]
        return render_template("exam/paper.html", user=user,data=data)
    return render_template("exam/failed.html", msg="无此考卷，重新登陆或联系管理员"
                           )
@app.route('/exam/result', methods=['GET'])
def examResult():

    return render_template("exam/result.html")
#    AABAC

# admin
admin.dashboard()
# login


login_manager = flask_login.LoginManager()

login_manager.init_app(app)
users = {}
raw_users = User.query.all()
for user in raw_users:
    users[user.name] = {'password': user.password}


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return

    user = User()
    user.id = username
    return user


@login_manager.request_loader
def request_loader(request):
    name = request.form.get('name')
    if name not in users:
        return

    user = User()
    user.id = name

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[name]['password']

    return user


@app.route('/api/login', methods=['POST', ])
def loginApi():
    name = str(request.form['name'])
    if request.form['password'] == users[name]['password']:
        user = User()
        user.id = name
        flask_login.login_user(user)
        return jsonify({'status': 'OK'})

    return jsonify({'status': 'bad login'})


@app.route('/login')
def login():
    if flask_login.current_user.is_authenticated:
        return redirect('/admin')
    return render_template('login.html')


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


application = app
if __name__ == '__main__':
    app.run(port=8080)
