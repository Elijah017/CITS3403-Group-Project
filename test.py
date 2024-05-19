import unittest
from forms import checkPassword
from app import create_app, get_owner, check_user_permission, search_board, AddUser, db, User, Board, Permission
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
        #Users
        tableValues.append(User(username="Bus", email="123456@i.com", password="123"))
        tableValues.append(User(username="Car", email="1123ad@a.com", password="1234567890"))
        tableValues.append(User(username="Cab", email="113dfsd@a.com", password="asdjojfajiafa"))
        tableValues.append(User(username="Truck", email="11edffsd@a.com", password="asfaf143256"))
        #Boards
        tableValues.append(Board(boardname="Project", visibility="public", superuser=1, active=True))
        tableValues.append(Board(boardname="Kanban", visibility="private", superuser=2, active=True))
        #Permissions
        tableValues.append(Permission(board=1, user=2, writeAccess=1, active=1))
        tableValues.append(Permission(board=2, user=4, writeAccess=1, active=1))
        for item in tableValues:
            db.session.add(item)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #Test the correct creation of user
    def test_user_creation_and_retrieval(self):
        # Initialize User object
        user1 = User(username="test_user", email="test@example.com", password="password")
        user2 = User(username="Testuser", email="Testing@e.com", password="password")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        # Retrieve the users from the database
        retrieved_user1 = User.query.filter_by(username='test_user').first()
        retrieved_user2 = User.query.filter_by(username='Testuser').first()
        # Assert that the retrieved user is not None
        self.assertTrue(retrieved_user1 is not None)
        self.assertTrue(retrieved_user2 is not None)

        # Assert that the retrieved users has the correct username, email, and password
        self.assertEqual(retrieved_user1.username, 'test_user')
        self.assertEqual(retrieved_user1.email, 'test@example.com')
        self.assertEqual(retrieved_user1.password, 'password')

        self.assertEqual(retrieved_user2.username, 'Testuser')
        self.assertEqual(retrieved_user2.email, 'Testing@e.com')
        self.assertEqual(retrieved_user2.password, 'password')

    #Testing the correct creation of boards
    def test_board_creation_and_retrieval(self):
        #Storing information of a board
        board = Board(boardname="Test Board", visibility="Public", superuser="1", active="1")
        db.session.add(board)
        db.session.commit()

        #Retrieving existing board
        retrieved_board1 = Board.query.filter_by(boardname="Test Board").first()
        self.assertTrue(retrieved_board1 is not None)

        #Retrieving non-existing board
        retrieved_board2 = Board.query.filter_by(boardname="New board").first()
        self.assertFalse(retrieved_board2 is not None)

        #Comparing values of newly added board
        self.assertEqual(retrieved_board1.boardname, "Test Board")
        self.assertEqual(retrieved_board1.visibility, "Public")
        self.assertEqual(retrieved_board1.superuser, "1")
        self.assertEqual(retrieved_board1.active, "1")

    #Testing the functionalities of the validators
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

    # Created test for adding permissions to a user
    def test_add_permission(self):
        AddUser("2", "1", "1")
        permission = Permission.query.filter_by(board="1")
        self.assertTrue(permission, "1")

    #Check normal functioning of search board function
    def test_search_board_normal(self):
        board1 = search_board("Project")
        board2 = search_board("Kanban")
        self.assertEqual(1, board1)
        self.assertEqual(2, board2)

    #Check function of search board function when the searched board does not exist
    def test_search_board_none(self):
        board1 = search_board("new")
        board2 = search_board("Newboard")
        self.assertIsNone(board1)
        self.assertIsNone(board2)

    def test_get_permission(self):
        #Testing the ability to obtain the write access on different boards
        perm1 = check_user_permission(2, 4)
        perm2 = check_user_permission(1, 2)
        perm3 = check_user_permission(2, 1)
        perm4 = check_user_permission(1, 1)
        self.assertTrue(perm1)
        self.assertTrue(perm2)
        self.assertFalse(perm3)
        self.assertFalse(perm4)

if __name__ == "__main__":
    unittest.main()
