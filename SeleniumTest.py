import unittest
from selenium import webdriver
from app import create_app, delete_board, db, User, Board
from config import TestConfig
from wtforms import validators

localHost = "http://localhost:5000/"

class SeleniumTests(unittest.TestCase):
    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        db.create_all()

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        self.driver= webdriver.Chrome(options=options)
        self.driver.get(localHost)

        self.server_thread = multiprocessing.Process(target=self.testApp.run)
        self.server_thread.start()
        user = User(username="Bus", 
                        email="123456@i.com", 
                        password="123")
        board1 = Board(boardname="Project",
                       visibility="public", 
                       superuser=1, 
                       active=True)
        db.session.add(user)
        db.session.add(board1)
        db.session.commit()


    def tearDown(self):
        self.server_thread.terminate()
        self.driver.close()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_delete_board(self):
        board = Board.query.filter_by(boardname="Project").first()
        self.assertTrue(board.active)
        delete_board(board)
        self.assertFalse(board.active)
    
if __name__ == "__main__":
    unittest.main()