from flask import Flask
from dotenv import load_dotenv

from .views.web import index, heartbeat


app = Flask(__name__)

load_dotenv()

app.add_url_rule('/heartbeat', view_func=heartbeat, methods=['GET'])

app.add_url_rule('/', view_func=index, defaults={'path': ''}, methods=['GET'])
app.add_url_rule('/<path:path>', view_func=index, methods=['GET'])


if __name__ == '__main__':
    app.run()
