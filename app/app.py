from flask import Flask

app = Flask(__name__)

## start view functions

@app.route('/', methods=['GET'])
def index():
    return "hi"

if __name__ == "__main__":
    app.run()
