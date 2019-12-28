from application import create_app as create_app_base

from pymongo import MongoClient

from user.models import User
import unittest
from flask import session

class UserTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'flaskbook_test'
        return create_app_base(
            MONGODB_SETTINGS={"DB": self.db_name},
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY='mySecret',
        )

    def setUp(self):
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()

    def tearDown(self):
        db = MongoClient()
        db.drop_database(self.db_name)

    def user_dict(self):
        return dict(
            first_name="Jorge",
            last_name="Escobar",
            username="jorge",
            email="jorge@example.com",
            password="test123",
            confirm="test123"
        )

    def test_register_user(self):
        rv = self.app.post('/register', data=self.user_dict(), follow_redirects=True)
        assert User.objects.filter(username='jorge').count() == 1

    def test_login_user(self):
        self.app.post('/register', data=self.user_dict())
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password'],
        ))

        with self.app as c:
            rv = c.get('/')
            assert session.get('username') == self.user_dict()['username']