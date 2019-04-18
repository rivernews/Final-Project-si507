import unittest

from SI507project_tools import WebScrapper
import browser as BrowserUtil
import database as DatabaseUtil

class TestCases(unittest.TestCase):

    def setUp(self):
        self.browser = BrowserUtil.Browser()
        self.db_manager = DatabaseUtil.DatabaseManager()
        return super().setUp()
    
    def tearDown(self):
        self.browser.close()
        return super().tearDown()

    def test_scrap_company_list(self):
        
        scrapper = WebScrapper(browser=self.browser, db=self.db_manager)
        scrapper.fetch_fortune_company_list()

        self.assertEqual(
            scrapper.company_list[0].lower(),
            'walmart'
        )
    
    def test_scrap_company_rating(self):
        scrapper = WebScrapper(browser=self.browser, db=self.db_manager)
        scrapper.fetch_fortune_company_list()

        self.assertEqual(
            scrapper.get_company_rating(scrapper.company_list[0]),
            3.2
        )

    

if __name__ == "__main__":
    unittest.main()