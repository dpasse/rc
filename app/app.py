import os
from dotenv import load_dotenv
from flask import Flask, render_template

app = Flask(__name__)

load_dotenv()


@app.route('/', methods=['GET'])
def index() -> str:
    return render_template(
        'index.html',
        version=os.getenv('VERSION')
    )

if __name__ == '__main__':
    app.run()
