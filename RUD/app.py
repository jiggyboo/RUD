from flask import Flask
from sqlalchemy import create_engine
from flask_cors import CORS

from model import DatabaseDao, PrawDao
from service import DatabaseWork, DailyContentCache
from view import create_endpoints

class Services:
	pass

###############################################################
#					   	  Create App                          #
###############################################################

def create_app(test_config = None):
	app = Flask(__name__)

	CORS(app)
	
	if test_config is None:
		app.config.from_pyfile("config.py")
	else:
		app.config.update(test_config)

	database = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
	app.database = database

	# Persistence Layer
	db_dao = DatabaseDao(database)
	praw_dao = PrawDao()

	# Business Layer
	services = Services
	services.dc_cache = DailyContentCache(db_dao, praw_dao)
	services.db_work = DatabaseWork(db_dao, praw_dao)

	# Create Endpoints
	create_endpoints(app, services)

	return app


