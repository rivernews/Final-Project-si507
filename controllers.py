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
    # company_list = db_manager.filter(database.Tables.COMPANY.value, {})

    # join rating val into companies
    db_manager.db.cursor.execute(
        f"""
            SELECT company.id, company.name, company.size, company.url, rating.value
            FROM {database.Tables.COMPANY.value} AS company
            LEFT JOIN CompanyRating AS rating
            ON company.id = rating.id
            WHERE rating.source = 'glassdoor'
            ORDER BY rating.value desc;
        """
    )

    company_list = db_manager.db.cursor.fetchall()

    context = {
        'company_list': company_list,
        'company_fields': database.CompanyTable,
        'company_rating_field_index': 4
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
    ratings_table = {}
    for rating_result in rating_result_list:
        ratings_table[
            rating_result[database.CompanyRatingTable.SOURCE.value]
        ] = rating_result[
            database.CompanyRatingTable.VALUE.value
        ]
    ratings_table['fortune 500'] = int(ratings_table['fortune 500'])
    
    context = {
        'company': company_result_list[0],
        'company_fields': database.CompanyTable,
        'ratings_table': ratings_table,
    }

    return render_template('detail.html', **context)