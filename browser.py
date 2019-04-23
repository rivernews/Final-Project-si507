from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException
)
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from pathlib import Path

import codecs
import re

import database

"""
    How to scrap a page?

    1. get browser object <----
    2. request web page
    3. wait till page load finished or an element shows up or till timeout
    (3. execute javascript piece if needed): browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    4. browser.find_elements_by_class_name('...')
    5. access element's attribute value
    6. store value data in python data structure
    7. cache save value
"""

class Browser:
    
    def __init__(self, db_manager, *args, **kwargs):
        self.browser = self.get_browser()
        self.db_manager = db_manager
        return super().__init__(*args, **kwargs)
    
    def get_browser(self):
        PROJECT_ROOT_DIRECTORY  = Path(__file__).parent

        options = Options()
        options.add_experimental_option(
            "prefs", {
                "download.default_directory": str(PROJECT_ROOT_DIRECTORY / 'data'),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
        )
        options.add_argument("--incognito")
        options.add_argument("--headless")

        # https://stackoverflow.com/questions/44770796/how-to-make-selenium-not-wait-till-full-page-load-which-has-a-slow-script/44771628
        
        browser = webdriver.Chrome(
            executable_path=(PROJECT_ROOT_DIRECTORY / 'chromedriver').resolve(),
            options=options,
        )

        return browser
    
    def request_page(self,
            page_url="http://fortune.com/fortune500/list/",
            timeout=10,
            page_name=''
        ):
        try:
            print("INFO: browser getting the page...")
            
            cache_lookup_result_list = self.db_manager.filter(database.Tables.WEBPAGE_CACHE.value, {
                'url': page_url
            })
            cache_file_path = None
            if len(cache_lookup_result_list) > 0:
                print("Cache found =", cache_lookup_result_list[0][2])
                cache_file_path = Path(cache_lookup_result_list[0][2])

            if cache_file_path and cache_file_path.exists():
                self.browser.get(f'file://{cache_file_path.absolute()}')
            else:
                print("not using cache, paeg url is", page_url)
                self.browser.get(page_url)
                sanitized_page_name = re.sub(r'[^0-9a-zA-Z_]', '-', page_name.lower())
                filename = f'cache/{sanitized_page_name}.html'
                self.save_page(filename)
                self.db_manager.create(database.Tables.WEBPAGE_CACHE.value, {
                    'url': page_url,
                    'filename': filename
                }, ['url'])
            # if extra_wait_css_selector:
            #     print("INFO: extra wait for request page by css selector {}".format(extra_wait_css_selector))
            #     WebDriverWait(
            #         self.browser, timeout
            #     ).until(
            #         EC.visibility_of_element_located((By.CSS_SELECTOR, extra_wait_css_selector))
            #     )
            return True
        except TimeoutException:
            print("ERROR: Timeout waiting for GET webpage")
            return False
        except Exception:
            raise RuntimeError("ERROR: fail to request page {}".format(page_url))
    
    def access_targets(self, selector, base_element=None, many=True):
        """
            Locating Elements: https://selenium-python.readthedocs.io/locating-elements.html#locating-elements
        """
        if base_element:
            base = base_element
        else:
            base = self.browser
        
        if many:
            targets = base.find_elements_by_css_selector(selector)
        else:
            targets = base.find_element_by_css_selector(selector)
            
        return targets
    
    def close(self):
        self.browser.quit()
    
    def save_page(self, filename):
        with codecs.open(filename, "w", "utf-8") as fileObject:
            html = self.browser.page_source
            fileObject.write(html)