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
    
    def __init__(self, *args, **kwargs):
        self.browser = self.get_browser()
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

        # https://stackoverflow.com/questions/44770796/how-to-make-selenium-not-wait-till-full-page-load-which-has-a-slow-script/44771628
        
        browser = webdriver.Chrome(
            executable_path=(PROJECT_ROOT_DIRECTORY / 'chromedriver').resolve(),
            options=options,
        )

        return browser
    
    def request_page(self,
            page_url="http://fortune.com/fortune500/list/",
            timeout=10,
        ):
        try:
            print("INFO: browser getting the page...")
            self.browser.get(page_url)
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