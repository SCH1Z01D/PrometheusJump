from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import dotenv_values
import requests
import base64
import os
import ai21


api_host = os.environ["API_HOST"] = "https://api.stability.ai"
stable_diffusionAPI = os.environ["STABE_DIFFUSION_API_KEY"] = "sk--Z88fszDULuXpRVaIzRXbOe5Zxxxxxxxxxxxxxxxxxxxxx"
engine_id = os.environ["ENGINE_ID"] = "stable-diffusion-xl-beta-v2-2-2"
ai21_key = os.environ["AI21_API_KEY"] = "TiAD0exxxxxxxxxx"

app = Flask(__name__)

CORS(app)
    
@app.route("/generate", methods=["GET"])
def generate():
    ai21.api_key = ai21_key
    # We create 2 prompts, one for the description and then another one for the name of the product
    prompt_description = 'You want to create a new and refreshing comic : "' + \
            request.args.get(
                "prompt") + '"'
    description = ai21.Completion.execute(
            model="j2-mid",
            prompt=prompt_description,
            numResults=1,
            maxTokens=64,
            temperature=0.84,
            topKReturn=0,
            topP=1,
            countPenalty={
                "scale":0,
                "applyToNumbers": False,
                "applyToPunctuations": False,
                "applyToStopwords": False,
                "applyToWhitespaces": False,
                "applyToEmojis": False
        },
        frequencyPenalty={
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        presencePenalty={
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        stopSequences=["##"]
    )
    response = description['completions'][0]['data']['text']   

    prompt_name = 'Please write a name with a maximum of 5 words for the comic that you want to create: "' +  response 
    name = ai21.Completion.execute(
        model="j2-mid",
        prompt=prompt_name, 
        numResults=1,
        maxTokens=64,
        temperature=0.84,
        topKReturn=0,
        topP=1,
        countPenalty={
            "scale":0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        frequencyPenalty={
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        presencePenalty={
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        stopSequences=["##"]
    )
    image_path = generate_image(name)
    result = {"name": name, "description": description, }

    return jsonify(result)


# Calls the Stable Diffusion API and generates an image for a product name
def generate_image(product_name):
    prompt = "Please generate a featured image for the following product idea: " + product_name + \
        ". The product must be showcased in full size at the center of the image, with minimum distractive elements, and a simple monochromatic background."
    url = f"{api_host}/v1/generation/{engine_id}/text-to-image"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {stable_diffusionAPI}"
    }
    payload = {}
    payload['text_prompts'] = [{"text": f"{prompt}"}]
    payload['cfg_scale'] = 7
    payload['clip_guidance_preset'] = 'FAST_BLUE'
    payload['height'] = 512
    payload['width'] = 512
    payload['samples'] = 1
    payload['steps'] = 50

    response = requests.post(url, headers=headers, json=payload)
    filename = check_and_create_filename(product_name.replace(" ", "_")+".png")
    image_path = ""

    # Processing the response
    if response.status_code == 200:
        data = response.json()
        for i, image in enumerate(data["artifacts"]):
            with open(f"{filename}", "wb") as f:
                f.write(base64.b64decode(image["base64"]))
                image_path = os.path.realpath(filename)

    return image_path

# Creates a new filename in case it already exists
def check_and_create_filename(filename):
    base_name, extension = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    while os.path.exists(new_filename):
        new_filename = f"{base_name}_{counter}{extension}"
        counter += 1

    return new_filename

# Start an http server and expose the api endpoint
def main():
    app.run(host="localhost", port=8000)
    print("Server running on  port 8000")


if __name__ == "__main__":
    main()
