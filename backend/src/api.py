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
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def getDrinks():
    # getting all drinks from db
    allDrinks = Drink.query.all()
    if len(allDrinks) == 0:
        abort(404)
    # drink.short() representation
    sortedDrinks = [d.short() for d in allDrinks]
    result = {
        'success': True,
        'drinks': sortedDrinks
    }
    # Explicitly returning status code 200 as it is mentioned in requirements
    return jsonify(result), 200


'''
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def getDrinkDetail(payload):
    allDrinks = Drink.query.all()
    if len(allDrinks) == 0:
        abort(404)
    # drink.long() representation
    longDrinks = [d.long() for d in allDrinks]
    result = {
        'success': True,
        'drinks': longDrinks
    }
    # Explicitly returning status code 200 as it is mentioned in the requirements
    return jsonify(result), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def createNewDrink(payload):
    # fetch Input
    if request.data:
        inputReqData = json.loads(request.data.decode('utf-8'))
        try:
            d = Drink()
            d.title = inputReqData['title']
            d.recipe = json.dumps(inputReqData['recipe'])
            # add Newly created drink
            d.insert()

        except Exception:
            abort(400)

        result = {
            'success': True,
            'drinks': [d.long()]
        }

        # Explicitly returning status code 200 as it is mentioned in the requirements
        return jsonify(result), 200


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
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deleteDrinks(payload, id):
    # fetch drink details for the input ID with one_or_none() for subsequent validaity checksss
    drinkData = Drink.query.filter(Drink.id == id).one_or_none()

    # Req 1: throw 404 error is no drink is found
    if not drinkData:
        abort(404)

    # try to delete drink and in case of error throw exception
    try:
        drinkData.delete()
    except Exception:
        abort(400)

    result = {
            'success': True,
            'delete': id
        }

    # Explicitly returning status code 200 as it is mentioned in the requirements
    return jsonify(result), 200



# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def errorUnprocessable(error):
    errorData = {
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }
    return jsonify(errorData), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def errorNotFound(error):
    errorData = {
        "success": False,
        "error": 404,
        "message": "Resource Not Found"
    }
    return jsonify(error_data), 404



'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authEror(error):
    return jsonify(e.error), e.status_code



