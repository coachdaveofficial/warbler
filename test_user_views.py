"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="user1",
                                    email="test1@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser2 = User.signup(username="user2",
                                    email="test2@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        self.user1_msg = Message(text="test message", user_id=self.testuser1.id)
        db.session.add(self.user1_msg)
        db.session.expire_on_commit=False
        db.session.commit()
        
        

    def test_list_all_users(self):
        """Test that all users appear"""
        with self.client as c:
            resp = c.get('/users')
            html = resp.get_data(as_text=True)

            self.assertTrue(resp.status_code, 200)
            self.assertIn("user1", html)
            self.assertIn("user2", html)

    def test_show_single_user(self):
        """Test that single user appears"""

        with self.client as c:
            resp = c.get(f'/users/{self.testuser1.id}')
            html = resp.get_data(as_text=True)

            self.assertTrue(resp.status_code, 200)
            self.assertIn("user1", html)
            self.assertIn("test message", html)
    
    def test_show_who_user_is_following(self):
        """Does it show who a user is following?"""

        u1_follows_u2 = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser1.id)
        db.session.add(u1_follows_u2)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get(f'/users/{self.testuser1.id}/following')
            html = resp.get_data(as_text=True)

            self.assertTrue(resp.status_code, 200)
            self.assertIn("user1", html)
            self.assertIn("user2", html)

    def test_show_who_is_following_user(self):
        """Does it show who is following a user?"""

        u1_follows_u2 = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser1.id)
        db.session.add(u1_follows_u2)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser2.id

            resp = c.get(f'/users/{self.testuser2.id}/followers')
            html = resp.get_data(as_text=True)

            self.assertTrue(resp.status_code, 200)
            self.assertIn("user1", html)
            self.assertIn("user2", html)
    def test_add_follow(self):
        """Does it allow a logged-in user to follow other users?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.post(f'/users/follow/{self.testuser2.id}')
            
            # make sure it redirects
            self.assertEqual(resp.status_code, 302)


    



            