from flask import request, jsonify, current_app, Response, g
from flask.json import JSONEncoder
from functools import wraps

import jwt

###############################################################
#					   	  Decorators                          #
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
			g.user = get_user(user_id) if user_id else None
		else:
			return Response(status=401)

		return f(*args, **kwargs)
	return decorated_function

def create_endpoints(app, services):
    db_work = services.db_work
    dc_cache = services.dc_cache

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = user_service.create_new_user(new_user)
        new_user = user_service.get_user(new_user_id)

        return jsonify(new_user)

    @app.route("/api/ping", methods=['GET'])
    def ping():
        return "pong"

    @app.route("/api/dcnt", methods=['GET'])
    def dcnt():
        return dc_cache.dcnt()

    @app.route("/api/search", methods=['GET'])
    def search():
        sub = request.args.get('sub')
        if request.args.get('num') == None:
            num = 30
        else:
            num = int(request.args.get('num'))
        tim = request.args.get('tim')
        typ = request.args.get('typ')
        dated = request.args.get('date')

        return db_work.search(sub, num, tim, typ, dated)
