import browser
import database

import traceback

if __name__ == "__main__":
    try:
        browser = browser.Browser()
        db = database.DatabaseManager()
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
    finally:
        browser.close()