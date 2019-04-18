class WebScrapper:

    def __init__(self, browser=None, db=None):
        self.browser = browser
        self.db = db
    
    def fetch_fortune_company_list(self):
        self.company_list = []

        # navigate to target page
        self.navigate_to('http://fortune.com/fortune500/list/')

        # get the company name list
        css_selector = (
            'ul.company-list ' +
            'li a span.company-title'
        )
        company_span_list = self.browser.access_targets(css_selector)
        self.company_list = [
            span.get_attribute('innerHTML') for span in company_span_list
        ]

        
    
    def get_company_rating(self, company):

        rating = 0

        return rating
    
    def navigate_to(self, url):
        self.browser.request_page(page_url=url)
    