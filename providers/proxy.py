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


OVERRIDE_SUPPORTED_API_TYPES = ("chat/completions", "completions")


def openai_proxy(provider: str, prefix: str, token: str, api_type: str = ""):
    provider_upper = provider.upper()
    endpoint_url = current_app.config.get(f"AI_PROXY_ENDPOINT_URL_{provider_upper}", "")
    if not endpoint_url:
        return f"Endpoint URL for provider {provider} is not configured.", 500
    trial_passphrase = current_app.config.get("IRONNECT_TRIAL_PASSPHRASE", "")
    prefill_token = current_app.config.get(f"AI_TRIAL_PREFILL_TOKEN_{provider_upper}")
    request_token = prefill_token if token == trial_passphrase else token

    override_json = {}
    if token == trial_passphrase and api_type.rstrip("/") in OVERRIDE_SUPPORTED_API_TYPES:
        trial_model = current_app.config.get(f"AI_TRIAL_NYMPH_MODEL_{provider_upper}")
        if trial_model:
            override_json["model"] = trial_model

    return ai_request_proxy(endpoint_url, prefix, request_token, override_json=override_json)


def ai_request_proxy(endpoint_url: str, prefix: str, token: str, override_json: dict | None = None):
    app_root = current_app.config.get("APPLICATION_ROOT")
    app_root = app_root and app_root.lstrip("/")
    prefix = prefix and prefix.lstrip("/")

    current_url = urljoin(request.host_url, app_root)
    current_url = urljoin(current_url, prefix)

    request_method = request.method
    request_url = request.url.replace(current_url, endpoint_url)
    request_headers = {k: v for k, v in filter(filter_exclude_headers, request.headers)}
    request_json = request.get_json()
    if override_json and (request_json is None or isinstance(request_json, dict)):
        request_json = (request_json or {}).copy()
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
