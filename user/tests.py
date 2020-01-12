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
        assert User.objects.filter(username=self.user_dict()['username']).count() == 1
        # Invalid Username characters
        user2 = self.user_dict()
        user2['username'] = 'test test'
        user2['email'] = 'test@example.com'
        rv = self.app.post('/register', data=user2, follow_redirects=True)
        assert 'Invalid User' in str(rv.data)

        # Test whether username is saved in lowercase
        user3 = self.user_dict()
        user3['username'] = 'TestUser'
        user3['email'] = "test3@example.com"
        rv = self.app.post('/register', data=user3, follow_redirects=True)
        assert User.objects.filter(username=user3['username'].lower()).count() == 1

    def test_login_user(self):
        self.app.post('/register', data=self.user_dict())
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password'],
        ))

        with self.app as c:
            rv = c.get('/')
            assert session.get('username') == self.user_dict()['username']

    def test_edit_porfile(self):
        # create user
        self.app.post('/register', data=self.user_dict())

        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']

        ))
        rv = self.app.get('/' + self.user_dict()['username'])
        assert 'Edit Profile' in str(rv.data)

        #edit fields
        user = self.user_dict()
        user['first_name'] = "Test First"
        user['last_name'] = "Test Last"
        user['username'] = "TestUsername"
        user['email'] = "Test@Example.com"

        # edit the user
        rv = self.app.post('/edit', data=user)
        assert "Profile updated" in str(rv.data)
        edited_user = User.objects.first()
        assert edited_user.first_name == "Test First"
        assert edited_user.last_name == "Test Last"
        assert edited_user.username == "testusername"
        assert edited_user.email == "test@example.com"

        # create a second user
        self.app.post('/register', data=self.user_dict())
        # login the user
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']
        ))

        # try to save same email
        user = self.user_dict()
        user['email'] = "test@example.com"
        rv = self.app.post('/edit', data=user)
        assert "Email already exists" in str(rv.data)

        # try to save same username
        user = self.user_dict()
        user['username'] = "TestUsername"
        rv = self.app.post('/edit', data=user)
        assert "Username already exists" in str(rv.data)