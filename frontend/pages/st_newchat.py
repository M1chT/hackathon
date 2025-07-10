import streamlit as st
import requests
from PIL import Image

# Initialize chat history for session state
if "history" not in st.session_state:
    st.session_state["history"] = []

# backend codes
from chatbot import chatbot_response, initialise_conversation

## update chatbot response in session history
def on_chat_submit(chat_input):
    """
    Handle chat input submissions and interact with the OpenAI API.

    Parameters:
    - chat_input (str): The chat input from the user.

    Returns:
    - None: Updates the chat history in Streamlit's session state.
    """
    API_URL = "http://127.0.0.1:8000/send_query"
    user_input = chat_input.strip().lower()

    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = initialise_conversation()

    st.session_state.conversation_history.append({"role": "user", "content": user_input})



    payload = {
            "type": "text",
            "messages": [user_input]    
    }

    
    response = requests.post(
        API_URL,  # or your deployed FastAPI URL
        json=payload
    )
    if response.status_code == 200:
        # assistant_reply = response.json()["messages"][1]["content"]
        assistant_reply = response.json() 
    else:
        print(f"Error: {response.status_code} - {response.text}")
        assistant_reply = "Sorry, I couldn't process your request at the moment."

    # response = chatbot_response(user_input)
    # assistant_reply = response

    st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})

    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": assistant_reply})

def save_feedback(index):
    st.session_state.history[index]["feedback"] = st.session_state[f"feedback_{index}"]

def handle_file_upload(uploaded_file):
    """Handle file upload and save to uploaded folder"""
    try:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            
            # Create uploaded directory if it doesn't exist
            import os
            # Use the hackathon directory as the base path (go up 2 levels from frontend/pages)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            uploaded_dir = os.path.join(base_dir, "mcp_server", "tools", "uploaded")
            
            os.makedirs(uploaded_dir, exist_ok=True)
            
            # Save the uploaded file to the uploaded folder
            file_path = os.path.join(uploaded_dir, uploaded_file.name)
            image.save(file_path)
            
            return True, file_path, image
        return False, None, None
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return False, None, None

# ## display image as base64 content to embed using img or CSS tags
# def img_to_base64(image_path):
#     """Convert image to base64."""
#     try:
#         with open(image_path, "rb") as img_file:
#             return base64.b64encode(img_file.read()).decode()
#     except Exception as e:
#         print(f"Error converting image to base64: {str(e)}")
#         return None
    
# ## for streaming of chat convo
# def chat_stream(response):
#     for char in response:
#         yield char
#         time.sleep(0.02)

## css format
css = '''
<style>
    /* Make the file uploader button fully transparent */
    [data-testid='stFileUploader'] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        position: relative !important;
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        min-height: 48px !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid='stFileUploader'] * {
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        text-shadow: none !important;
    }
    [data-testid='stFileUploader'] section > div,
    [data-testid='stFileUploader'] section > span,
    [data-testid='stFileUploader'] section > input + div,
    [data-testid='stFileUploader'] section > * {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }
    /* Add cloud upload icon (cloud with upward arrow) */
    [data-testid='stFileUploader']::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 36px;
        height: 36px;
        transform: translate(-50%, -50%);
        background-image: url('data:image/svg+xml;utf8,<svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M27 28a5 5 0 0 0 0-10c-.36 0-.71.04-1.05.1A9 9 0 0 0 9 15a7 7 0 0 0 0 14h18z" stroke="grey" stroke-width="2" fill="none"/><path d="M18 24V16" stroke="grey" stroke-width="2" stroke-linecap="round"/><path d="M15 19l3-3 3 3" stroke="grey" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>');
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        pointer-events: none;
        z-index: 10;
        opacity: 1;
    }
    /* Vertically center the file uploader in its column */
    [data-testid="stVerticalBlock"] > div:first-child {
        display: flex !important;
        align-items: center !important;
        height: 100%;
        justify-content: center;
    }
    /* Adjust chat input margin for alignment */
    [data-testid="stChatInput"] {
        margin-left: 8px !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    /* Make chat input box a comfortable single line height */
    [data-testid="stChatInput"] textarea {
        min-height: 32px !important;
        max-height: 32px !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

'''



####################################################################################
# Streamlit app UI - NEW CHAT PAGE
####################################################################################
st.set_page_config(page_title="New Chat", page_icon="💬", layout="centered")

st.markdown(css, unsafe_allow_html=True)
st.header("Discover your marketing strategy ✨")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Move input bar to bottom
col1, col2 = st.columns([1, 20], gap="small")
with col1:
    files = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed", accept_multiple_files=True)
with col2:
    user_input = st.chat_input("Hello! How can I assist you today?")

# Save images if there are any
if files:
    uploaded_files = []
    uploaded_images = []
    
    for file in files:
        success, file_path, image = handle_file_upload(file)
        
        if success:
            uploaded_files.append(file.name)
            uploaded_images.append((image, file.name))
    
    # Show success message for all uploaded files
    if uploaded_files:
        if len(uploaded_files) == 1:
            st.success(f"File '{uploaded_files[0]}' uploaded successfully to uploaded folder!")
        else:
            files_list = ", ".join([f"'{name}'" for name in uploaded_files])
            st.success(f"Files {files_list} uploaded successfully to uploaded folder!")
        
        # Display all uploaded images
        for image, filename in uploaded_images:
            st.image(image, caption=f"Uploaded: {filename}", use_container_width=True)

if user_input:
    user_input = user_input
    on_chat_submit(user_input)

## Display chat conversations + feedback
for i, message in enumerate(st.session_state.history):
    avatar_image = "./frontend/images/guru2.jpg" if message["role"] == "assistant" else "./frontend/images/user.png" if message["role"] == "user" else None
    with st.chat_message(message["role"], avatar=avatar_image):
        st.write(message["content"])
        # st.write_stream(chat_stream(message["content"]))
        if message["role"] == "assistant":
            feedback = message.get("feedback", None)
            st.session_state[f"feedback_{i}"] = feedback
            st.feedback(
                "thumbs",
                key=f"feedback_{i}",
                disabled=feedback is not None,
                on_change=save_feedback,
                args=(i,),
            )
