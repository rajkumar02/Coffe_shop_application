import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks")
def get_drink():
    drink_query = Drink.query.all()
    drinks = [data.short() for data in drink_query]
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_details(payload):
    drink_query = Drink.query.all()
    drinks = [data.short() for data in drink_query]
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks")
@requires_auth("post:drinks")
def post_drinks(payload):
    get_body = request.get_json()
    drink = Drink()
    drink.recipe = json.dumps(get_body.get("recipe"))
    drink.title = get_body.get("title")
    drink.insert()
    return jsonify({
        "success": True,
        "drink": drink.long()
    }), 201


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drinks_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drinks(payload, drinks_id):
    get_body = request.get_json()
    title = get_body.get('title', None)
    recipe = get_body.get('recipe', None)

    try:
        drink = Drink.query.filter_by(id=drinks_id).one_or_none()
        if drink is None:
            abort(404)

        if title is None:
            abort(400)

        if title is not None:
            drink.title = title

        if recipe is not None:
            drink.recipe = json.dumps(recipe)

        drink.update()

        drink_update = Drink.query.filter_by(id=drinks_id).first()

        return jsonify({
            'success': True,
            'drinks': [drink_update.long()]
        })

    except:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks/<int:drinks_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drinks(token, drinks_id):
    try:

        drink = Drink.query.filter_by(id=drinks_id).one_or_none()

        if drink is None:
            abort(404)
        drink.delete()

        return jsonify({
            'success': True,
            'delete': drinks_id
        })

    except:

        abort(422)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'Unauthorized'
    }, 401)


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"

    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method not allowed'
    }, 405)


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }, 500)
