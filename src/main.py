import extcolors, random
from action import Action
from api import *
from datetime import datetime
from deta import Deta
from fastapi import BackgroundTasks, FastAPI
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

def get_random_input() -> str:
    return random.choice(GENERATE_INPUTS)

def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{hex(r)[2:].zfill(2)}{hex(g)[2:].zfill(2)}{hex(b)[2:].zfill(2)}" #16진수 문자 0x 제거 후 0으로 채워서 6자리 헥스 코드로 변환

async def generate_new_essay():
    toked = get_random_input()
    essay = await generate_text(toked)

    if essay:
        translation = translate(essay)
        image = generate_image(translation)
        extracted, pixel_count = extcolors.extract_from_image(image)
        colors = [rgb_to_hex(color[0][0], color[0][1], color[0][2]) for color in extracted[:2]]

        db.put(data={"input": toked,
                     "body": essay[len(toked) + 1:],
                     "gradientFrom": colors[0],
                     "gradientTo": colors[1]},
               key=datetime.now(timezone("Asia/Seoul")).strftime("%Y%m%d"))
        print("Successfully generated")
    else:
        print("Error occurred during generation")

@app.post("/__space/v0/actions")
def post_actions(action: Action, background_tasks: BackgroundTasks):
    if action.event.id == "generation":
        background_tasks.add_task(generate_new_essay)

        return {"result": "Generation started"}

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