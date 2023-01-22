"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, bcrypt

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
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_user_repr(self):
        """Does __repr__ work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        self.assertIn(str(u.id), str(u.__repr__))
        self.assertIn(u.username, str(u.__repr__))
        self.assertIn(u.email, str(u.__repr__))

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        
        
        user1 = User(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD"
        )
        user2 = User(
            email="user2@test.com",
            username="user2",
            password="HASHED_PASSWORD"
        )       

        db.session.add_all([user1, user2])
        db.session.commit()
        user1_follow_user2 = Follows(user_being_followed_id=user2.id, user_following_id=user1.id)
        db.session.add(user1_follow_user2)
        db.session.commit()

        self.assertEqual(user1.is_following(user2), True)

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is NOT following user2?"""
        
        
        user1 = User(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD"
        )
        user2 = User(
            email="user2@test.com",
            username="user2",
            password="HASHED_PASSWORD"
        )       

        db.session.add_all([user1, user2])
        db.session.commit()


        self.assertEqual(user1.is_following(user2), False)

    def test_is_followed_by(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""        
        
        user1 = User(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD"
        )
        user2 = User(
            email="user2@test.com",
            username="user2",
            password="HASHED_PASSWORD"
        )       

        db.session.add_all([user1, user2])
        db.session.commit()
        user2_follow_user1 = Follows(user_being_followed_id=user1.id, user_following_id=user2.id)
        db.session.add(user2_follow_user1)
        db.session.commit()


        self.assertEqual(user1.is_followed_by(user2), True)

    def test_is_not_followed_by(self):
        """Does is_followed_by successfully detect when user1 is NOT followed by user2?"""        
        
        user1 = User(
            email="user1@test.com",
            username="user1",
            password="HASHED_PASSWORD"
        )
        user2 = User(
            email="user2@test.com",
            username="user2",
            password="HASHED_PASSWORD"
        )       

        db.session.add_all([user1, user2])
        db.session.commit()



        self.assertEqual(user1.is_followed_by(user2), False)

    def test_user_signup(self):
        """Does User.signup successfully create a new user given valid credentials?"""

        self.assertEqual(User.query.count(), 0)

        user = User.signup(
            email="test@test.com",
            username="testuser",
            password="NOT_HASHED_PASSWORD",
            image_url="stockphoto.com"
        )
        db.session.commit()
        
        self.assertNotEqual(user.password, "NOT_HASHED_PASSWORD")
        self.assertEqual(user.username, "testuser")
        self.assertIsInstance(user, User)
        self.assertEqual(User.query.count(), 1)

    def test_bad_user_signup(self):
        """Does User.signup fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""
        self.assertEqual(User.query.count(), 0)
        try:
            user = User.signup(
            username=None,
            email="",
            password="NOT_HASHED_PASSWORD",
            image_url=""
            )
            db.session.commit()
        except:
            db.session.rollback()
            self.assertEqual(User.query.count(), 0)
        try:
            user = User.signup(
            username="testing",
            email=None,
            password="NOT_HASHED_PASSWORD",
            image_url=""
            )
            db.session.commit()
        except:
            db.session.rollback()
            self.assertEqual(User.query.count(), 0)
        
    def test_user_authenticate_success(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        password = "testpw"
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user1 =  User(
                email="test@test.com",
                username="testuser",
                password=hashed_pwd
            )
        db.session.add(user1)
        db.session.commit()
        self.assertEqual(User.authenticate("testuser", "testpw"), user1)
    
    def test_user_authenticate_bad_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
        password = "testpw"
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user1 =  User(
                email="test@test.com",
                username="testuser",
                password=hashed_pwd
            )
        db.session.add(user1)
        db.session.commit()
        self.assertFalse(User.authenticate("baduser", "testpw"), user1)

    def test_user_authenticate_bad_username(self):
        """Does User.authenticate fail to return a user when the password is invalid?"""
        password = "testpw"
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        user1 =  User(
                email="test@test.com",
                username="testuser",
                password=hashed_pwd
            )
        db.session.add(user1)
        db.session.commit()
        self.assertFalse(User.authenticate("testuser", "badpw"), user1)
    

        



   


       


        