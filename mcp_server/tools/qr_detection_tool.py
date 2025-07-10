import os
import glob
import shutil
import logging
from openai import OpenAI
from dotenv import load_dotenv
import base64

log_file = "qr_detection.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),  # Save to file
        logging.StreamHandler(),  # Also print to console
    ],
)

logger = logging.getLogger(__name__)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_VISION = "gpt-4.1-mini"


def encode_image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def detect_qr_code_with_llm(image_path, client):
    """Use LLM to detect if image contains a QR code"""
    try:
        # Encode image to base64
        base64_image = encode_image_to_base64(image_path)

        # Create the prompt for QR detection
        prompt = """
        Look at this image and determine if it contains a QR code.
        
        A QR code is a type of 2D barcode that consists of black squares arranged in a square grid on a white background.
        QR codes typically have:
        - Square shape
        - Black and white pattern
        - Three large squares in the corners (position detection patterns)
        - Smaller squares throughout the pattern
        
        Respond with only "YES" if you see a QR code, or "NO" if you don't see a QR code.
        """

        response = client.responses.create(
            model=MODEL_VISION,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ],
        )

        result = response.output_text.strip().upper()
        return result == "YES"

    except Exception as e:
        logger.error(f"Error detecting QR code in {image_path}: {e}")
        return False


def qr_detection_and_copy_tool():
    """
    Tool to detect QR codes in uploaded images and copy them to qr_placeholder folder.
    Only works if there are images in the uploaded folder.
    """
    logger.info("Starting QR code detection and copy process...")

    # Check if uploaded folder exists and has images
    uploaded_folder = "mcp_server/tools/uploaded"
    qr_placeholder_folder = "mcp_server/tools/qr_placeholder"

    if not os.path.exists(uploaded_folder):
        logger.info("Uploaded folder does not exist.")
        return "No uploaded folder found."

    # Get all image files in uploaded folder
    image_paths = glob.glob(f"{uploaded_folder}/*.[pj][pn]g")

    if not image_paths:
        logger.info("No images found in uploaded folder.")
        return "No images found in uploaded folder."

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Ensure qr_placeholder folder exists
    os.makedirs(qr_placeholder_folder, exist_ok=True)

    qr_images_found = []

    for image_path in image_paths:
        logger.info(f"Analyzing image: {image_path}")

        # Detect if image contains QR code
        is_qr_code = detect_qr_code_with_llm(image_path, client)

        if is_qr_code:
            # Copy to qr_placeholder folder
            filename = os.path.basename(image_path)
            destination_path = os.path.join(qr_placeholder_folder, filename)

            try:
                shutil.copy2(image_path, destination_path)
                qr_images_found.append(filename)
                logger.info(f"QR code image copied: {filename}")
            except Exception as e:
                logger.error(f"Error copying {filename}: {e}")

    if qr_images_found:
        return f"QR code detection complete. Found and copied {len(qr_images_found)} QR code image(s): {', '.join(qr_images_found)}"
    else:
        return "No QR codes detected in uploaded images."


if __name__ == "__main__":
    result = qr_detection_and_copy_tool()
    print(result)
