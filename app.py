from flask import Flask, request
from flask_cors import cross_origin

from proxy import (
    gemini_openai_proxy,
    groq_openai_proxy,
)

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
    request_headers = request.headers
    request_auth = request_headers.get("authorization", "")

    request_auth_args = request_auth.split(" ", 3)
    if len(request_auth_args) < 2 or request_auth_args[0].lower() != "bearer":
        return "Invalid Authorization header.", 400

    if len(request_auth_args) == 2:
        request_provider = "gemini"
        request_token = request_auth_args[1]
    else:
        request_provider = request_auth_args[1].lower()
        request_token = request_auth_args[2]

    if request_provider == "gemini":
        return gemini_openai_proxy("/v1", request_token)
    if request_provider == "groq":
        return groq_openai_proxy("/v1", request_token)

    return "Unknown provider you requested.", 404


@app.route("/trial/v1/<path:_>", methods=["GET", "POST"])
@cross_origin()
def openai_trial(_):
    request_headers = request.headers
    request_auth = request_headers.get("authorization", "")

    request_auth_args = request_auth.split(" ", 2)
    if len(request_auth_args) != 2 or request_auth_args[0].lower() != "bearer":
        return "Invalid Authorization header.", 400

    prefill_token_gemini = app.config.get("GEMINI_OPENAI_PREFILL_TOKEN")
    prefill_token_groq = app.config.get("GROQ_OPENAI_PREFILL_TOKEN")

    request_provider = request_auth_args[1].lower()
    if request_provider == "gemini" and prefill_token_gemini:
        return gemini_openai_proxy("/v1", prefill_token_gemini)
    if request_provider == "groq" and prefill_token_groq:
        return groq_openai_proxy("/v1", prefill_token_groq)

    return "Unknown provider you requested.", 404
