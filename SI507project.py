import browser
import database

import traceback

if __name__ == "__main__":
    try:
        db_manager = database.DatabaseManager()
        browser = browser.Browser(db_manager)
        
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
    finally:
        browser.close()