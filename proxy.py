from flask import current_app, request, Response
from requests import request as send_request
from urllib.parse import urljoin

trial_passphrase = "zr3Pjc68z4bOtw=="


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
        "connection",
        "host",
    )
    return key not in excluded_headers


def openai_proxy_gemini(prefix: str, token: str):
    endpoint_url = current_app.config["OPENAI_ENDPOINT_URL_GEMINI"]
    prefill_token = current_app.config.get("AI_TRIAL_PREFILL_TOKEN_GEMINI")
    request_token = prefill_token if token == trial_passphrase else token
    return ai_request_proxy(endpoint_url, prefix, request_token)


def openai_proxy_groq(prefix: str, token: str):
    endpoint_url = current_app.config["OPENAI_ENDPOINT_URL_GROQ"]
    prefill_token = current_app.config.get("AI_TRIAL_PREFILL_TOKEN_GROQ")
    request_token = prefill_token if token == trial_passphrase else token
    return ai_request_proxy(endpoint_url, prefix, request_token)


def ai_request_proxy(endpoint_url: str, prefix: str, token: str):
    app_root = current_app.config.get("APPLICATION_ROOT")
    app_root = app_root and app_root.lstrip("/")
    prefix = prefix and prefix.lstrip("/")

    current_url = urljoin(request.host_url, app_root)
    current_url = urljoin(current_url, prefix)

    request_method = request.method
    request_url = request.url.replace(current_url, endpoint_url)
    request_headers = {k: v for k, v in filter(filter_exclude_headers, request.headers)}
    request_data = request.get_data()

    request_headers["user-agent"] = (
        "Ironnect/1.0 (+https://github.com/ai-tech-tw/ironnect)"
    )
    request_headers["authorization"] = f"Bearer {token}"

    proxy_response = send_request(
        method=request_method,
        url=request_url,
        headers=request_headers,
        data=request_data,
    )

    response_data = proxy_response.content
    response_status = proxy_response.status_code
    response_headers = list(proxy_response.raw.headers.items())
    response_headers.append(("x-ironnect-proxy-endpoint-url", endpoint_url))
    response_headers = filter(filter_exclude_headers, response_headers)

    return Response(response_data, response_status, response_headers)
