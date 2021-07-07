import os
from os.path import join, dirname

import requests
from dotenv import load_dotenv
from flask import Flask, request, abort

app = Flask(__name__)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


@app.route('/')
def index():
    username = request.args.get('username')
    auth_header = request.headers.get('Authorization')
    if auth_header is None or auth_header[0:6] != 'Bearer' or auth_header[7:] != os.environ.get('API_KEY'):
        abort(403)
    res = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    return res.json()['title'] + username


if __name__ == "__main__":
    app.run(debug=True)
