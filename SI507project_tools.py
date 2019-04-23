class WebScrapper:

    def __init__(self, browser=None, db=None):
        self.browser = browser
        self.db = db
    
    def fetch_fortune_company_list(self):
        self.company_list = []

        # locate the company in the page
        css_selector = (
            'ul.company-list ' +
            'li a span.company-title'
        )

        # navigate to target page
        self.navigate_to(
            'http://fortune.com/fortune500/list/',
            page_name='fortune-500'
        )

        # get the company name list
        
        company_span_list = self.browser.access_targets(css_selector)
        self.company_list = [
            span.get_attribute('innerHTML') for span in company_span_list
        ]

        
    
    def get_company_rating(self, company):

        rating = 0.0

        company_header_css_selector = (
            'div[id=ReviewSearchResults] ' +
            'div.header.cell.info'
        )
        sanitized_company_name = company.strip().replace(' ', '-')
        self.navigate_to(
            self.generate_glassdoor_company_query_url(company),
            page_name=f'gd-{sanitized_company_name}'
        )

        # extract that specific company rating data
        company_header_list = self.browser.access_targets(
            company_header_css_selector
        )
        for company_header in company_header_list:

            # use the target company only
            company_name_anchor = self.browser.access_targets(
                'div.margBotXs a',
                base_element=company_header,
                many=False
            )
            if company_name_anchor.get_attribute('innerHTML').strip().lower() == company.lower():
                rating_span = self.browser.access_targets('span.bigRating', base_element=company_header, many=False)
                rating = float(rating_span.get_attribute('innerHTML').strip())
                return rating

        return rating
    
    def navigate_to(self, url, page_name):
        self.browser.request_page(page_url=url, page_name=page_name)
    
    def generate_glassdoor_company_query_url(self, company_name):
        template_url = '''https://www.glassdoor.com/Reviews/company-reviews.htm?suggestCount=10&suggestChosen=false&clickSource=searchBtn&typedKeyword=%s&sc.keyword=%s&locT=C&locId=&jobType='''
        return template_url.replace('%s', company_name)