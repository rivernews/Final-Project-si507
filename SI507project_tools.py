import database
import settings as Settings

class WebScrapper:

    def __init__(self, browser=None, db_manager=None):
        self.browser = browser
        self.db_manager = db_manager
        self.company_list = []
    
    def fetch_fortune_company_list(self, is_get_all=False):
        self.company_list = []
        # locate the company in the page
        css_selector = (
            'ul.company-list ' +
            'li a span.company-title'
        )

        # navigate to target page
        if is_get_all:
            self.navigate_to(
                'http://fortune.com/fortune500/list/',
                page_name='fortune-500',
                
                infinite_scroll=True,
                infinite_scroll_spinner_css_selector=(
                    'div.F500-spinner'
                ),
                infinite_scroll_element_css_selector=(
                    'ul.company-list li'
                ),
                infinite_scroll_maximum_scroll_times=100
            )
        else:
            self.navigate_to(
                'http://fortune.com/fortune500/list/',
                page_name='fortune-500',
            )

        # get the company name list
        
        company_span_list = self.browser.access_targets(css_selector)
        self.company_list = [
            span.get_attribute('innerHTML') for span in company_span_list
        ]

    def create_or_update_company(self, company_data={}):
        if 'id' in company_data:
            company_id = company_data.pop('id')
        elif not 'name' in company_data:
            raise KeyError('ERROR: at least give either name or id when create/update company.')
        else:
            query_object = {'name': company_data['name']}
            if self.db_manager.count(database.Tables.COMPANY.value, query_object) > 0:
                # user did not pass in company `id`, but the company is already in database
                company_id = self.db_manager.filter(
                    database.Tables.COMPANY.value, query_object
                )[0][database.CompanyTable.ID.value]
            else:
                # no company data in database so indeed need to create
                company_id = self.db_manager.create(database.Tables.COMPANY.value, {
                    'name': ''
                })

        if 'companyratings' in company_data:
            companyratings = company_data.pop('companyratings')
            
            if not isinstance(companyratings, list):
                raise TypeError('ERROR: companyratings should be a list.')
            
            for companyrating in companyratings:
                if not (
                    'source' in companyrating
                ):
                    raise KeyError('ERROR: Please make sure you provide source, sample_date in companyratings.')

                # in case user send in `companyId`; we will assign companyId explicitly
                companyrating['companyId'] = company_id

                # check if exists; if exists, perform udpate
                if 'id' in companyrating and self.db_manager.count(database.Tables.COMPANY_RATING.value, {'id': companyrating['id']}) > 0:
                    del companyrating['id']
                    self.db_manager.update(database.Tables.COMPANY_RATING.value, companyrating)
                # if not, create it
                else:
                    if 'id' in companyrating:
                        del companyrating['id']
                    self.db_manager.create(database.Tables.COMPANY_RATING.value, companyrating)

        if 'hq_location' in company_data:
            hq_location = company_data.pop('hq_location')
            # TODO

        if 'home_page' in company_data:
            home_page = company_data.pop('home_page')
            # TODO
        
        # assign value for update/create
        if company_id != None:
            self.db_manager.update(database.Tables.COMPANY.value, {
                **company_data
            }, company_id)
        
        return company_id

    
    def get_company_glassdoor_rating(self, company_name):
        
        # check if any rating exists in database; if so than just use database data.
        company = None
        result_list = self.db_manager.filter(database.Tables.COMPANY.value, {
            'name': company_name
        })
        if len(result_list) > 0:
            company = result_list[0]
        else:
            print(f'WARNING: company = {company_name} is not in database, so cannot lookup glassdoor rating for it.')
            return
        
        glassdoor_company_rating = None
        result_list = self.db_manager.filter(database.Tables.COMPANY_RATING.value, {
            'companyId': company[database.CompanyTable.ID.value],
            'source': 'glassdoor'
        })
        if len(result_list) > 0:
            glassdoor_company_rating = result_list[0]
            return glassdoor_company_rating[database.CompanyRatingTable.VALUE.value]

        # rating for company is not in database, so we now scrap it
        rating = -1

        company_header_css_selector = (
            'div[id=ReviewSearchResults] ' +
            'div.header.cell.info'
        )
        sanitized_company_name = company_name.strip().replace(' ', '-')
        self.navigate_to(
            self.generate_glassdoor_company_query_url(company_name),
            page_name=f'gd-{sanitized_company_name}'
        )

        # extract that specific company rating data
        company_header_list = self.browser.access_targets(
            company_header_css_selector
        )
        if len(company_header_list) > 0:
            for company_header in company_header_list:

                # use the target company only
                company_name_anchor = self.browser.access_targets(
                    'div.margBotXs a',
                    base_element=company_header,
                    many=False
                )
                if company_name_anchor.get_attribute('innerHTML').strip().lower() == company_name.lower():
                    rating_span = self.browser.access_targets('div.ratingsSummary span.bigRating', base_element=company_header, many=False)
                    if rating_span == None:
                        # Not yet rated, like https://www.glassdoor.com/Reviews/plains-gp-holdings-reviews-SRCH_KE0,18.htm
                        return -1
                    rating = float(rating_span.get_attribute('innerHTML').strip())
                    return rating
            
            # no company header matches company name, then just use first search result
            company_header = company_header_list[0]
            rating_span = self.browser.access_targets('div.ratingsSummary span.bigRating', base_element=company_header, many=False)
            
            if rating_span == None:
                # We guess the 1st result is the correct company
                # but the company has no rating data yet
                # e.g. https://www.glassdoor.com/Reviews/united-continental-holdings-reviews-SRCH_KE0,27.htm
                print(f'WARNING: cannot get glassdoor rating for {company_name}. Url = {self.generate_glassdoor_company_query_url(company_name)}')
                return -1

            rating = float(rating_span.get_attribute('innerHTML').strip())
            return rating

        else:
            # glassdoor might be single result page so have a different layout
            # like https://www.glassdoor.com/Overview/Working-at-Fannie-Mae-EI_IE247.11,21.htm
            rating_div = self.browser.access_targets((
                'div.ratingInfo > div.ratingNum'
            ), many=False)
            
            if rating_div == None:
                # exception, not sure what's going on here & might need to look at the webpage to actually see what it looks like
                # like https://www.glassdoor.com/Reviews/costco-reviews-SRCH_KE0,6.htm
                # The company name in Fortune 500 is Costco, but in glassdoor the name is `Costco Wholesale`
                print(f'WARNING: cannot get glassdoor rating for {company_name}. Url = {self.generate_glassdoor_company_query_url(company_name)}')
                return -1
            
            rating = float(rating_div.get_attribute('innerHTML').strip())
            return rating
    
    def batch_scrap_and_store_company_data(self, fortune_rank_range=[1,10]):
        if len(self.company_list) == 0:
            self.fetch_fortune_company_list()
        
        scrapped_company_id_list = []

        loop_range = None
        if isinstance(fortune_rank_range, list):
            if len(fortune_rank_range) == 2 and fortune_rank_range[1] <= len(self.company_list):
                loop_range = range(fortune_rank_range[0], fortune_rank_range[1] + 1)
            elif len(fortune_rank_range) == 1:
                # by default we will fetch as much companies as we can if amount/end rank exceeded `self.company_list`
                loop_range = range(fortune_rank_range[0], len(self.company_list) + 1)
            else:
                loop_range = range(1, len(self.company_list) + 1)
        # only work on one company given the specific rank number
        elif isinstance(fortune_rank_range, int):
            loop_range = range(fortune_rank_range, fortune_rank_range + 1)
        
        if loop_range:
            for fortune_rank in loop_range:
                company_name = self.company_list[fortune_rank - 1]
                
                # query company object in database
                company_result_list = self.db_manager.filter(database.Tables.COMPANY.value, {
                    'name': company_name
                })
                if len(company_result_list) == 0:
                    company_id = self.create_or_update_company({ 'name': company_name })
                else:
                    company_id = company_result_list[0][database.CompanyTable.ID.value]

                rating = self.get_company_glassdoor_rating(company_name)

                self.create_or_update_company({
                    'id': company_id,
                    'name': company_name,
                    'companyratings': [
                        {
                            'source': 'glassdoor',
                            'value': rating
                        },
                        {
                            'source': 'fortune 500',
                            'value': fortune_rank
                        }
                    ]
                })

                scrapped_company_id_list.append(company_id)
            
            return scrapped_company_id_list
    
    def navigate_to(
        self, url, page_name,
        infinite_scroll=False,
        infinite_scroll_spinner_css_selector='',
        infinite_scroll_element_css_selector='',
        infinite_scroll_timeout=20,
        infinite_scroll_element_maximum_amount=1000,
        infinite_scroll_maximum_scroll_times=10,
    ):
        self.browser.request_page(
            page_url=url, page_name=page_name,
            infinite_scroll=infinite_scroll,
            infinite_scroll_spinner_css_selector=infinite_scroll_spinner_css_selector,
            infinite_scroll_element_css_selector=infinite_scroll_element_css_selector,
            infinite_scroll_timeout=infinite_scroll_timeout,
            infinite_scroll_element_maximum_amount=infinite_scroll_element_maximum_amount,
            infinite_scroll_maximum_scroll_times=infinite_scroll_maximum_scroll_times,
        )
    
    def generate_glassdoor_company_query_url(self, company_name):
        template_url = '''https://www.glassdoor.com/Reviews/company-reviews.htm?suggestCount=10&suggestChosen=false&clickSource=searchBtn&typedKeyword=%s&sc.keyword=%s&locT=C&locId=&jobType='''
        return template_url.replace('%s', company_name)