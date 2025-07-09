import streamlit as st
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
    user_input = chat_input.strip().lower()

    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = initialise_conversation()

    st.session_state.conversation_history.append({"role": "user", "content": user_input})

    response = chatbot_response(user_input)
    assistant_reply = response

    st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})

    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": assistant_reply})

def save_feedback(index):
    st.session_state.history[index]["feedback"] = st.session_state[f"feedback_{index}"]

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
    file = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
with col2:
    user_input = st.chat_input("Hello! How can I assist you today?")

# Save image if there is one
if file is not None:
    image = Image.open(file)
    ##st.image(image, caption="Uploaded Image", use_column_width=True)

if user_input:
    on_chat_submit(user_input)

## Display chat conversations + feedback
for i, message in enumerate(st.session_state.history):
    avatar_image = "./images/guru2.jpg" if message["role"] == "assistant" else "./images/user.png" if message["role"] == "user" else None
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

    # if "stage" not in st.session_state:
    #     st.session_state.stage = "user"
    #     st.session_state.pending = None
    #     st.session_state.history2 = []
    
    # # user_input = st.chat_input("What collaterals do you need?")
    # # if user_input:
    # #     on_chat_submit(user_input)

    # # Allow editing of generated response - text
    # if st.session_state.stage == "user":
    #     if user_input := st.chat_input("Hello! What collaterals do you need?"):
    #         st.session_state.history2.append({"role": "user", "content": user_input})
    #         on_chat_submit(user_input)
    #         with st.chat_message("user", avatar="./images/user.png"):
    #             st.write(user_input)
    #         with st.chat_message("assistant", avatar="./images/guru2.jpg"):
    #             response = st.write_stream(chat_stream("what is this?"))
    #             st.session_state.pending = response
    #             st.session_state.stage = "validate"
    #             st.rerun()

    # elif st.session_state.stage == "validate":
    #     st.chat_input("Accept, or rewrite the answer above", disabled=True)
    #     with st.chat_message("assistant"):
    #         st.markdown(st.session_state.pending)
    #         st.divider()
    #         cols = st.columns(2)
    #         if cols[0].button("Accept"):
    #             st.session_state.history2.append(
    #                 {"role": "assistant", "content": st.session_state.pending}
    #             )
    #             st.session_state.pending = None
    #             st.session_state.stage = "user"
    #             st.rerun()
    #         if cols[1].button("Rewrite answer", type="secondary"):
    #             st.session_state.stage = "rewrite"
    #             st.rerun()

    # elif st.session_state.stage == "rewrite":
    #     st.chat_input("AAccept, or rewrite the answer above", disabled=True)
    #     with st.chat_message("assistant"):
    #         new = st.text_area("Rewrite the answer", value=st.session_state.pending)
    #         if st.button(
    #             "Update", type="primary", disabled=new is None or new.strip(". ") == ""
    #         ):
    #             st.session_state.history2.append({"role": "assistant", "content": new})
    #             st.session_state.pending = None
    #             st.session_state.stage = "user"
    #             st.rerun()
    
    # ## Display chat conversations + feedback
    # for i, message in enumerate(st.session_state.history2):
    #     avatar_image = "./images/guru2.jpg" if message["role"] == "assistant" else "./images/user.png" if message["role"] == "user" else None
    #     with st.chat_message(message["role"], avatar=avatar_image):
    #         st.write(message["content"])
    #         # st.write_stream(chat_stream(message["content"]))
    #         if message["role"] == "assistant":
    #             feedback = message.get("feedback", None)
    #             st.session_state[f"feedback_{i}"] = feedback
    #             st.feedback(
    #                 "thumbs",
    #                 key=f"feedback_{i}",
    #                 disabled=feedback is not None,
    #                 on_change=save_feedback,
    #                 args=[i],
    #             )

    # # Display chats with images - allow download button of the images/ copy of text

    # # A/B testing



# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# user_input = st.text_input("You:", key="input")

# if user_input:
#     response = chatbot_response(user_input)

#     # Save conversation
#     st.session_state.chat_history.append(("You", user_input))
#     st.session_state.chat_history.append(("Bot", response))

# # Display conversation
# for speaker, text in st.session_state.chat_history:
#     if speaker == "You":
#         st.markdown(f"**You:** {text}")
#     else:
#         st.markdown(f"**🤖 Bot:** {text}")
