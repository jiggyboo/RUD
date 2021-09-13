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
from praw_info import prawInfo

# Set cannot be jsonified. So have to use a custom json encoder.
class CustomJSONEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, set):
			return list(obj)
		
		return JSONEncoder.default(self, obj)

###############################################################
#                            MYSQL                            #
###############################################################

def getT_url(url):
	rurl = current_app.database.execute(text("""
		SELECT
			id
			urls
		FROM urls
		WHERE sub = : sub_name AND type = : url_type AND date = : url_date AND TIME = : url_dur
		"""), {
			'sub_name' : url['sub'],
			'url_type' : url['stype'],
			'url_date' : url['sdate'],
			'url_dur' : url['sdur']
		}).fetchone()

	return {
		'id' : rurl['id'],
		'sub' : url['sub'],
		'urls' : rurl['urls']
	} if rurl else None

def get_url(url):
	rurl = current_app.database.execute(text("""
		SELECT
			id
			urls
		FROM urls
		WHERE sub = : sub_name AND type = : url_type AND date = : url_date
		"""), {
			'sub_name' : url['sub'],
			'url_type' : url['stype'],
			'url_date' : url['sdate']
		}).fetchone()

	return {
		'id' : rurl['id'],
		'sub' : url['sub'],
		'urls' : rurl['urls']
	} if rurl else None

def get_sub(sub):
	subn = current_app.database.execute(text("""
	SELECT 
		sub
	FROM subs
	WHERE sub = : sub_name
	"""), sub).fetchone()
	return subn

def insert_url(url):
	return current_app.database.execute(text("""
		INSERT INTO urls (
			urls,
			type,
			time,
			nump,
			sub
		) VALUES (
			:urls,
			:type,
			:time,
			:nump,
			:sub
		)
	"""), url).lastrowid

def insert_sub(sub):
	return current_app.database.execute(text("""
		INSERT INTO subs (
			sub,
			nsfw
		) VALUES (
			:sub,
			:nsfw
		)
	"""), sub).lastrowid

def increment_hits_sub(subname):
	current_app.database.execute(text("""
	UPDATE subs
		SET hits = hits + 1
		WHERE sub = : subname
	"""), {
		'subname' : subname
	})

def increment_hits_url(id):
	current_app.database.execute(text("""
	UPDATE urls
	SET hits = hits + 1
	WHERE id = : sub_id
	"""), {
		'sub_id' : id
	})

## Searches Reddit using PRAW, returns urls of downloadable contents of each items in the sub.
def search_sub(sub,tim,num,type):
	urls = []
	reddit = praw.Reddit(client_id=prawInfo['client_id'], \
                     client_secret=prawInfo['client_secret'], \
                     user_agent=prawInfo['user_agent'], \
                     username=prawInfo['username'], \
                     password=prawInfo['password'])
	subred = reddit.subreddit(sub)
	if type == 'top':
		posts = subred.top(time_filter=tim, limit=num)
	elif type == 'new':
		posts = subred.new(limit = num)
	elif type == 'hot':
		posts = subred.hot(limit = num)
	for post in posts:
		try:
			url = post.url
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
			print("failed")
			pass
	return urls

## Given the URL of Cyberdrop post, returns downloadable urls of each items in the gallery.
def downloadCD(url):
    r = requests.get(url).text
    urls = []
    pics = r.split('downloadUrl: "')
    for durl in pics[1:]:
        urls.append(durl.split('",\n')[0])
    vids = r.split('mp4" data-html')
    for vurl in vids[1:]:
        vvurl = vurl.split('href="')[1]
        url = vvurl.split('" target=')[0]
        urls.append(url)
    print(len(urls))

    return jsonify({'urls':urls})

def is_18(sub):
	reddit = praw.Reddit(client_id=prawInfo['client_id'], \
                     client_secret=prawInfo['client_secret'], \
                     user_agent=prawInfo['user_agent'], \
                     username=prawInfo['username'], \
                     password=prawInfo['password'])
	subred = reddit.subreddit(sub)
	return subred.over18


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

	@app.route("/api/ping", methods=['GET'])
	def ping():
		return "pong"

	@app.route('/api/search', methods=['GET'])
	def search():
		sub = request.args.get('sub')
		num = int(request.args.get('num'))
		tim = request.args.get('tim')
		typ = request.args.get('typ')
		dur = request.args.get('dur')
		if dur != '':
			url = get_url({''})
		else:
			url = getT_url({''})
		if url == None:
			if get_sub(sub) == None:
				insert_sub(jsonify({'sub':sub,'nsfw':int(is_18(sub))}))
			rurl = search_sub(sub, tim, num, typ)
			insert_url(jsonify({'urls':rurl,'type':typ,'time':tim,'nump':num,'sub':sub}))
		else:
			rurl = url
			increment_hits_sub(sub)
			increment_hits_url(rurl['id'])

		return jsonify({'url':rurl['urls']})

	@app.route('/api/cors/<path:url>', methods=method_requests_mapping.keys())
	def purl(url):
		requests_function = method_requests_mapping[request.method]
		req = requests_function(url, stream=True, params=request.args)
		response = Response(stream_with_context(req.iter_content()),
								content_type=req.headers['content-type'],
								status=req.status_code)
		response.headers['Access-Control-Allow-Origin'] = '*'
		return response

	@app.route('/api/url', methods=['GET'])
	def url():
		return jsonify({'url' : 'reddit.com', 'download' : 'downloadit'})

	@app.route('/api/list', methods=['GET'])
	def liste():
		return jsonify({'sub': 'subname', 'urls':'["https://i.redd.it/xiwx5di1h6i71.jpg","https://i.redd.it/enjfvmtll4i71.png"]'})

	@app.route('/api/down', methods=['GET'])
	def down():
		sub = request.args.get('sub')
		num = int(request.args.get('num'))
		tim = request.args.get('tim')
		typ = request.args.get('typ')
		urls = []

		reddit = praw.Reddit(client_id=prawInfo['client_id'], \
			client_secret=prawInfo['client_secret'], \
			user_agent=prawInfo['user_agent'], \
			username=prawInfo['username'], \
			password=prawInfo['password'])
		subred = reddit.subreddit(sub)
		print(sub,num,typ,tim)

		topPosts = subred.top(time_filter=tim, limit=num)
		for post in topPosts:
			try:
				url = post.url
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
		return jsonify(urls)

	return app


