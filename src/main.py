import json, os, random, requests
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
        "top_k": 95,
        "top_p": 0.95,
        "temperature": 1.2,
        "repetition_penalty": 2.0,
        "max_length": 80,
        "do_sample": True
    },
    "options": {
        "use_cache": False,
        "wait_for_model": True
    }
}

with open("words.txt", "r", encoding="utf-8") as f:
    GENERATE_INPUTS = f.read().splitlines()

def get_random_input() -> str:
    return random.choice(GENERATE_INPUTS)

def generate(toked: str) -> Optional[str]:
    GENERATE_DATA["inputs"] = toked
    response = requests.post(GENERATE_URL, json=GENERATE_DATA, headers=GENERATE_HEADERS)

    return response.json()[0]["generated_text"] if response.status_code == 200 else None

@app.post("/__space/v0/actions")
def post_actions(action: Action):
    if action.event.id == "generate":
        toked = get_random_input()
        essay = generate(toked)

        if essay:
            db.put(data={"input": toked, "body": essay[len(toked) + 1:]}, key=datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d"))

@app.get("/essays")
def get_essays(date: Optional[str] = None, limit: int = 30):
    items = db.fetch().items

    if date:
        for item in items:
            if item["date"] == date:
                return item
    else:
        return items[::-1][:limit]

    return None

@app.get("/test-generation")
def test_generation():
    toked = get_random_input()
    essay = generate(toked)

    if essay:
        return {"input": toked, "body": essay[len(toked) + 1:], "key": datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d")}
    else:
        return None