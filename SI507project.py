import browser
import database
import SI507project_tools as WebScrapTools

import traceback

import flask_server

if __name__ == "__main__":
    try:
        db_manager = database.DatabaseManager()
        browser = browser.Browser(db_manager=db_manager)
        web_scrapper = WebScrapTools.WebScrapper(
            browser=browser,
            db_manager=db_manager
        )

        web_scrapper.fetch_fortune_company_list(is_get_all=True)

        web_scrapper.batch_scrap_and_store_company_data([1, 500])
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
    finally:
        browser.close()