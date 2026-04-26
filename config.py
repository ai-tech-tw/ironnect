AI_PROXY_PROVIDERS = ["cerebras"]
AI_PROXY_ALLOWED_PATHS = [
    "chat/completions",
    "completions",
    "embeddings",
    "models"
]

AI_PROXY_ENDPOINT_URL_CEREBRAS = "https://api.cerebras.ai/v1"
AI_TRIAL_PREFILL_TOKEN_CEREBRAS = "your_cerebras_token_here"
AI_TRIAL_NYMPH_MODEL_CEREBRAS = "gpt-oss-120b"

AI_LOCAL_MODEL_PATH_IRON = "models/gemma-3-270m-it-Q4_K_M.gguf"
AI_TRIAL_NYMPH_MODEL_IRON = "gemma-3-270m"
