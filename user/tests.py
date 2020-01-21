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
            first_name="Yuxin",
            last_name="Zhao",
            username="zhaoyuxin",
            email="zhaoyuxin95@gmail.com",
            password="zhao",
            confirm="zhao"
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

        #confirm the user
        user = User.objects.get(username=self.user_dict()["username"])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert "Your email has been confirmed" in str(rv.data)

        # try again to confirm
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert rv.status_code == 404

        # check change configuration is empty
        user = User.objects.get(username=self.user_dict()['username'])
        assert user.change_configuration == {}

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

        #confirm the user
        user = User.objects.get(username=self.user_dict()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)

        #user login
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']
        ))


        #edit fields
        user = self.user_dict()
        user['first_name'] = "Test First"
        user['last_name'] = "Test Last"
        user['username'] = "TestUsername"
        #user['email'] = "Test@Example.com"

        # edit the user
        rv = self.app.post('/edit', data=user)
        assert "Profile updated" in str(rv.data)
        edited_user = User.objects.first()
        assert edited_user.first_name == "Test First"
        assert edited_user.last_name == "Test Last"
        assert edited_user.username == "testusername"
        # assert edited_user.email == "test@example.com"

        # check new email update
        user['email'] = 'test@example.com'
        rv = self.app.post('/edit', data=user)
        assert 'You will need to confirm the new email to complete this change'
        db_user = User.objects.first()
        code = db_user.change_configuration.get('confirmation_code')
        new_email = db_user.change_configuration.get('new_email')
        assert new_email == user['email']

        # confirm the change of the email
        rv = self.app.get('/confirm/' + db_user.username + '/' + code)
        db_user = User.objects.first()
        assert db_user.email == user['email']
        assert db_user.change_configuration == {}

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

    def test_get_profile(self):
        # create a user
        self.app.post('/register', data=self.user_dict())

        # get the user's profile
        rv = self.app.get('/' + self.user_dict()['username'])
        assert self.user_dict()['username'] in str(rv.data)

        # get 404
        rv = self.app.get('/noexist')
        assert rv.status_code == 404


    def test_forgot_password(self):
        # create a user
        self.app.post('/register', data=self.user_dict())

        # confirm the user
        user = User.objects.get(username=self.user_dict()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)

        # enter user forgot email
        rv = self.app.post('/forgot', data=dict(email=self.user_dict().get('email')))
        user = User.objects.first()
        password_reset_code = user.change_configuration.get('password_reset_code')
        assert password_reset_code is not None

        # try wrong username
        rv = self.app.get('/password_reset/not_there/' + password_reset_code)
        assert rv.status_code == 404

        # do right password reset code
        rv = self.app.post('/password_reset/' + self.user_dict().get('username') + "/" + password_reset_code, data=dict(password='newpassword', confirm='newpassword'), follow_redirects=True)
        assert "Your password has been updated" in str(rv.data)
        user = User.objects.first()
        assert user.change_configuration == {}

        # try logging in with new password
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password='newpassword',
        ))

        # check if the session is set
        with self.app as c:
            rv = c.get('/')
            assert session.get('username') == self.user_dict()['username']