from mongoengine import signals
from application import db
from utilities.common import utc_now_ts as now
from flask import url_for
from settings import STATIC_IMAGE_URL

import os


class User(db.Document):
    username = db.StringField(db_field="u", required=True, unique=True)
    password = db.StringField(db_field="p", required=True)
    email = db.StringField(db_field="e", required=True, unique=True)
    first_name = db.StringField(db_field="fn", max_length=50)
    last_name = db.StringField(db_field="ln", max_length=50)
    created = db.IntField()
    bio = db.StringField(db_field="b", max_length=160)
    email_confirmed = db.BooleanField(db_field='ecf', default=False)
    change_configuration = db.DictField(db_field='cc')
    profile_image = db.StringField(db_field='i', default=None)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        document.username = document.username.lower()
        document.email = document.email.lower()

    def profile_imgsrc(self, size):
        return os.path.join(STATIC_IMAGE_URL, 'user', "%s.%s.%s.png" % (self.id, self.profile_image, size))

    meta = {
        'indexes': ["username", "email", "-created"]
    }

signals.pre_save.connect(User.pre_save, sender=User)