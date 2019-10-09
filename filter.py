from flask import Blueprint

from SI507project_tools import WebScrapper

filters = Blueprint('filters', __name__)

@filters.app_template_filter('as_glassdoor_url')
def get_gd_url(company_name):
    return WebScrapper.generate_glassdoor_company_query_url(company_name)