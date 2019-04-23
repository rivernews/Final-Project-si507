import database

class WebScrapper:

    def __init__(self, browser=None, db_manager=None):
        self.browser = browser
        self.db_manager = db_manager
    
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