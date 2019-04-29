#!/usr/bin/env python3
import os
import json
from flask import Flask, Response
from lib import capacity

app = Flask(__name__)


@app.route('/')
def get_capacity():
    return Response(json.dumps(capacity.get_capacity_data()), mimetype='application/json')


@app.route('/health')
def hello_world():
    health = {
        "status": "UP"
    }
    return Response(json.dumps(health), mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
