import asyncio, io, re, requests, os
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as diffusion
from stability_sdk import client
from typing import Optional
from PIL import Image
from const import *

async def generate_text(toked: str) -> Optional[str]:
    GENERATE_DATA["inputs"] = f"{GENERATE_PROMPT}{toked}"
    response = requests.post(GENERATE_URL, json=GENERATE_DATA, headers=GENERATE_HEADERS)

    if response.status_code == 503:
        time = float(response.json()["estimated_time"])
        print("Loading model")
        await asyncio.sleep(time + GENERATE_EXTRA_WAIT_TIME)

        response = requests.post(GENERATE_URL, json=GENERATE_DATA, headers=GENERATE_HEADERS)

    if response.status_code == 200:
        essay = response.json()[0]["generated_text"][len(GENERATE_PROMPT):]
        splitted = re.split(r"((?:[.]|[?]|!){1}\s?)", essay)
        print("Text generation done")

        return splitted[0].strip() if len(splitted) == 1 else "".join(splitted[:-1]).strip()
    else:
        return None
    
def translate(text: str) -> Optional[str]:
    url = f"{PAPAGO_URL}?source=ko&target=en&text={text}"
    response = requests.post(url, headers=PAPAGO_HEADERS);

    if response.status_code == 200:
        print("Translation done")

        return response.json()["message"]["result"]["translatedText"]
    else:
        return None

def generate_image(text: str) -> Image:
    model = client.StabilityInference(key=STABILITY_KEY, engine=STABILITY_ENGINE)
    answers = model.generate(prompt=text)

    for response in answers:
        for artifact in response.artifacts:
            if artifact.finish_reason == diffusion.FILTER:
                print("Diffusion Inference request activated safety filter, fallback colors are used")
                # TODO: Fallback colors
            elif artifact.type == diffusion.ARTIFACT_IMAGE:
                print("Text-to-Image generation done")

                return Image.open(io.BytesIO(artifact.binary))

    return None