import io, re, requests
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as diffusion
from stability_sdk import client
from typing import Optional
from PIL import Image
from const import *

def warm_up_model():
    requests.post(GENERATE_URL, headers=GENERATE_HEADERS)

def generate_text(toked: str) -> Optional[str]:
    GENERATE_DATA["inputs"] = f"{GENERATE_PROMPT}{toked}"
    response = requests.post(GENERATE_URL, json=GENERATE_DATA, headers=GENERATE_HEADERS)

    if response.status_code == 200:
        essay = response.json()[0]["generated_text"][len(GENERATE_PROMPT):]
        splitted = re.split(r"((?:[.]|[?]|!){1}\s?)", essay)

        return splitted[0].strip() if len(splitted) == 1 else "".join(splitted[:-1]).strip()
    else:
        return None
    
def translate(text: str) -> Optional[str]:
    url = f"{PAPAGO_URL}?source=ko&target=en&text={text}"
    response = requests.post(url, headers=PAPAGO_HEADERS);

    return response.json()["message"]["result"]["translatedText"] if response.status_code == 200 else None

def generate_image(text: str) -> Image:
    model = client.StabilityInference(key=STABILITY_KEY, engine=STABILITY_ENGINE)
    answers = model.generate(prompt=text)

    for response in answers:
        for artifact in response.artifacts:
            if artifact.finish_reason == diffusion.FILTER:
                return None
            elif artifact.type == diffusion.ARTIFACT_IMAGE:
                return Image.open(io.BytesIO(artifact.binary))

    return None