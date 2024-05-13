import unittest
from forms import checkPassword
from app import create_app, db
from config import TestConfig

#Testing 
class BasicTests(unittest.TestCase):
    def setUp(self):
        testApp = create_app(TestConfig)
        self.app_context = testApp.app_context()
        self.app_context.push()
        db.create_all()
        
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_checkPassword(self):
        s = User.query.get("")
        self.assertFalse(checkPassword("1234567"))
        self.assertTrue(checkPassword("Qw12947552?"))
        
if __name__ == "__main__":
    unittest.main()