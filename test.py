import unittest
from forms import checkPassword
from app import create_app, get_owner, delete_board, AddUser, db, User, Board, Permission
from config import TestConfig
from wtforms import validators


class Password:
    def __init__(self, data):
        self.data = data


# Testing
class BasicTests(unittest.TestCase):
    def setUp(self):
        tableValues = []
        testApp = create_app(TestConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        self.client = testApp.test_client()
        db.create_all()
        # Testing values in database
        tableValues.append(User(username="Bus", email="123456@i.com", password="123"))
        tableValues.append(User(username="Car", email="1123ad@a.com", password="1234567890"))
        tableValues.append(User(username="Cab", email="113dfsd@a.com", password="asdjojfajiafa"))
        tableValues.append(User(username="Truck", email="11edffsd@a.com", password="asfaf143256"))
        tableValues.append(Board(boardname="Project", visibility="public", superuser=1, active=True))
        for item in tableValues:
            db.session.add(item)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_checkPassword(self):
        p1 = Password("123")
        p2 = Password("1234567890")
        p3 = Password("asdjojfajiafa")
        p4 = Password("asfaf143256")
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

    # Test correct functionality of get_owner function
    def test_get_owner(self):
        self.assertEqual(get_owner("1", 1), "Me")
        self.assertEqual(get_owner("1", 2), "Bus")
        self.assertEqual(get_owner("4", 2), "Truck")
        self.assertEqual(get_owner("3", 4), "Cab")

    # Retrieve none when the user ID does not exist in the database
    def test_get_username_not_exists(self):
        self.assertIsNone(get_owner("5", 1))
        self.assertIsNone(get_owner("9", 3))
        self.assertIsNone(get_owner("6", 4))
        self.assertIsNone(get_owner("7", 2))

    # Test the proper functioning of delete board function
    def test_delete_board(self):
        # Active stored as '1' and non-ative stored as '0'
        board = Board.query.filter_by(boardname="Project").first()
        self.assertEqual(board.active, "1")
        delete_board(board.id)
        self.assertEqual(board.active, "0")

    # Created test for adding permissions to a user
    def test_add_permission(self):
        AddUser("2", "1", "1")
        permission = Permission.query.filter_by(board="1")
        self.assertTrue(permission, "1")
        AddUser("2", "1", "0")

    # Have 5 tests currently


if __name__ == "__main__":
    unittest.main()
