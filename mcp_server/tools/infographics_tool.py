import os
import glob
import base64
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image as PILImage


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


MODEL_COPYWRITER = "gpt-4.1-mini"
MODEL_DESIGNER = "gpt-4.1"
RESPONSE_ID_DIR = "prev_response"
RESPONSE_ID_FILE = os.path.join(RESPONSE_ID_DIR, "last_response_id.txt")


def generate_tagline(prompt, client):
    logger.info("Generating tagline...")
    response = client.responses.create(
        model=MODEL_COPYWRITER,
        input=prompt,
    )
    return json.loads(response.output_text)


def generate_infographic(
    prompt, client, folder="uploaded", previous_response=None
):
    logger.info("Generating infographics...")
    # 1. Find and upload all images in the folder (if any)
    file_ids = []
    upload_folder = f"mcp_server/tools/{folder}"
    if os.path.exists(upload_folder):
        image_paths = glob.glob(f"{upload_folder}/*.[pj][pn]g")
        for path in image_paths:
            with open(path, "rb") as img_file:
                file_response = client.files.create(file=img_file, purpose="vision")
                file_ids.append(file_response.id)
    print(file_ids)
    # 2. Build the content list
    content = [{"type": "input_text", "text": prompt}]
    for file_id in file_ids:
        content.append({"type": "input_image", "file_id": file_id})

    # 3. Prepare API call
    api_args = {
        "model": MODEL_DESIGNER,
        "tools": [{"type": "image_generation"}],
    }
    if previous_response is not None:
        api_args["previous_response_id"] = previous_response.id

    api_args["input"] = [{"role": "user", "content": content}]

    # 4. Call the API
    response = client.responses.create(**api_args)

    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]

    if not image_data:
        print("Warning: No image data returned by the image_generation tool.")
        return response.output_text, None

    image_base64 = image_data[0]
    with open("infographic.png", "wb") as f:
        f.write(base64.b64decode(image_base64))

    return response, image_base64


def save_response_id(response):
    """Save the response ID to a file for future follow-up."""
    os.makedirs(RESPONSE_ID_DIR, exist_ok=True)
    with open(RESPONSE_ID_FILE, "w") as f:
        f.write(response.id)


def load_previous_response(client):
    """Load the previous response object using the saved response ID."""
    if os.path.exists(RESPONSE_ID_FILE):
        with open(RESPONSE_ID_FILE, "r") as f:
            response_id = f.read().strip()
        if response_id:
            return client.responses.retrieve(response_id)
    return None


def generate_infographics_tool(user_prompt):
    client = OpenAI(api_key=OPENAI_API_KEY)
    print(os.getcwd())
    print("hi")
    previous_response = load_previous_response(client)

    if previous_response:
        # Follow-up: ask user for changes, use previous_response. If not, it improves the infographics by itself.
        user_prompt = input(
            "What changes would you like to make to this infographic? "
            "You can upload new images too.\n"
            "↵ Press Enter to auto-improve: "
        ).strip()
        if user_prompt:
            prompt_to_use = user_prompt
        else:
            prompt_to_use = "Improve the infographic as appropriate."
    else:
        # First run: generate tagline and full prompt
        tagline_prompt = f"""
        You are a professional creative copywriter.

        Based on the following inputs, generate 3 short, clear, catchy taglines (each under 8 words)
        that could be used in marketing materials for a MINDEF/SAF digital tool.

        Respond only with a JSON array of strings, like:
        ["Tagline 1", "Tagline 2", "Tagline 3"]

        Extract Product Name, Product Description, and Unique Selling Point from the user prompt.
        """
        tagline_response = generate_tagline(tagline_prompt, client)
        SELECTED_TAGLINE = tagline_response[0]

        infographic_prompt = f"""
        You are a professional communications designer and marketing copywriter for the Ministry of Defence (MINDEF).

        Create a recommended style given from the user prompt infographics image for the internal launch of a digital tool.

        Include all images provided in the appropriate positions. If the image is a logo, it should be display it prominently at the top.
        If a QR code image is provided, include it at the bottom of the infographic with a tag e.g. "Find out more here".

        Use the following information to guide your design, but not all needs to be included if they are repeated, irrelevant or redundant:
        Extract Product Name, Product Description, and Unique Selling Point from the user prompt .
        Tagline: "{SELECTED_TAGLINE}"

        Include icons at each section to visually represent the content.

        Do not include the words 'Product Name', 'Product Description', 'Unique Selling Point', or 'Tagline' in the design.
        """
        prompt_to_use = infographic_prompt

        # Generate infographic
        response, generated_infographics = generate_infographic(
            prompt_to_use,
            client,
            folder="uploaded",
            previous_response=previous_response,
        )
        print(response.output_text)
        # Save response ID for future follow-up
        # TODO: prev_response FOLDER NEEDS TO BE CLEARED FOR NEW SESSION
        if response:
            save_response_id(response)

        # Display the image (optional, for local testing)
        if generated_infographics:
            try:
                img = PILImage.open("infographic.png")
                img.show()
            except Exception as e:
                print("Could not display image:", e)
        else:
            print("No infographic generated.")