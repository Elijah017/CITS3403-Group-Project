import unittest
from forms import checkPassword
from app import create_app, get_owner, delete_board, db, User, Board
from config import TestConfig
from wtforms import validators

class Password:
    def __init__(self, data):
        self.data = data

# Testing
class BasicTests(unittest.TestCase):
    def setUp(self):
        testApp = create_app(TestConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()
        user1 = User(username="Bus", 
                        email="123456@i.com", 
                        password="123")
        user2 = User(username="Car", 
                        email="1123ad@a.com", 
                        password="1234567890")
        user3 = User(username="Cab", 
                        email="113dfsd@a.com", 
                        password="asdjojfajiafa")
        user4 = User(username="Truck", 
                        email="11edffsd@a.com", 
                        password="asfaf143256")
        board = Board(boardname="Project",
                       visibility="public", 
                       superuser=1, 
                       active=True)
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.add(user4)
        db.session.add(board)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_checkPassword(self):
        p1 = Password(User.query.filter_by(username="Bus").first().password)
        p2 = Password(User.query.filter_by(username="Car").first().password)
        p3 = Password(User.query.filter_by(username="Cab").first().password)
        p4 = Password(User.query.filter_by(username="Truck").first().password)
        with self.assertRaises(validators.ValidationError) as context:
            checkPassword(p1)
        self.assertEqual(context.exception.args[0], "Password length should be more than 10 characters")
        with self.assertRaises(validators.ValidationError) as context:
            checkPassword(p2)
        self.assertEqual(context.exception.args[0], "Password must contain at least one lowercase letter")
        with self.assertRaises(validators.ValidationError) as context:
            checkPassword(p3)
        self.assertEqual(context.exception.args[0], "Password must contain at least one digit")
        with self.assertRaises(validators.ValidationError) as context:
            checkPassword(p4)
        self.assertEqual(context.exception.args[0], "Password must contain at least one uppercase letter")

    def test_get_owner(self):
        self.assertEqual(get_owner("1", 1), "Me")
        self.assertEqual(get_owner("1", 2), "Bus")        
        self.assertEqual(get_owner("4", 2), "Truck")   
        self.assertEqual(get_owner("3", 4), "Cab")

    def test_delete_board(self):
        #Active stored as '1' and non-ative stored as '0'
        board = Board.query.filter_by(boardname="Project").first()
        self.assertEqual(board.active, '1')
        delete_board(board.id)
        self.assertEqual(board.active, '0')

if __name__ == "__main__":
    unittest.main()
