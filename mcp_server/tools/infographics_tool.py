import os
import glob
import base64
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image as PILImage


from .qr_code_replacement_helper import replace_qr_in_placeholder_from_b64
from .qr_detection_tool import qr_detection_and_copy_tool


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


MODEL_COPYWRITER = "gpt-4.1-mini"
MODEL_DESIGNER = "gpt-4.1"
RESPONSE_ID_DIR = "prev_response"
RESPONSE_ID_FILE = os.path.join(RESPONSE_ID_DIR, "last_response_id.txt")

# PRODUCT_NAME = "NAVI"
# PRODUCT_DESC = "A digital assistant that helps users navigate MINDEF/SAF policies quickly and easily"
# UNIQUE_SELLING_POINT = "Quick search and answers to MINDEF specific policy questions"
# RECOMMENDED_STYLE = "modern, clean, and professional"

def generate_tagline(prompt, client):
    logger.info("Generating tagline...")
    response = client.responses.create(
        model=MODEL_COPYWRITER,
        input=prompt,
    )
    return json.loads(response.output_text)


def generate_infographic(prompt, client, folder="uploaded", previous_response=None):
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
    logger.info(f"file ids: {file_ids}")

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
    logger.info(f"Calling OpenAI API with args: {api_args}")
    response = client.responses.create(**api_args)
    logger.info(f"Response: {response}")

    image_data = [
        output.result
        for output in response.output
        if output.type == "image_generation_call"
    ]
    logger.info(f"Image data: {image_data}")

    if not image_data:
        print("Warning: No image data returned by the image_generation tool.")
        return response, None

    image_base64 = image_data[0]

    try:
        image_base64 = replace_qr_in_placeholder_from_b64(image_base64)
    except:
        pass

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


def generate_infographics_tool(user_prompt: str):
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("at infographics node")
    # Detect and copy QR codes from uploaded images
    qr_detection_result = qr_detection_and_copy_tool()
    logger.info(f"QR Detection: {qr_detection_result}")

    previous_response = load_previous_response(client)
    # SELECTED_TAGLINE = "Navigate Policies with NAVI – Your Smart MINDEF/SAF Assistant!"

    infographic_prompt = f"""
        You are a professional communications designer and marketing copywriter for the Ministry of Defence (MINDEF).

        Create a recommended style given from the user prompt infographics image for the internal launch of a digital tool.

        Include all images provided in the appropriate positions. If the image is a logo, it should be display it prominently at the top.
        If a QR code image is provided, include it at the bottom of the infographic with a tag e.g. "Find out more here".

        Use the following information to guide your design, but not all needs to be included if they are repeated or redundant:
        Extract Product Name, Product Description, Unique Selling Point and Tagline from the user prompt .

        Include icons at each section to visually represent the content.

        Do not include the words 'Product Name', 'Product Description', 'Unique Selling Point', or 'Tagline' in the design.
        """


    if previous_response:
        prompt_to_use = user_prompt.strip() or "Improve the infographic as appropriate."
        # prompt_to_use = user_prompt['messages']
    else:
        # first run: the full briefing
        prompt_to_use = infographic_prompt
    logger.info(f"infographic_prompt: {infographic_prompt}")
    logger.info(f"prompt_to_use: {user_prompt.strip()}")
    # prompt_to_use = """Product name: NAVI
    #                 Product description: A productivity chatbot that acts as a digital assistant to help users navigate MINDEF/SAF policies quickly and easily.
    #                 Target audience: All MINDEF and SAF personnel.
    #                 Promotion channels: Email infographics.
    #                 Campaign goals: Drive utilisation and get good feedback.
    #                 Unique selling point: Simplifies access to important policy information for MINDEF and SAF members.        
    #                 Recommended style: Professional and clear with engaging visuals.
    #                 Tagline: "Navigate Policies with NAVI – Your Smart MINDEF/SAF Assistant!"""
    # Generate infographic
    response, generated_infographics = generate_infographic(
        prompt_to_use,
        client,
        folder="uploaded",
        previous_response=previous_response,
    )
    logger.info(f"generated_infographics: {generated_infographics}")
    # logger.info(response.output_text)
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
            logger.info("Could not display image:", e)
    else:
        logger.info("No infographic generated.")
    return {'img_b64': generated_infographics}