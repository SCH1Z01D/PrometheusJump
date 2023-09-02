from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from dotenv import dotenv_values
import ai21
import gpt4all
import requests
import base64
import os

config = dotenv_values(".env")
api_host = config["API_HOST"]
api_key = config["API_KEY"]
engine_id = config["ENGINE_ID"]
app = Flask(__name__)
CORS(app)

# the api key for ai21 is:
ai21.api_key = "<API_KEY>"


@app.route("/generate", methods=["GET"])
def generate():
    response = ai21.Completion.execute(
        model="j1-large",
        temperature= 0.65,
        minTokens=4,
        maxTokens=32,
        numResults=1
    )


# Calls the Stable Diffusion API and generates an image for a product name
def generate_image(product_name):
    prompt = "Please generate a featured image for the following product idea: " + product_name + \
        ". The product must be showcased in full size at the center of the image, with minimum distractive elements, and a simple monochromatic background."
    url = f"{api_host}/v1/generation/{engine_id}/text-to-image"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
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