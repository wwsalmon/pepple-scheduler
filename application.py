import json
import os
from os.path import join, dirname

from dotenv import load_dotenv
from flask import Flask, request, abort

from data_gen import get_day_objects

application = Flask(__name__)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


@application.route('/')
def index():
    auth_header = request.headers.get('Authorization')
    if auth_header is None or auth_header[0:6] != 'Bearer' or auth_header[7:] != os.environ.get('API_KEY'):
        abort(403)

    username = request.args.get('username')

    day_objects = get_day_objects(username)

    return {"day_objects": day_objects}


if __name__ == "__main__":
    application.run(debug=True)
