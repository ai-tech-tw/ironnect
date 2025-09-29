from functools import lru_cache
from flask import current_app, request, jsonify
from llama_cpp import Llama


@lru_cache()
def _fetch_inference():
    model_path = current_app.config.get("LOCAL_MODEL_PATH", "")
    if not model_path:
        raise ValueError("Local model path is not configured.")
    return Llama(model_path=model_path)


def openai_local_iron(token: str = ""):
    if token != current_app.config["IRONNECT_TRIAL_PASSPHRASE"]:
        return "Invalid token for the model.", 403

    model_name = current_app.config.get("LOCAL_MODEL_NAME", "")
    if not model_name:
        return "Model is not configured.", 500

    json_data = request.get_json()
    inference = _fetch_inference()

    result = inference.create_chat_completion(**json_data)

    response = jsonify(result)
    response.headers.add_header("x-ironnect-model-name", model_name)

    return response
