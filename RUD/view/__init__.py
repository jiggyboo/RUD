from flask import request, jsonify, current_app, Response, g, abort
from flask.json import JSONEncoder
from functools import wraps

import jwt


###############################################################
#		   	  Decorators                          #
###############################################################
def login_required(f):  #name of the decorator
	@wraps(f)
	def decorated_function(*args, **kwargs):
		access_token = request.headers.get('Authroization')
		if access_token is not None:
			try:
				payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
			except jwt.InvalidTokenError:
				payload = None

			if  payload is None: return Response(status=401)

			user_id = payload['user_id']
			g.user_id = user_id
		else:
			return Response(status=401)

		return f(*args, **kwargs)
	return decorated_function

def create_endpoints(app, services):
    db_work = services.db_work
    rst_worker = services.rst_worker
    ip_ban_list = ['128.1.134.181', '178.128.92.95', '36.90.8.75', '161.35.188.242', '36.70.122.110', '45.32.17.205']

    @app.before_request
    def block_method():
        ip = request.environ.get('REMOTE_ADDR')
        if ip in ip_ban_list:
            print(f'blacklist ip {ip} trying to access website')
            abort(403)

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = db_work.create_new_user(new_user)
        new_user = db_work.get_user(new_user_id)

        return jsonify(new_user)

    @app.route("/api/ping", methods=['GET'])
    def ping():
        return "pong"

    @app.route("/api/search", methods=['GET'])
    def search():
        sub = request.args.get('sub')
        if request.args.get('num') == None:
            num = 40
        else:
            num = int(request.args.get('num'))
        tim = request.args.get('tim')
        typ = request.args.get('typ')

        return db_work.search(sub, num, tim, typ)

    @app.route("/api/searcht", methods=['GET'])
    def searcht():
        sub = request.args.get('sub')
        if request.args.get('num') == None:
            num = 30
        else:
            num = int(request.args.get('num'))
        tim = request.args.get('tim')
        typ = request.args.get('typ')

        return db_work.searcht(sub, num, tim, typ)

    @app.route("/api/cd", methods=['GET'])
    def cd():
        url = request.args.get('url')

        return db_work.cd(url)

    @app.route("/rst/api/dcnt", methods=['GET'])
    def rst_dcnt():
        return rst_worker.rstDCNT()

    @app.route("/rst/api/register", methods=['POST'])
    def rst_register():
        return jsonify(db_work.create_user(request.json))


    @app.route("/rst/api/login", methods=['POST'])
    def rst_login():
        credential = request.json
        authroized = db_work.login(credential)
        if authroized:
            user_credential = db_work.get_user_id_password(credential['email'])
            user_id = user_credential['user_id']
            token = db_work.generate_token(user_id)
            return jsonify({
                'user_id' :user_id,
                'token' : token
            })
        else:
            return '', 401

    @app.route("/rst/api/follow", methods=['POST'])
    @login_required
    def rst_follow():
        user_id = g.user_id
        ticker = request.json['ticker']
        return db_work.follow_stock(user_id, ticker)

    @app.route("/rst/api/unfollow", methods=['POST'])
    @login_required
    def rst_unfollow():
        user_id = g.user_id
        ticker = request.json['ticker']
        return db_work.unfollow_stock(user_id, ticker)

    @app.route("/rst/api/forgot", methods=['POST'])
    def rst_forgot():
        email = request.json['email']
        return db_work.forgot_password(email)