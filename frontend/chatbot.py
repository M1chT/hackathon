## backend codes
import io
import base64
from PIL import Image

# convert image to base64
def image_to_base64(uploaded_files):
    # uploaded_files is a list of UploadedFile objects from Streamlit
    base64_list = []
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        base64_list.append(img_str)
    return base64_list

# Simple rule-based chatbot logic
def chatbot_response(user_input):
    """
    Parameter:
        user_input: {
        'text': user query in text format,
        'img': user's uploaded img}

    Output:
        response: {
        'text': text response, 
        'base64': img in base64}
    """
    query = user_input['text'].lower()
    response = {"trigger": False, "text": "", "base64": None}

    if "hello" in query or "hi" in query:
        response['text'] = "Hello! How can I help you today?"
        response['base64'] = None
        return response
    elif "how are you" in query:
        response['text'] = "I'm just a bot, but I'm doing great! Thanks for asking."
        response['base64'] = None
        return response
    elif "bye" in query:
        response['text'] = "Goodbye! Have a great day."
        response['base64'] = None
        return response
    elif "trigger" in query:
        response['text'] = None
        response['base64'] = None
        response['trigger'] = True
        return response
    elif "accept" in query:
        response['text'] = "tool triggered"
        response['base64'] = None
        response['trigger'] = False
        return response
    elif "rewrite" in query:
        response['text'] = "ok got your rewritten stuff"
        response['base64'] = None
        response['trigger'] = False
        return response
    elif "reject" in query:
        response['text'] = "ok you asked me not to execute"
        response['base64'] = None
    elif "more images" in query:
        response['text'] = "I hope the generated image fits your needs"
        response['base64'] = image_to_base64(["./images/31941-Christmas-New-Year-snow-winter-snowman-4K.jpg", "./images/790317-snowman-snow-xmas-christmas-figure-cinnamon-4K.jpg"])
        return response
    elif "three options" in query:
        response['text'] = "I hope the generated image fits your needs"
        response['base64'] = image_to_base64(["./images/31941-Christmas-New-Year-snow-winter-snowman-4K.jpg", "./images/790317-snowman-snow-xmas-christmas-figure-cinnamon-4K.jpg", "./images/snow_covered_road_and_trees_in_winter_4k_hd_nature-1920x1080.jpg"])
        return response
    elif "generate" in query:
        response['text'] = "I hope the generated image fits your needs"
        response['base64'] = image_to_base64(["./images/31941-Christmas-New-Year-snow-winter-snowman-4K.jpg"])
        return response
    else:
        response['text'] = "I'm not sure how to respond to that. Can you rephrase?"
        response['base64'] = None
        return response

## initialise conversation
def initialise_conversation():
    """
    Initialise the conversation history with system and assistant messages.

    Returns:
    - list: Initialised conversation history.
    """
    assistant_message = "Hello! I am your marketing guru. How can I assist you with your product today?"

    # lol this serves as a prompt
    conversation_history = [
        {"role": "system", "content": "You are Streamly, a specialized AI assistant trained in Streamlit."},
        {"role": "system", "content": "Streamly, is powered by the OpenAI GPT-4o-mini model, released on July 18, 2024."},
        {"role": "system", "content": "You are trained up to Streamlit Version 1.36.0, release on June 20, 2024."},
        {"role": "system", "content": "Refer to conversation history to provide context to your response."},
        {"role": "system", "content": "You were created by Madie Laine, an OpenAI Researcher."},
        {"role": "assistant", "content": assistant_message}
    ]
    return conversation_history