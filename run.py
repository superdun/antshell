import random
from flask import Flask, render_template,redirect,jsonify,request,flash,url_for
from dbORM import db,User, Post
import thumb
from moduleGlobal import app, qiniu_store, QINIU_DOMAIN, TAG, UPLOAD_URL
import moduleAdmin as admin
import flask_login
from werkzeug.contrib.cache import FileSystemCache


cache = FileSystemCache(cache_dir='cache/',default_timeout=0)




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
    if cache.get('liveSwitch')==1:
        return render_template('live.html')
    filePath = url_for('static', filename='video/cat%d.mp4'%random.randint(1,4))
    return render_template('nolive.html',filePath = filePath)
@app.route('/livecontroller')
def livecontroller():
    # return render_template('live.html')

    return render_template('livecontroller.html')

@app.route('/api/live', methods=['POST','GET'])
def setliveApi():

    if request.method=='POST':
        X = int(request.form['X'])
        Y = int(request.form['Y'])
        stat = request.form['stat']
        source = request.form['source']
        if source == "U":
            cache.set('goalLiveStat', {"X": X, 'Y': Y, "stat": stat}, timeout=0)
            print {'current':cache.get('currentLiveStat'),'goal':cache.get('goalLiveStat')}
            return jsonify(cache.get('currentLiveStat'))
        else:
            cache.set('currentLiveStat', {"X": X, 'Y': Y, "stat": stat}, timeout=0)
            return jsonify(cache.get('goalLiveStat'))

    if  request.method == 'GET':
        return jsonify({'current':cache.get('currentLiveStat'),'goal':cache.get('goalLiveStat')})

@app.route('/admin/upload', methods=['POST'])
def upload():
    file = request.files.to_dict()['files[]']
    result = thumb.upload_file(file, UPLOAD_URL, QINIU_DOMAIN, qiniu_store)
    return jsonify(result)

@app.route('/api/test', methods=['POST','GET'])
def testApi():
    if request.method=='POST':
        uid = request.form['uid']
        name = request.form['name']
        cache.delete('testData')
        cache.set('testData',{"uid":uid,'name':name})

        return jsonify({'status':'ok','content':{"uid":uid,'name':name}})
    if   request.method == 'GET':
        rv = cache.get('testData')
        print 'get '
        if rv is None:
            return jsonify({'status': 'error'})
        uid = rv['uid']
        name = rv['name']
        return jsonify({'status':'ok','content':{"uid":uid,'name':name}})

@app.route('/api/verify', methods=['GET'])
def CheckTestApi():
     username = request.args.get('username')
     psswd = request.args.get('psswd')
     if username == 'LiDun' and psswd == "ZuiShuai":
         return jsonify({'status': 'ok', 'code': '200', 'content': {"uid": 123546, 'name': 'LiDun'}})

     return jsonify({'status': 'failed', 'code': '400'})


@app.route('/api/cat', methods=['POST','GET'])
def cat():

    if request.method == 'POST':

        quantity = request.form['quantity']
        password = request.form['password']

        if quantity =='1':
            quantityTime = 0.2
        elif quantity =='2':
            quantityTime = 0.3
        else:
            quantityTime = 0.4
        if password == 'cat123456':
            cache.delete('catData')
            cache.set('catData', [quantityTime,"open"])
            print cache.get('catData')
            return jsonify({'status': 'ok', 'content': {"quantityTime": cache.get('catData')[0], 'status': cache.get('catData')[1]} })
        else:
            return jsonify({'status': 'error', 'content':{}})

    if request.method == 'GET':
        rv = cache.get('catData')

        if rv is None:
            return jsonify({'status': 'close'})
        cache.delete('catData')
        return jsonify({ "quantityTime": rv[0], 'status': rv[1]})

@app.route('/api/upload', methods=['POST'])
def uploadApi():
    if 'Photo' not in request.files:
        flash('No file part')
        return jsonify({"status":"failed","msg":"No file part"})
    file = request.files['Photo']
    if file.filename == '':
        flash('No selected file')
        return jsonify({"status": "failed", "msg": "No selected file"})
    if file :
        result = thumb.upload_file(file,UPLOAD_URL,QINIU_DOMAIN,qiniu_store)
        if result['result'] != 1:
            return jsonify({"status": "failed", "msg": "server busy"})

        cache.set("PhotoUrl", result['localUrl'])
        return  jsonify({"status": "ok", "msg": "ok"})

@app.route('/showphoto', methods=['GET'])
def showPhoto():
    url = cache.get("PhotoUrl")
    return render_template("ShowPhoto.html",photoUrl=url)

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
