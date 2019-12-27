from application import create_app as create_app_base

from pymongo import MongoClient

from user.models import User
import unittest


class UserTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'flaskbook_test'
        return create_app_base(
            MONGODB_SETTINGS={"DB": self.db_name},
            TESTING=True,
            WTF_CSRF_ENABLED=False,
        )

    def setUp(self):
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client()

    def tearDown(self):
        db = MongoClient()
        db.drop_database(self.db_name)

    def test_register_user(self):
        rv = self.app.post('/register', data=dict(
            first_name="Jorge",
            last_name="Escobar",
            username="jorge",
            email="jorge@example.com",
            password="test123",
            confirm="test123"
        ), follow_redirects=True)
        assert User.objects.filter(username='jorge').count() == 1