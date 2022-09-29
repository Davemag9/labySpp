from flask import Flask

app = Flask(__name__)

@app.route("/api/v1/hello-world-{16}")
def hello_world():
    return "<p>Hello, World - 16!</p>", 200