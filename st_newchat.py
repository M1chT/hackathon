import streamlit as st
import io
import base64
from PIL import Image
from st_copy import copy_button

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

def get_gif_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

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
            print(file_path)
            image.save(file_path)
            
            return True, file_path, image
        return False, None, None
    except Exception as e:
        st.error(f"Error uploading file: {str(e)}")
        return False, None, None

####################################################################################
# new chat page UI
####################################################################################

st.title("Discover Your Marketing Strategy")
st.markdown("""
    <style> 
    .stChatInputContainer > div {
    background-color: #FFA500;
    }
    </style>
    """, unsafe_allow_html=True)

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
        col1, col2 = st.columns([10, 1], gap="small")
        with col1:
            st.markdown(convo["content"])
        with col2:
            if convo["role"] == "assistant":
                with col2:
                    copy_button(convo["content"],
                            tooltip="copy",
                            copied_label="copied!",
                            icon="st",
                        )
        if convo['image'] and convo["role"] == "assistant":
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
    accept_file="multiple",
    file_type=["jpg", "jpeg", "png"],
  #  disabled=st.session_state.awaiting_user,
):
    
    img_base64 = image_to_base64(user_input["files"])
    user_input["base64"] = img_base64
    
    # Create display text with file names
    if user_input["files"]:
        file_names = [getattr(file, 'name', str(file)) for file in user_input["files"]]
        display_text = str(user_input["text"]) + f"\n\n**🔗 Uploaded files:** {'; '.join(file_names)}"

        # Save images if there are any
        uploaded_files = []
        uploaded_images = []
        
        for file in user_input["files"]:
            success, file_path, image = handle_file_upload(file)
            
            if success:
                uploaded_files.append(getattr(file, 'name', str(file)))
                uploaded_images.append((image, getattr(file, 'name', str(file))))
        
        # Show success message for all uploaded files
        if uploaded_files:
            if len(uploaded_files) == 1:
                st.success(f"File '{uploaded_files[0]}' uploaded successfully to uploaded folder!")
            else:
                files_list = ", ".join([f"'{name}'" for name in uploaded_files])
                st.success(f"Files {files_list} uploaded successfully to uploaded folder!")
    else:
        display_text = user_input["text"]
    
    st.chat_message("user").markdown(display_text)

    st.session_state.convo_history.append({"role": "user", "content": display_text, "image": user_input['base64']})

    with st.chat_message("assistant"):
        spinner_gif_path = "images/spinner.gif"  # Make sure this file exists
        spinner_gif_base64 = get_gif_base64(spinner_gif_path)
        spinner_html = f'<img src="data:image/gif;base64,{spinner_gif_base64}" width="36" style="vertical-align:middle;">'
        placeholder = st.empty()
        placeholder.markdown(spinner_html, unsafe_allow_html=True)
    
    # with st.spinner("Generating response..."):
        response = chatbot_response(user_input)

        st.session_state.last_response = response

        if response and response.get('trigger', False):
            st.session_state.awaiting_user = True
        else:
            st.session_state.awaiting_user = False

# Tool trigger loop (one input per rerun)
if st.session_state.awaiting_user:
    with st.chat_message("user"):
        second_input = st.chat_input("<name of tool> will be triggered. You may type 'accept' to continue, else type 'reject' to stop the execution. If not, you may also rewrite your query.")

    if second_input:
        # display the updated input
        st.session_state.convo_history.append({"role": "user", "content": second_input, "image": None})
        with st.chat_message("user"):
            st.markdown(second_input)
            # get the response
            response = chatbot_response({'text': second_input, 'img': None})
            st.session_state.last_response = response
            if response and response.get('trigger', False):
                st.session_state.awaiting_user = True
            else:
                st.session_state.awaiting_user = False
        st.rerun()


# # Display the last response if available and not awaiting further input
# if st.session_state.last_response and not st.session_state.awaiting_user:
#     response = st.session_state.last_response
#     if response['text']:
#         placeholder.markdown(response['text'])
#     if response['base64']:
#         images = base64_to_image(response["base64"])
#         if len(images) == 1:
#             st.image(images[0], caption="Generated Image", use_container_width=True)
#         else:
#             # user_option = st.selectbox('Which image do you want to keep?', ["keep all"] +[f'Image {i+1}' for i in range(len(images))], key="image_selectbox")
#             for i in range(0, len(images), 2):
#                 cols = st.columns(2)
#                 for j, each_img in enumerate(images[i:i+2]):
#                     cols[j].image(each_img, caption=f"Generated Image {i + j + 1}", use_container_width=True)
        
# # Display the last response if available and not awaiting further input
# if st.session_state.last_response and not st.session_state.awaiting_user:
#     response = st.session_state.last_response
#     if response['text'] and 'placeholder' in locals():
#         col1, col2 = st.columns([1, 1], gap="small")
#         with col1:
#             placeholder.markdown(response['text'])
#         with col2:
#             copy_button(response['text'],
#                     tooltip="copy",
#                     copied_label="copied!",
#                     icon="st",
#                 )
#         if response['base64']:
#             images = base64_to_image(response["base64"])
#             if len(images) == 1:
#                 st.image(images[0], caption="Generated Image", use_container_width=True)
#             else:
#                 # user_option = st.selectbox('Which image do you want to keep?', ["keep all"] +[f'Image {i+1}' for i in range(len(images))], key="image_selectbox")
#                 for i in range(0, len(images), 2):
#                     cols = st.columns(2)
#                     for j, each_img in enumerate(images[i:i+2]):
#                         cols[j].image(each_img, caption=f"Generated Image {i + j + 1}", use_container_width=True)      
#     elif response['text'] and 'placeholder' not in locals():
#         with st.chat_message("assistant"):
#             col1, col2 = st.columns([1, 1], gap="small")
#             with col1:
#                 st.markdown(response['text'])
#             with col2:
#                 copy_button(response['text'],
#                         tooltip="copy",
#                         copied_label="copied!",
#                         icon="st",
#                     )
#             if response['base64']:
#                 images = base64_to_image(response["base64"])
#                 if len(images) == 1:
#                     st.image(images[0], caption="Generated Image", use_container_width=True)
#                 else:
#                     # user_option = st.selectbox('Which image do you want to keep?', ["keep all"] +[f'Image {i+1}' for i in range(len(images))], key="image_selectbox")
#                     for i in range(0, len(images), 2):
#                         cols = st.columns(2)
#                         for j, each_img in enumerate(images[i:i+2]):
#                             cols[j].image(each_img, caption=f"Generated Image {i + j + 1}", use_container_width=True)

# Display the last response if available and not awaiting further input
if st.session_state.last_response and not st.session_state.awaiting_user:
    response = st.session_state.last_response
    if response['text'] and 'placeholder' in locals():
        col1, col2 = st.columns([10, 1], gap="small")
        print('placeholder')
        with col1:
            placeholder.markdown(response['text'])
        with col2:
            copy_button(response['text'],
                    tooltip="copy",
                    copied_label="copied!",
                    icon="st",
                )
        if response['base64']:
            images = base64_to_image(response["base64"])
            if len(images) == 1:
                st.image(images[0], caption="Generated Image", use_container_width=True)
            else:
                # user_option = st.selectbox('Which image do you want to keep?', ["keep all"] +[f'Image {i+1}' for i in range(len(images))], key="image_selectbox")
                for i in range(0, len(images), 2):
                    cols = st.columns(2)
                    for j, each_img in enumerate(images[i:i+2]):
                        cols[j].image(each_img, caption=f"Generated Image {i + j + 1}", use_container_width=True)      
    elif response['text'] and 'placeholder' not in locals():
        with st.chat_message("assistant"):
            col1, col2 = st.columns([10, 1], gap="small")
            with col1:
                print('st')
                st.markdown(response['text'])
            with col2:
                copy_button(response['text'],
                        tooltip="copy",
                        copied_label="copied!",
                        icon="st",
                    )
            if response['base64']:
                images = base64_to_image(response["base64"])
                if len(images) == 1:
                    st.image(images[0], caption="Generated Image", use_container_width=True)
                else:
                    # user_option = st.selectbox('Which image do you want to keep?', ["keep all"] +[f'Image {i+1}' for i in range(len(images))], key="image_selectbox")
                    for i in range(0, len(images), 2):
                        cols = st.columns(2)
                        for j, each_img in enumerate(images[i:i+2]):
                            cols[j].image(each_img, caption=f"Generated Image {i + j + 1}", use_container_width=True)

    st.session_state.convo_history.append({"role": "assistant", "content": response['text'], "image": response["base64"]})
    st.session_state.last_response = None  # Reset after displaying

