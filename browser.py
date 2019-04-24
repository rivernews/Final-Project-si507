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
import time

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
        # options.add_argument("--headless")

        # https://stackoverflow.com/questions/44770796/how-to-make-selenium-not-wait-till-full-page-load-which-has-a-slow-script/44771628
        
        browser = webdriver.Chrome(
            executable_path=(PROJECT_ROOT_DIRECTORY / 'chromedriver').resolve(),
            options=options,
        )

        return browser
    
    def consume_infinite_scroll_page(self,
        infinite_scroll_smooth,
        infinite_scroll_spinner_css_selector,
        infinite_scroll_element_css_selector,
        infinite_scroll_timeout,
        infinite_scroll_maximum_scroll_times,
    ):
        scroll_times = 0
        visible_spinner_timeout_times = 0
        visible_spinner_timeout_maximum_times = 2
        element_list = []
        browser_short_pauser = WebDriverWait(
            self.browser, 3.5
        )
        browser_pauser = WebDriverWait(
            self.browser, infinite_scroll_timeout
        )
        while True:
            # scroll down
            print('INFO: scrolling down.')
            if infinite_scroll_smooth:
                self.browser.execute_script("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")
            else:
                self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            scroll_times += 1
            print(f'INFO: scroll times = {scroll_times}/{infinite_scroll_maximum_scroll_times}')
            if scroll_times >= infinite_scroll_maximum_scroll_times:
                break
            
            # expect spinner showing
            # if timed out - it's not showing, then might mean no further content so break
            try:
                print('INFO: waiting for visible spinner...')
                browser_short_pauser.until(
                    EC.visibility_of_element_located((
                        By.CSS_SELECTOR,
                        infinite_scroll_spinner_css_selector
                    ))
                )
                print('INFO: spinner found.')

                # expect disappear
                # if timed out - it's spinning a long time, then probably poor/slow network.
                # we might choose to raise a timeout error; or break loop and mark this func as best effort
                try:
                    print('INFO: waiting for spinner to become invisible...')
                    browser_pauser.until(
                        EC.invisibility_of_element_located((
                            By.CSS_SELECTOR,
                            infinite_scroll_spinner_css_selector
                        ))
                    )
                    print('INFO: spinner disappeared.')
                except TimeoutException:
                    msg = 'WARNING: spinner loading too long, perhaps due to poor network. Will stop consuming infinite scroll, but the result might be incomplete.'
                    print(msg)
                    # raise TimeoutException(msg)
                    break

                # wait .5~1 sec for page to load Ajax data
                time.sleep(1)
            
            except TimeoutException:
                print('INFO: timed out and move on.')
                # visible_spinner_timeout_times += 1
                # if visible_spinner_timeout_times > visible_spinner_timeout_maximum_times:
                #     print('INFO: waiting for spinner showing timed out. Will stop consuming infinite scroll.')
                #     break
                # else:
                #     print(f'INFO: timed out, times = {visible_spinner_timeout_times}/{visible_spinner_timeout_maximum_times}')

            # compare if element list increased. if not, break
            elements_list_in_page = self.access_targets(
                infinite_scroll_element_css_selector,
            )
            print(f'INFO: infinite scroll items {len(element_list)} -> {len(elements_list_in_page)}')
            if len(elements_list_in_page) > len(element_list):
                element_list = elements_list_in_page
                continue
            else:
                break
        
        print(f'INFO: finish consuming infinite scroll, list amount = {len(element_list)}')

    
    def request_page(self,
            infinite_scroll,
            infinite_scroll_smooth,
            infinite_scroll_spinner_css_selector,
            infinite_scroll_element_css_selector,
            infinite_scroll_timeout,
            infinite_scroll_maximum_scroll_times,
            page_url="http://fortune.com/fortune500/list/",
            page_name='',
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
                
                # access page online
                self.browser.get(page_url)

                if infinite_scroll and infinite_scroll_spinner_css_selector and infinite_scroll_element_css_selector:
                    self.consume_infinite_scroll_page(
                        infinite_scroll_smooth,
                        infinite_scroll_spinner_css_selector,
                        infinite_scroll_element_css_selector,
                        infinite_scroll_timeout,
                        infinite_scroll_maximum_scroll_times,
                    )

                # cache webpage
                sanitized_page_name = re.sub(r'[^0-9a-zA-Z_]', '-', page_name.lower())
                filename = f'cache/{sanitized_page_name}.html'
                self.save_page(filename)
                self.db_manager.create(database.Tables.WEBPAGE_CACHE.value, {
                    'url': page_url,
                    'filename': filename
                }, ['url'])
            
            return True
        except TimeoutException:
            print("ERROR: Timeout waiting for GET webpage")
            return False
        except Exception as e:
            raise RuntimeError("ERROR: fail to request page {}. Exception={}".format(page_url, e))
    
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