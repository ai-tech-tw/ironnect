from flask import Flask, request
from flask_cors import cross_origin

from providers import (
    openai_local_iron,
    openai_proxy_gemini,
    openai_proxy_groq,
)

app = Flask(__name__)
app.config.from_pyfile("config.py")
app.config.from_pyfile("config.local.py", silent=True)
app.config["IRONNECT_TRIAL_PASSPHRASE"] = "zr3Pjc68z4bOtw=="


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

    # The always available provider for LLMs
    if request_provider == "nymph":
        return provider_nymph()

    # Specified providers for using LLMs
    if request_provider == "iron":
        return provider_iron(request_token)
    if request_provider == "gemini":
        return provider_gemini(request_token)
    if request_provider == "groq":
        return provider_groq(request_token)

    return "Unknown provider you requested.", 404


def provider_nymph():
    # Try to use Gemini first, then Groq, otherwise using local model
    trial_passphrase = app.config["IRONNECT_TRIAL_PASSPHRASE"]
    try:
        response = openai_proxy_gemini(
            "/v1",
            trial_passphrase,
            {
                "model": "gemini-2.0-flash",
            },
        )
        if response.status_code != 200:
            raise Exception("Provider request failed")
        return response
    except Exception:
        pass

    try:
        response = openai_proxy_groq(
            "/v1",
            trial_passphrase,
            {
                "model": "llama3-70b-chat",
            },
        )
        if response.status_code != 200:
            raise Exception("Provider request failed")
        return response
    except Exception:
        pass

    return openai_local_iron(
        trial_passphrase,
        {
            "model": "gemma-3-270m-it",
        },
    )


def provider_iron(request_token):
    return openai_local_iron(request_token)


def provider_gemini(request_token: str):
    return openai_proxy_gemini("/v1", request_token)


def provider_groq(request_token: str):
    return openai_proxy_groq("/v1", request_token)
