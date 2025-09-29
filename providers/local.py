from functools import lru_cache
from flask import current_app, request, jsonify
from llama_cpp import Llama


@lru_cache()
def _fetch_inference():
    model_path = current_app.config.get("LOCAL_MODEL_PATH", "")
    if not model_path:
        raise ValueError("Local model path is not configured.")
    return Llama(model_path=model_path)


def openai_local_iron(token: str = "", override_json: dict = None):
    if token != current_app.config["IRONNECT_TRIAL_PASSPHRASE"]:
        return "Invalid token for the model.", 403

    json_data = request.get_json()
    if override_json:
        json_data.update(override_json)
    inference = _fetch_inference()

    return inference.create_chat_completion(**json_data)
