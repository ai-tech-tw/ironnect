from flask import current_app, request, Response
from requests import request as send_request
from urllib.parse import urljoin


def filter_exclude_headers(args: tuple) -> bool:
    key = args[0].lower()
    excluded_headers = (
        "transfer-encoding",
        "content-encoding",
        "content-length",
        "connection",
        "host",
    )
    return key not in excluded_headers


def gemini_openai_proxy(prefix: str, prefill_token: str = ""):
    current_url = urljoin(request.host_url, prefix)
    endpoint_url = current_app.config["GEMINI_OPENAI_ENDPOINT_URL"]

    request_method = request.method
    request_url = request.url.replace(current_url, endpoint_url)
    request_headers = {
        k: v for k, v in
        filter(filter_exclude_headers, request.headers)
    }
    request_data = request.get_data()

    request_headers["user-agent"] = "Ironnect/1.0 (+https://github.com/ai-tech-tw/ironnect)"
    if prefill_token:
        request_headers["authorization"] = f"Bearer {prefill_token}"

    proxy_response = send_request(
        method=request_method,
        url=request_url,
        headers=request_headers,
        data=request_data,
    )

    response_data = proxy_response.content
    response_status = proxy_response.status_code
    response_headers = filter(
        filter_exclude_headers,
        proxy_response.raw.headers.items(),
    )

    return Response(response_data, response_status, response_headers)
