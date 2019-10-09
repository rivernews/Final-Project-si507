import browser
import database
import SI507project_tools as WebScrapTools

import traceback

import flask_server
import settings as Settings

if __name__ == "__main__":
    try:
        db_manager = database.DatabaseManager()
        browser = browser.Browser(db_manager=db_manager)
        web_scrapper = WebScrapTools.WebScrapper(
            browser=browser,
            db_manager=db_manager
        )

        company_list = []
        company_list +=  web_scrapper.fetch_usc_career_fair_19_company_list()
        # company_list += web_scrapper.fetch_umich_career_fair_19_company_list()
        # company_list += web_scrapper.fetch_fortune_company_list(is_get_all=True)

        if not company_list:
            raise Exception('Empty company list')

        if Settings.SCRAP_COMPANY_AMOUNT and Settings.SCRAP_COMPANY_AMOUNT >= 0:
            web_scrapper.batch_scrap_and_store_company_data(company_list, fortune_rank_range=[1, Settings.SCRAP_COMPANY_AMOUNT])
        elif Settings.SCRAP_COMPANY_AMOUNT == None:
            # scrap as much as we can
            web_scrapper.batch_scrap_and_store_company_data(company_list, fortune_rank_range=[])
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
    finally:
        browser.close()