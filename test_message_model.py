"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, datetime

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
    def tearDown(self):
        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        db.session.commit()

    def test_user_model(self):
        """Does the Message model function?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages
        self.assertEqual(len(u.messages), 0)

        msg = Message(text="Hello World", user_id=u.id)

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(u.messages), 1)
        self.assertEqual(u.messages[0].text, "Hello World")

    def test_delete_on_cascade(self):
        """Does msg get deleted when User is deleted?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(Message.query.count(), 0)

        msg = Message(text="Hello World", user_id=u.id)

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(Message.query.count(), 1)


        # unsure why this isn't working?
        db.session.delete(u)
        db.session.commit()

        self.assertEqual(Message.query.count(), 0)

    def test_add_msg_when_user_non_existent(self):
        """Can you add a message for a non-existent user?"""

        self.assertEqual(Message.query.count(), 0)

        try:
            msg = Message(text="Hello World", user_id=9999)
            db.session.add(msg)
            db.session.commit()
        except:
            db.session.rollback()
            self.assertEqual(Message.query.count(), 0)





        

