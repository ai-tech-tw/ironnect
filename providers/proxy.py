from flask import current_app, request, Response
from requests import request as send_request
from urllib.parse import urljoin


def filter_exclude_headers(args: tuple) -> bool:
    key = args[0].lower()
    excluded_headers = (
        "access-control-allow-credentials",
        "access-control-allow-headers",
        "access-control-allow-methods",
        "access-control-allow-origin",
        "access-control-expose-headers",
        "access-control-max-age",
        "access-control-request-headers",
        "access-control-request-method",
        "transfer-encoding",
        "content-encoding",
        "accept-encoding",
        "content-length",
        "content-type",
        "connection",
        "host",
    )
    return key not in excluded_headers


def openai_proxy_gemini(prefix: str, token: str, override_json: dict = {}):
    endpoint_url = current_app.config["AI_PROXY_ENDPOINT_URL_GEMINI"]
    trial_passphrase = current_app.config["IRONNECT_TRIAL_PASSPHRASE"]
    prefill_token = current_app.config.get("AI_TRIAL_PREFILL_TOKEN_GEMINI")
    request_token = prefill_token if token == trial_passphrase else token
    return ai_request_proxy(endpoint_url, prefix, request_token, override_json=override_json)


def openai_proxy_groq(prefix: str, token: str, override_json: dict = {}):
    endpoint_url = current_app.config["AI_PROXY_ENDPOINT_URL_GROQ"]
    trial_passphrase = current_app.config["IRONNECT_TRIAL_PASSPHRASE"]
    prefill_token = current_app.config.get("AI_TRIAL_PREFILL_TOKEN_GROQ")
    request_token = prefill_token if token == trial_passphrase else token
    return ai_request_proxy(endpoint_url, prefix, request_token, override_json=override_json)


def ai_request_proxy(endpoint_url: str, prefix: str, token: str, override_json: dict = {}):
    app_root = current_app.config.get("APPLICATION_ROOT")
    app_root = app_root and app_root.lstrip("/")
    prefix = prefix and prefix.lstrip("/")

    current_url = urljoin(request.host_url, app_root)
    current_url = urljoin(current_url, prefix)

    request_method = request.method
    request_url = request.url.replace(current_url, endpoint_url)
    request_headers = {k: v for k, v in filter(filter_exclude_headers, request.headers)}
    request_json = request.get_json()

    if override_json:
        request_json.update(override_json)

    request_headers["user-agent"] = (
        "Ironnect/1.1 (+https://github.com/ai-tech-tw/ironnect)"
    )
    request_headers["authorization"] = f"Bearer {token}"

    proxy_response = send_request(
        method=request_method,
        url=request_url,
        headers=request_headers,
        json=request_json,
    )

    response_data = proxy_response.content
    response_status = proxy_response.status_code
    response_headers = list(proxy_response.raw.headers.items())
    response_headers.append(("x-ironnect-proxy-endpoint-url", endpoint_url))
    response_headers = filter(filter_exclude_headers, response_headers)

    return Response(response_data, response_status, response_headers)
