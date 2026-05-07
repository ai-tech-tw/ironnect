from flask import Flask, HTTPException, request
from flask_cors import cross_origin

from providers import (
    openai_local,
    openai_proxy,
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


@app.route("/v1/<path:req_path>", methods=["GET", "POST"])
@cross_origin()
def openai_pass(req_path: str):
    request_headers = request.headers
    request_auth = request_headers.get("authorization", "")

    request_auth_args = request_auth.split(" ", 3)
    if len(request_auth_args) < 2 or request_auth_args[0].lower() != "bearer":
        raise HTTPException("Invalid Authorization header.", 400)

    if len(request_auth_args) == 2:
        request_provider = "nymph"
        request_token = request_auth_args[1]
    else:
        request_provider = request_auth_args[1].lower()
        request_token = request_auth_args[2]

    if req_path not in app.config.get("AI_PROXY_ALLOWED_PATHS", []):
        raise HTTPException("The requested path is not allowed.", 403)

    # The always available provider for LLMs
    if request_provider == "nymph":
        return provider_nymph(request_token, req_path)

    # Specified providers for using LLMs
    if request_provider == "iron":
        return openai_local(request_token)

    # Other providers by proxy, with the order of priority defined in the config
    proxy_providers = app.config.get("AI_PROXY_PROVIDERS", [])
    if request_provider in proxy_providers:
        return openai_proxy(request_provider, "/v1", request_token, req_path)

    # No provider matched, return an error
    raise HTTPException(f"Unknown provider you requested: {request_provider}", 404)


def provider_nymph(request_token: str, api_type: str = ""):
    # Try each proxy provider in order, with Iron as the final fallback
    trial_passphrase = app.config.get("IRONNECT_TRIAL_PASSPHRASE")
    if not trial_passphrase:
        raise HTTPException("Internal Server Error: Trial passphrase not configured.", 500)    
    if request_token != trial_passphrase:
        raise HTTPException("Invalid token for the model.", 403)    
    proxy_providers = app.config.get("AI_PROXY_PROVIDERS", [])

    for provider in proxy_providers:
        trial_model = app.config.get(f"AI_TRIAL_NYMPH_MODEL_{provider.upper()}")
        if not trial_model:
            continue
        try:
            response = openai_proxy(
                provider,
                "/v1",
                trial_passphrase,
                api_type,
            )
            if response.status_code != 200:
                print(f"Provider {provider} request failed: {response.status_code}")
                continue
            return response
        except Exception as e:
            print(f"Provider {provider} request failed: {e}")

    # Iron is always the final fallback
    trial_model_iron = app.config.get("AI_TRIAL_NYMPH_MODEL_IRON", "")
    return openai_local(
        trial_passphrase,
        {
            "model": trial_model_iron,
        },
    )
