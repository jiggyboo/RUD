from flask import Flask, request, jsonify, current_app, Response, g, stream_with_context
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from functools import wraps
from flask_cors import CORS
import bcrypt
import jwt
import requests
import praw

# Set cannot be jsonified. So have to use a custom json encoder.
class CustomJSONEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, set):
			return list(obj)
		
		return JSONEncoder.default(self, obj)

# # replaced by create_app
# app = Flask(__name__)
# app.id_count = 1
# app.users = {}
# app.tweets = []
# app.json_encoder = CustomJSONEncoder # flask always has a jsonencoder

# @app.route("/ping", methods=['GET'])
# def ping():
# 	return "pong"

# @app.route("/sign-up", methods=['POST'])
# def sign_up():
# 	new_user = request.json
# 	new_user["id"] = app.id_count
# 	app.users[app.id_count] = new_user
# 	app.id_count = app.id_count + 1

# 	return jsonify(new_user)

# @app.route("/tweet", methods=['POST'])
# def tweet():
# 	payload = request.json
# 	user_id = int(payload["id"])
# 	tweet = payload["tweet"]

# 	if len(tweet) > 300:
# 		return "More than 300 words", 400

# 	if user_id not in app.users:
# 		return "No such user", 400

# 	app.tweets.append({
# 		'user_id' : user_id,
# 		'tweet' : tweet
# 	})

# 	return '', 200

# @app.route("/follow", methods=['POST'])
# def follow():
# 	payload = request.json
# 	user_id = int(payload["id"])
# 	follow_id = int(payload["follow"])

# 	if user_id not in app.users or follow_id not in app.users:
# 		return "No such user", 400

# 	user = app.users[user_id]
# 	user.setdefault('follow',set()).add(follow_id)

# 	return jsonify(user)

# @app.route("/unfollow", methods=['POST'])
# def unfollow():
# 	payload = request.json
# 	user_id = int(payload["id"])
# 	unfollow_id = int(payload["unfollow"])

# 	if user_id not in app.users or unfollow_id not in app.users:
# 		return "No such user", 400

# 	user = app.users[user_id]
# 	user.setdefault('follow',set()).discard(unfollow_id)

# 	return jsonify(user)

# # decorator takes user_id from URI with <int:user_id> and passes it as timeline argument
# @app.route("/timeline/<int:user_id>", methods=['GET'])
# def timeline(user_id):
# 	if user_id not in app.users:
# 		return "No such user", 400
	
# 	follow_list = app.users[user_id].get('follow', set())
# 	follow_list.add(user_id)
# 	timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]

# 	return jsonify({
# 		"user_id" : user_id,
# 		"timeline" : timeline
# 	})


	
def get_user(user_id):
	user = current_app.database.execute(text("""
		SELECT
			id,
			name,
			email,
			profile
		FROM users
		WHERE id = : user_id
		"""), {
			'user_id' : user_id
		}).fetchone()

	return {
		'id' : user['id'],
		'name' : user['name'],
		'email' : user['email'],
		'profile' : user['profile']
	} if user else None


def insert_user(user):
	return current_app.database.execute(text("""
		INSERT INTO users (
			name,
			email,
			profile,
			hashed_password
		) VALUES (
			:name,
			:email,
			:profile,
			:password
		)
	"""), user).lastrowid

def insert_tweet(user_tweet):
	return current_app.database.execute(text("""
		INSERT INTO tweets (
			user_id,
			tweet
		) VALUES(
			:id,
			:tweet
		)
	"""), user_tweet).rowcount

def insert_follow(user_follow):
	return current_app.database.execute(text("""
		INSERT INTO user_follow_list (
			user_id,
			follow_user_id
		) VALUES (
			:id,
			:follow
		)
	"""), user_follow).rowcount

def insert_unfollow(user_unfollow):
	return current_app.database.execute(text("""
		DELETE FROM users_follow_list
		WHERE user_id = :id
		AND follow_user_id = :unfollow
	"""), user_unfollow).rowcount

def get_timeline(user_id):
	timeline = current_app.database.execute(text("""
		SELECT
			t.user_id,
			t.tweet
		FROM tweets t
		LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
		WHERE t.user_id= :user_id
		OR t.user_id = ufl.follow_user_id
	"""), {
		'user_id' : user_id
	}).fetchall()

	return [{
		'user_id' : tweet['user_id'],
		'tweet' : tweet['tweet']
	} for tweet in timeline]

def get_user_id_and_password(email):
	row = current_app.database.execute(text("""
		SELECT
			id,
			hashed_password
		FROM users
		WHERE email =: email
	"""), {'email': email}).fetchone()

	return {
		'id' : row['id'],
		'hashed_password' : row['hashed_password']
	} if row else None

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


# using mysql with mysql connector now
def create_app(test_config = None):
	app = Flask(__name__)

	CORS(app)

	method_requests_mapping = {
		'GET': requests.get,
		'HEAD': requests.head,
		'POST': requests.post,
		'PUT': requests.put,
		'DELETE': requests.delete,
		'PATCH': requests.patch,
		'OPTIONS': requests.options,
	}

	if test_config is None:
		app.config.from_pyfile("config.py")
	else:
		app.config.update(test_config)

	database = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
	app.database = database

	app.json_encoder = CustomJSONEncoder

	@app.route("/ping", methods=['GET'])
	def ping():
		return "pong"

	@app.route('/sign-up', methods=['POST'])
	def sign_up():
		new_user = request.json
		new_user['password'] = bcrypt.hashpw(
			new_user['password'].encode('UTF-8'), bcrypt.gensalt()
		)
		new_user_id = insert_user(new_user)
		new_user_info = get_user(new_user_id)

		return jsonify(new_user_info)

	@app.route('/login', methods=['POST'])
	def login():
		credential = request.json
		email = credential['email']
		password = credential['password']

		row = database.execute(text("""
			SELECT
				id,
				hashed_password
			FROM users
			WHERE email = :email
		"""), {'email':email}).fetchone()

		if row and bcrypt.checkpw(password.encode('UTF-8'), row['hashed_password'].encode('UTF-8')):
			user_id = row['id']
			payload = {
				'user_id' : user_id,
				'exp' : datetime.utcnow() + timedelta(seconds = 60*60*24)
			}
			token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')

			return jsonify({
				'user_id' : user_id,
				'access_token' : token
				})
		
		else:
			return '', 401
	
	@app.route('/cors/<path:url>', methods=method_requests_mapping.keys())
	def purl(url):
		requests_function = method_requests_mapping[request.method]
		req = requests_function(url, stream=True, params=request.args)
		response = Response(stream_with_context(req.iter_content()),
								content_type=req.headers['content-type'],
								status=req.status_code)
		response.headers['Access-Control-Allow-Origin'] = '*'
		return response

	@app.route('/url', methods=['GET'])
	def url():
		return jsonify({'url' : 'reddit.com', 'download' : 'downloadit'})

	@app.route('/list', methods=['GET'])
	def liste():
		return jsonify({'sub': 'subname', 'urls':'["https://i.redd.it/xiwx5di1h6i71.jpg","https://i.redd.it/enjfvmtll4i71.png"]'})

	@app.route('/down', methods=['GET'])
	def down():
		file = open("urls.txt","a")
		sub = request.args.get('sub')
		num = int(request.args.get('num'))
		tim = request.args.get('tim')
		typ = request.args.get('typ')
		urls = []

		reddit = praw.Reddit(client_id='z1eHTSoHlmqgkw', \
                     client_secret='Y3g69V7w6_drdPkfiFenPWb6azh2tQ', \
                     user_agent='stkRadar', \
                     username='Great-Practice3637', \
                     password='satrhdqn19')
		subred = reddit.subreddit(sub)
		print(sub,num,typ,tim)

		topPosts = subred.top(time_filter=tim, limit=num)
		for post in topPosts:
			try:
				url = post.url
				file.write(url)
				file.write(', ')
				extens = url.split(".")[-1]
				if extens == 'jpg' or extens == 'png':
					urls.append(url)
				elif extens == 'gifv':
					urls.append(url)
				elif url.split('/')[2] == 'redgifs.com':
					try:
						r = requests.get(url)
						spl = r.text.split('/')
						num = 88
						for i in range(5):
							if spl[num+i].rfind('.mp4') != -1:
								mark = spl[num+i].split('"')[0]
						url = 'https://thumbs2.redgifs.com/'+mark
						urls.append(url)
					except:
						pass
			except:
				pass
		print(len(urls))
		file.close()
		return jsonify(urls)
	
	@app.route('/tweet', methods=['POST'])
	@login_required
	def tweet():
		new_tweet = request.json
		new_tweet['id'] = g.user_id
		tweet = new_tweet['tweet']

		if len(tweet) > 300:
			return "Over 300 letters", 400
		
		insert_tweet(new_tweet)

		return '',200

	@app.route('/follow', methods=['POST'])
	@login_required
	def follow():
		payload = request.json
		insert_follow(payload)

		return '', 200

	@app.route('/unfollow', methods=['POST'])
	@login_required
	def unfollow():
		payload = request.json
		insert_unfollow(payload)

		return '', 200
	
	@app.route('/timeline/<int:user_id>', methods=['GET'])
	@login_required
	def timeline(user_id):
		return jsonify({
			'user_id' : user_id,
			'tweet' : get_timeline(user_id)
		})	


	@app.route('/timeline',methods=['GET'])
	@login_required
	def user_timeline():
		user_id = g.user_id

		return jsonify({
			'user_id' : user_id,
			'timeline' : get_timeline(user_id)
		})

	# @app.route("/sign-up", methods=['POST'])
	# def sign_up():
	# 	new_user = request.json
	# 	new_user_id = app.database.execute(text("""
	# 		INSERT INTO users	(
	# 			name,
	# 			email,
	# 			profile,
	# 			hashed_password
	# 		)	VALUES	(
	# 			:name,
	# 			:email,
	# 			:profile,
	# 			:password
	# 		)
	# 	"""), new_user).lastrowid
		
	# 	row = app.database.execute(text("""
	# 		SELECT
	# 			id,
	# 			name,
	# 			email,
	# 			profile
	# 		FROM users
	# 		WHERE id = :user_id
	# 		"""), {
	# 			'user_id' : new_user_id
	# 		}).fetchone()

	# 	created_user = {
	# 			'id'	: row['id'],
	# 			'name'	: row['name'],
	# 			'email'	: row['email'],
	# 			'profile'	: row['profile']
	# 		} if row else None

	# 	return jsonify(created_user)

	# @app.route('/tweet', methods=['POST'])
	# def tweet():
	# 	user_tweet = request.json
	# 	tweet = user_tweet['tweet']

	# 	if len(tweet) > 300:
	# 		return 'Length over 300', 400
		
	# 	app.database.execute(text("""
	# 		INSERT INTO tweets (
	# 			user_id,
	# 			tweet
	# 		) VALUES (
	# 			:id,
	# 			:tweet
	# 		)
	# 	"""), user_tweet)

	# 	return '', 200

	# @app.route('/timeline/<int:user_id>', methods=['GET'])
	# def timeline(user_id):
	# 	rows = app.database.execute(text("""
	# 		SELECT
	# 			t.user_id,
	# 			t.tweet
	# 		FROM tweets t
	# 		LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
	# 		WHERE t.user_id = :user_id
	# 		OR t.user_id = ufl.follow_user_id
	# 	"""), {
	# 		'user_id' : user_id
	# 	}).fetchall()

	# 	timeline = [{
	# 		'user_id' : row['user_id'],
	# 		'tweet' : row['tweet']
	# 	} for row in rows]

	# 	return jsonify({
	# 		'user_id' : user_id,
	# 		'timeline' : timeline
	# 	})

	return app


