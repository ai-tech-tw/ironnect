from flask import Flask, request
from flask_cors import cross_origin
from proxy import gemini_openai_proxy

app = Flask(__name__)
app.config.from_pyfile("config.py")
app.config.from_pyfile("config.local.py", silent=True)


@app.route("/")
def greet():
    hosturl = request.host_url
    message = f"Greeting! {hosturl}"
    return message


@app.route("/v1/<path:_>", methods=["GET", "POST"])
@cross_origin()
def openai_pass(_):
    return gemini_openai_proxy("/v1")


@app.route("/trial/v1/<path:_>", methods=["GET", "POST"])
@cross_origin()
def openai_trial(_):
    prefill_token = app.config.get("GEMINI_OPENAI_PREFILL_TOKEN")
    return gemini_openai_proxy("/trial/v1", prefill_token)
