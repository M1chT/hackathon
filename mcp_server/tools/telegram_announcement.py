import os
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


MODEL_COPYWRITER = "gpt-4.1-mini"
RESPONSE_ID_DIR = "prev_response"
RESPONSE_ID_FILE = os.path.join(RESPONSE_ID_DIR, "last_response_id.txt")


# # Product info. SHOULD BE FROM UPSTREAM
# PRODUCT_NAME = "NAVI"
# PRODUCT_DESC = "A digital assistant that helps users navigate MINDEF/SAF policies quickly and easily"
# UNIQUE_SELLING_POINT = "Quick search and answers to MINDEF specific policy questions"


def generate_telegram_text(prompt, client, previous_response=None):
    logger.info("Generating telegram text...")

    api_args = {
        "model": MODEL_COPYWRITER,
        "input": [
            {"role": "user", "content": [{"type": "input_text", "text": prompt}]}
        ],
    }

    if previous_response:
        api_args["previous_response_id"] = previous_response.id

    response = client.responses.create(**api_args)

    return response, response.output_text


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


def gen_telegram_announcement_tool(user_prompt):
    client = OpenAI(api_key=OPENAI_API_KEY)

    telegram_text_prompt = """
    You are a professional copywriter for official Telegram posts by MINDEF/SAF.

    Write a short, energetic announcement post in this format:

    1. A single emoji (or emoji cluster) followed by the event or product name, then a bold, inspiring headline. 
    Example:
    💪🏼 SAF Day: Celebrating 60 Years of Strength!

    2. A brief, engaging paragraph (2–3 sentences max) that explains the occasion or product in a relatable and uplifting tone.

    3. End with a positive invitation or call to action. Use inclusive language like “join us,” “find out more,” or “be part of it.”

    Guidelines:
    - Keep the tone proud, professional, and inspiring.
    - Use Telegram Markdown formatting (e.g. *bold*, _italic_) where appropriate.
    - Output only the message (no quotes, no JSON)

    Use the following information to guide your design, but not all needs to be included if they are repeated or redundant:
    Extract Product Name, Product Description, and Unique Selling Point from the user prompt.
    """

    previous_response = load_previous_response(client)

    if previous_response:
        prompt_to_use = (
            user_prompt.strip() or "Improve the announcement as appropriate."
        )
    else:
        # first run: the full briefing
        prompt_to_use = telegram_text_prompt

    # Generate infographic
    response, telegram_post = generate_telegram_text(
        prompt_to_use,
        client,
        previous_response=previous_response,
    )

    print(telegram_post)

    # Save response ID for future follow-up
    # TODO: prev_response FOLDER NEEDS TO BE CLEARED FOR NEW SESSION
    if response:
        save_response_id(response)
    return telegram_post
