import os

GENERATE_URL = "https://api-inference.huggingface.co/models/daveripper0020/essaygpt2"
GENERATE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['HUGGINGFACE_TOKEN']}"
}
GENERATE_PROMPT = os.environ["GENERATION_PROMPT"]
GENERATE_EXTRA_WAIT_TIME = int(os.environ["GENERATION_EXTRA_WAIT_TIME"])
GENERATE_DATA = {
    "inputs": "",
    "parameters": {
        "top_k": int(os.environ["GENERATION_TOP_K"]),
        "top_p": float(os.environ["GENERATION_TOP_P"]),
        "temperature": float(os.environ["GENERATION_TEMPERATURE"]),
        "repetition_penalty": float(os.environ["GENERATION_REPETITION_PENALTY"]),
        "max_length": int(os.environ["GENERATION_MAX_LENGTH"]),
        "do_sample": True
    },
    "options": {
        "use_cache": False
    }
}

with open("words.txt", "r", encoding="utf-8") as f:
    GENERATE_INPUTS = f.read().splitlines()

PAPAGO_URL = "https://openapi.naver.com/v1/papago/n2mt"
PAPAGO_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Naver-Client-Id": os.environ["PAPAGO_CLIENT_ID"],
    "X-Naver-Client-Secret": os.environ["PAPAGO_CLIENT_SECRET"]
}

STABILITY_KEY = os.environ["STABILITY_KEY"]
STABILITY_ENGINE = os.environ["STABILITY_ENGINE"]

PALETTE_COLORS = int(os.environ["PALETTE_COLORS"])