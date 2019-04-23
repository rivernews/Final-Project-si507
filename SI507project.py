import browser
import database

import traceback

import flask_server

if __name__ == "__main__":
    try:
        flask_server.app.run()
        
    except Exception as err:
        traceback.print_tb(err.__traceback__)
        print(err)
    finally:
        # browser.BROWSER.close()
        pass