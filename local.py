from functools import lru_cache
from flask import current_app, request, Response
from llama_cpp import Llama


@lru_cache()
def _fetch_inference():
    model_name = current_app.config["LOCAL_MODEL_NAME"]
    model_path = current_app.config["LOCAL_MODEL_PATH"]
    return model_name, Llama(model_path=model_path)


def openai_local():
    json_data = request.get_json()
    model_name, inference = _fetch_inference()
    result = inference.create_chat_completion(**json_data)
    return Response(result, headers={
        "x-ironnect-local-model-name": model_name,
    })
