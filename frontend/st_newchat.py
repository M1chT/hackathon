import streamlit as st
import io
import base64
from PIL import Image

from chatbot import chatbot_response

## functions
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

def base64_to_image(base64_input):
    # Accepts either a string or a list of strings
    if isinstance(base64_input, list):
        images = []
        for base64_str in base64_input:
            img_data = base64.b64decode(base64_str)
            image = Image.open(io.BytesIO(img_data))
            images.append(image)
        return images
    else:
        img_data = base64.b64decode(base64_input)
        image = Image.open(io.BytesIO(img_data))
        return [image]  # Always return a list

####################################################################################
# new chat page UI
####################################################################################

st.title("Discover Your Marketing Strategy")

# Initialise chat history
if "convo_history" not in st.session_state:
    st.session_state.convo_history = []
if "awaiting_user" not in st.session_state:
    st.session_state.awaiting_user = False
if "last_response" not in st.session_state:
    st.session_state.last_response = None

# Display chat messages from history on app rerun
for convo in st.session_state.convo_history:
    with st.chat_message(convo["role"]):
        st.markdown(convo["content"])
        if convo['image']:
            images = base64_to_image(convo["image"])
            if len(images) == 1:
                st.image(images[0], caption="Generated Image", use_container_width=True)
            else:
                for i in range(0, len(images), 2):
                    cols = st.columns(2)
                    for j, each_img in enumerate(images[i:i+2]):
                        cols[j].image(each_img, caption=f"Generated Image {i + j + 1}", use_container_width=True)


# Main user input
if user_input := st.chat_input(
    "Say something and/or attach an image",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
):
    img_base64 = image_to_base64(user_input["files"])
    user_input["base64"] = img_base64
    st.chat_message("user").markdown(user_input["text"])
    st.session_state.convo_history.append({"role": "user", "content": user_input['text'], "image": user_input['base64']})

    response = chatbot_response(user_input)
    st.session_state.last_response = response

    if response.get('trigger', False):
        st.session_state.awaiting_user = True
    else:
        st.session_state.awaiting_user = False

# Tool trigger loop (one input per rerun)
if st.session_state.awaiting_user:
    with st.chat_message("assistant"):
        second_input = st.chat_input("<name of tool> will be triggered. To continue, type 'accept', else 'reject', or rewrite your query")
    if second_input:
        # display the updated input
        st.session_state.convo_history.append({"role": "user", "content": second_input, "image": None})
        with st.chat_message("user"):
            st.markdown(second_input)
            # get the response
            response = chatbot_response({'text': second_input, 'img': None})
            st.session_state.last_response = response
            if response.get('trigger', False):
                st.session_state.awaiting_user = True
            else:
                st.session_state.awaiting_user = False
        st.rerun()

# Display the last response if available and not awaiting further input
if st.session_state.last_response and not st.session_state.awaiting_user:
    response = st.session_state.last_response
    with st.chat_message("assistant"):
        st.markdown(response['text'])
        if response['base64']:
            images = base64_to_image(response["base64"])
            if len(images) == 1:
                st.image(images[0], caption="Generated Image", use_container_width=True)
            else:
                for i in range(0, len(images), 2):
                    cols = st.columns(2)
                    for j, each_img in enumerate(images[i:i+2]):
                        cols[j].image(each_img, caption=f"Generated Image {i + j + 1}", use_container_width=True)
    st.session_state.convo_history.append({"role": "assistant", "content": response['text'], "image": response["base64"]})
    st.session_state.last_response = None  # Reset after displaying


