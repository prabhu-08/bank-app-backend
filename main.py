from app import app, mongo
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import jsonify, request, send_from_directory
import string
import random
from datetime import datetime, timedelta
import os
import sys

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
os.environ.update({'ROOT_PATH': ROOT_PATH})
sys.path.append(os.path.join(ROOT_PATH, 'modules'))

PUBLIC_PATH = os.path.join(ROOT_PATH, 'public')
time_range_hours = {"1hour": 1, "5hours": 5}
time_range_days = {"day": 1, "week": 7, "month": 30}


def string_generator(size):
    chars = string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(size))


def string_num_generator(size):
    chars = string.digits
    return ''.join(random.choice(chars) for _ in range(size))


@app.route('/')
def index():
    """ static files serve """
    return send_from_directory(PUBLIC_PATH, 'index.html')


@app.route('/<path:path>')
def static_proxy(path):
    """ static folder serve """
    file_name = path.split('/')[-1]
    dir_name = os.path.join(PUBLIC_PATH, '/'.join(path.split('/')[:-1]))
    return send_from_directory(dir_name, file_name)


@app.route('/api/add')
def add_transcation():
    _json = {'from': string_generator(4),
             "to": string_generator(4), 'time': datetime.utcnow(), 'amount': string_num_generator(3)}
    _time = _json['time']
    _from = _json['from']
    _to = _json['to']
    _amount = _json['amount']
    id = mongo.db.transaction.insert(
        {'time': _time, 'from': _from, 'to': _to, 'amount': int(_amount)})
    resp = jsonify('bank data added successfully!')
    resp.status_code = 200
    return resp


@app.route('/api/data', methods=['GET'])
def users():
    duration = request.args.get('duration')
    if time_range_hours.get(duration):
        minDate = datetime.utcnow() - \
            timedelta(hours=time_range_hours[duration])
    elif time_range_days.get(duration):
        minDate = datetime.utcnow() - \
            timedelta(days=time_range_days[duration])
    else :
        minDate = datetime.utcnow() - timedelta(hours=1)
    maxDate = datetime.utcnow()
    transaction = mongo.db.transaction.aggregate([
        {"$match": {
            "time": {"$gte": minDate,
                     "$lt": maxDate
                     }
        }
        }, {"$group": {
            "_id": {
                "$toDate": {
                    "$subtract": [
                        {"$toLong": "$time"},
                        {"$mod": [{"$toLong": "$time"}, 1000 * 60 * 15]}
                    ]
                }
            },
            "total_amount": {"$avg": "$amount"},
            "count": {"$sum": 1}
        }}
    ])
    resp = dumps(transaction)
    return resp


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


if __name__ == "__main__":
    app.run()