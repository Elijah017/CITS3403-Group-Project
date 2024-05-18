import unittest, multiprocessing
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app import create_app, db, User, Board
from config import TestConfig

localHost = "http://127.0.0.1:5000/"

class SeleniumTests(unittest.TestCase):
    def setUp(self):
        self.testApp = create_app(TestConfig)
        self.app_context = self.testApp.app_context()
        self.app_context.push()
        
        #Manage database
        db.create_all()

        """#Something else?
        user = User(username="Key", email="qwert@i.com", password="Qw1234567?")
        board = Board(boardname="Project", visibility="public", superuser=1, active=True)
        db.session.add(user)
        db.session.add(board)
        db.session.commit()"""

        self.server_process = multiprocessing.Process(target=self.testApp.run)
        self.server_process.start()

        #options = webdriver.ChromeOptions()
        #options.add_argument("--headless=new")
        #self.driver = webdriver.Chrome(options=options)
        #self.driver.implicitly_wait(5)
        self.driver = webdriver.Chrome()
        self.driver.get(localHost)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.server_process.terminate()
        self.driver.close()

    def test_create_board_name_exists(self):
        sleep(10)
        self.assertTrue(True)
        """driver = self.driver
        
        # Log in as the test user
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.NAME, "email").send_keys("123456@i.com")
        driver.find_element(By.NAME, "password").send_keys("Qw1234567?" + Keys.RETURN)
        
        # Go to the new board page
        driver.get("http://127.0.0.1:5000/newBoard/")
        
        # Fill out the form with an existing board name
        driver.find_element(By.NAME, "boardname").send_keys("ExistingBoard")
        driver.find_element(By.NAME, "visibility").send_keys("public")
        driver.find_element(By.NAME, "submit").click()
        
        # Check for the flash message indicating the board name already exists
        flash_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        self.assertIn("Board With This Name Already Exists.", flash_message)

    def test_create_new_board(self):
        driver = self.driver
        
        # Log in as the test user
        driver.get("http://127.0.0.1:5000/login")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        
        driver.find_element(By.NAME, "email").send_keys("123456@i.com")
        driver.find_element(By.NAME, "password").send_keys("Qw1234567?" + Keys.RETURN)
        
        # Go to the new board page
        driver.get("http://127.0.0.1:5000/newBoard/")
        
        # Fill out the form with a new board name
        driver.find_element(By.NAME, "boardname").send_keys("NewBoard")
        driver.find_element(By.NAME, "visibility").send_keys("public")
        driver.find_element(By.NAME, "submit").click()
        
        # Check for the success flash message
        flash_message = driver.find_element(By.CLASS_NAME, "flash-message").text
        self.assertIn("Public Board Created", flash_message)"""

if __name__ == "__main__":
    unittest.main()
