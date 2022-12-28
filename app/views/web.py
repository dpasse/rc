import os
from flask import render_template, jsonify


def index(path: str) -> str:
    model = {
        'version': os.getenv('VERSION')
    }

    return render_template('index.html', model=model)

def heartbeat():
    model = {
        'status': 'healthy'
    }

    return jsonify(model)
