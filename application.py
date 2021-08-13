import os
from os.path import join, dirname

import requests
from dotenv import load_dotenv
from flask import Flask, request, abort
from threading import Thread
import time

from data_gen import get_day_objects

application = Flask(__name__)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


@application.route('/')
def index():
    auth_header = request.headers.get('Authorization')
    if auth_header is None or auth_header[0:6] != 'Bearer' or auth_header[7:] != os.environ.get('SCHEDULER_API_KEY'):
        abort(403)

    username = request.args.get('username')
    month = request.args.get('month')
    year = request.args.get('year')

    if username is None or month is None or year is None:
        abort(400)

    day_objects = get_day_objects(username, month, year)

    return {"day_objects": day_objects}


if __name__ == "__main__":
    application.run(debug=True)
