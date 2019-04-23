import unittest

from SI507project_tools import WebScrapper
import browser as BrowserUtil
import database as DatabaseUtil

class TestCases(unittest.TestCase):

    def setUp(self):
        self.db_manager = DatabaseUtil.DatabaseManager()
        self.browser = BrowserUtil.Browser(db_manager=self.db_manager)
        return super().setUp()
    
    def tearDown(self):
        self.browser.close()
        return super().tearDown()

    def test_scrap_company_list(self):
        self.scrapper = WebScrapper(browser=self.browser, db_manager=self.db_manager)
        self.scrapper.fetch_fortune_company_list()
        self.assertEqual(
            self.scrapper.company_list[0].lower(),
            'walmart'
        )
    
    def test_scrap_company_rating(self):
        self.scrapper = WebScrapper(browser=self.browser, db_manager=self.db_manager)
        self.scrapper.fetch_fortune_company_list()

        self.assertEqual(
            self.scrapper.get_company_rating(self.scrapper.company_list[0]),
            3.2
        )
    
    def test_company_data_store(self, fortune_rank=1):
        self.scrapper = WebScrapper(browser=self.browser, db_manager=self.db_manager)
        self.scrapper.fetch_fortune_company_list()
        
        company_name = self.scrapper.company_list[fortune_rank - 1]

        rating = self.scrapper.get_company_rating(company_name)

        company_id = self.scrapper.create_or_update_company({
            'name': company_name,
            'companyratings': [
                {
                    'source': 'glassdoor',
                    'value': rating
                },
                {
                    'source': 'fortune 500',
                    'value': fortune_rank
                }
            ]
        })

        # Test company
        result_list = self.db_manager.filter(DatabaseUtil.Tables.COMPANY.value, {
            'id': company_id
        })

        self.assertEqual(len(result_list), 1, msg='TEST FAILURE: company created but result in database is not correct.')
        
        stored_company = result_list[0]
        self.assertEqual(stored_company[1], company_name)

        # Test company rating
        result_list = self.db_manager.filter(DatabaseUtil.Tables.COMPANY_RATING.value, {
            'companyId': company_id
        })

        for result in result_list:
            if result[2] == 'glassdoor':
                self.assertEqual(result[1], rating, msg='TEST FAILURE: stored company rating value not correct.')
            elif result[2] == 'fortune 500':
                self.assertEqual(result[1], fortune_rank, msg='TEST FAILURE: stored fortune rank value not correct.')

    def test_multi_company_data_store(self):
        for fortune_rank in range(1, 11):
            self.test_company_data_store(fortune_rank=fortune_rank)
    
if __name__ == "__main__":
    unittest.main()