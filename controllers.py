from flask import Blueprint, render_template, jsonify, abort, make_response, request

import database

routes = Blueprint('routes', __name__)

@routes.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found', 'detail': error}), 404)

@routes.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request', 'detail': error}), 400)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/companies/')
def list_company():
    db_manager = database.DatabaseManager()
    company_list = db_manager.filter(database.Tables.COMPANY.value, {})
    context = {
        'company_list': company_list,
        'company_fields': database.CompanyTable,
    }
    return render_template('master.html', **context)

@routes.route('/companies/<int:id>/')
def detail_company(id):
    db_manager = database.DatabaseManager()

    # query company data
    company_result_list = db_manager.filter(database.Tables.COMPANY.value, {
        'id': id
    })

    if len(company_result_list) == 0:
        abort(404)
        return
    
    # query rating data
    rating_result_list = db_manager.filter(database.Tables.COMPANY_RATING.value, {
        'companyId': id
    })
    
    context = {
        'company': company_result_list[0],
        'company_fields': database.CompanyTable,
        'ratings': rating_result_list,
        'rating_fields': database.CompanyRatingTable,
    }

    return render_template('detail.html', **context)