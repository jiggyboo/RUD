import pytest
import bcrypt
import json
import config

from app import create_app
from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding='utf-8',max_overflow=0)

@pytest.fixture
def api():
    app = create_app(config.test_config)
    app.config['TESTING'] = True
    return app.test_client()

def setup_function():
    ## Create a new database for testing

    ## Create a new user
    hashed_password = bcrypt.hashpw(
        b"test password",
        bcrypt.gensalt()
    )
    new_users = [
        {
            'id': 1,
            'name': 'test user1',
            'email': 'testemail1@email.com',
            'password': hashed_password
        },
        {
            'id': 2,
            'name': 'test user2',
            'email': 'testemail2@email.com',
            'password': hashed_password
        }
    ]
    database.execute(text("""
        INSERT INTO users (id, name, email, password)
        VALUES (:id, :name, :email, :password)
        """), new_users)

    ## Create a new stock info

    pass

def teardown_function():
    ## Delete the database
    database.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    database.execute(text("TRUNCATE TABLE users"))
    database.execute(text("TRUNCATE TABLE stocks"))
    database.execute(text("TRUNCATE TABLE following_ticker"))
    database.execute(text("TRUNCATE TABLE ticker_follow"))
    database.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

def test_login(api):
    ## Test login
    response = api.post('/api/login', json={
        'email': 'testemail1@email.com',
        'password': 'test password'
    })
    assert b"access_token" in response.data

    ## Test login with wrong password
    response = api.post('/api/login', json={
        'email': 'testemail1@email.com',
        'password': 'wrong password'
    })
    assert b"access_token" not in response.data

    ## Test login with wrong email
    response = api.post('/api/login', json={
        'email': 'wrongemail@email.com',
        'password': 'test password'
    })
    assert b"access_token" not in response.data

def test_register(api):
    ## Test register
    response = api.post('/api/register', json={
        'name': 'test user3',
        'email': 'testemail3@email.com',
        'password': 'test password'
    })
    assert response.status_code == 200

    ## Test register with existing email
    response = api.post('/api/register', json={
        'name': 'test user1',
        'email': 'testemail1@email.com',
        'password': 'test password'
    })
    assert response.status_code == 400