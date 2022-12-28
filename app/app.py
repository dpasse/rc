import os
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify

app = Flask(__name__)

load_dotenv()


@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "healthy"})

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def index(path: str) -> str:
    return render_template(
        'index.html',
        version=os.getenv('VERSION')
    )

if __name__ == '__main__':
    app.run()
