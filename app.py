from flask import Flask, request
from proxy import gemini_openai_proxy

app = Flask(__name__)
app.config.from_pyfile("config.py")
app.config.from_pyfile("config.local.py", silent=True)


@app.route("/")
def greet():
    hosturl = request.host_url
    message = f"Greeting! {hosturl}"
    return message


@app.route("/openai/v1/<path:_>", methods=["GET", "POST"])
def openai_pass(_):
    return gemini_openai_proxy("/openai/v1")


@app.route("/openai/trial/v1/<path:_>", methods=["GET", "POST"])
def openai_trial(_):
    prefill_token = app.config.get("GEMINI_OPENAI_PREFILL_TOKEN")
    return gemini_openai_proxy("/openai/trial/v1", prefill_token)
