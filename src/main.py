import os, random, re, requests
from action import Action
from datetime import datetime
from deta import Deta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pytz import timezone
from typing import Optional

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Deta().Base("essays")

GENERATE_URL = "https://api-inference.huggingface.co/models/daveripper0020/essaygpt2"

GENERATE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['HUGGINGFACE_TOKEN']}"
}

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

def get_random_input() -> str:
    return random.choice(GENERATE_INPUTS)

def generate(toked: str) -> Optional[str]:
    GENERATE_DATA["inputs"] = toked
    response = requests.post(GENERATE_URL, json=GENERATE_DATA, headers=GENERATE_HEADERS)

    if response.status_code == 200:
        essay = response.json()[0]["generated_text"]
        return "".join(re.split(r"((?:[.]|[?]|!){1}\s?)", essay)[:-1]).strip()
    else:
        return None

@app.post("/__space/v0/actions")
def post_actions(action: Action):
    if action.event.id == "pregeneration":
        requests.post(GENERATE_URL, headers=GENERATE_HEADERS)
        print("Loading a model");
    elif action.event.id == "generation":
        toked = get_random_input()
        essay = generate(toked)

        if essay:
            db.put(data={"input": toked, "body": essay[len(toked) + 1:]}, key=datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d"))
            print("Successfully generated")

@app.get("/essays")
def get_essays(date: Optional[str] = None, limit: int = 30):
    items = next(db.fetch())

    if date:
        for item in items:
            if item["key"] == date:
                return item
    else:
        return items[::-1][:limit]

    return None

@app.get("/regenerate-essay")
def regenerate_essay(date: str):
    toked = get_random_input()
    essay = generate(toked)
    db.update({"input": toked, "body": essay[len(toked) + 1]}, date)