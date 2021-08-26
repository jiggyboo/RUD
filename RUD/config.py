db = {
    'user'  : 'root',
    'password'  : 'satrhdqn19',
    'host'  : 'rud-db.cejatgjktly2.ap-northeast-2.rds.amazonaws.com',
    'port'  : 3306,
    'database' : 'RUD'
}

DB_URL = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
JWT_SECRET_KEY = 'password'
