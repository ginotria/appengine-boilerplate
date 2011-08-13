# -*- coding: utf-8 -*-
import logging

from hashlib import md5

from google.appengine.ext import db
from google.appengine.api import users


class UserPrefs(db.Model):
    """UserPrefs stores properties related to a specific user.

    All models with user relations should refer to the specific UserPrefs
    model, not the Google internal user model.
    """
    nickname = db.StringProperty()
    email = db.StringProperty(default="")

    # The md5 has of the email is used for gravatar image urls
    email_md5 = db.StringProperty(default="")

    # The main reference to the Google-internal user object
    federated_identity = db.StringProperty()
    federated_provider = db.StringProperty()

    # Google user id is only used on the dev server
    google_user_id = db.StringProperty()

    # Various meta information
    date_joined = db.DateTimeProperty(auto_now_add=True)
    date_lastlogin = db.DateTimeProperty(auto_now_add=True)  # TODO
    date_lastactivity = db.DateTimeProperty(auto_now_add=True)  # TODO

    @staticmethod
    def from_user(user):
        if not user:
            return None

        if user.federated_identity():
            # Standard OpenID user object
            q = db.GqlQuery("SELECT * FROM UserPrefs WHERE \
                federated_identity = :1 AND federated_provider = :2", \
                user.federated_identity(), user.federated_provider())

        else:
            # On local devserver there is only the google user object
            logging.warning("_ user has no fed id [%s]" % user)
            q = db.GqlQuery("SELECT * FROM UserPrefs WHERE \
                google_user_id = :1", user.user_id())

        # Try to get the UserPrefs from the data store
        prefs = q.get()

        # If not existing, create now
        if not prefs:
            nick = user.nickname()
            if user.email():
                if not nick or "http://" in nick:
                    # If user has email and openid-url is nickname, replace
                    nick = user.email()

            # Create new user preference entity
            logging.info("_ create new userprefs: %s" % nick)
            prefs = UserPrefs(nickname=nick,
                    email=user.email(),
                    email_md5=md5(user.email().strip().lower()).hexdigest(),
                    federated_identity=user.federated_identity(),
                    federated_provider=user.federated_provider(),
                    google_user_id=user.user_id())

            # Save the newly created UserPrefs
            prefs.put()

        # Return either found or just created user preferences
        return prefs


class YourCustomModel(db.Model):
    userprefs = db.ReferenceProperty(UserPrefs)

    demo_string_property = db.StringProperty()
    demo_boolean_property = db.BooleanProperty(default=True)
    demo_integer_property = db.IntegerProperty(default=1)
    demo_datetime_property = db.DateTimeProperty(auto_now_add=True)
