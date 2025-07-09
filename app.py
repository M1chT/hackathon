import streamlit as st
import base64
import time

## backend
# Simple rule-based chatbot logic
def chatbot_response(user_input):
    user_input = user_input.lower()
    if "hello" in user_input or "hi" in user_input:
        return "Hello! How can I help you today?"
    elif "how are you" in user_input:
        return "I'm just a bot, but I'm doing great! Thanks for asking."
    elif "bye" in user_input:
        return "Goodbye! Have a great day."
    else:
        return "I'm not sure how to respond to that. Can you rephrase?"

## streamlit - initialise session state
def initialise_session_state():
    """Initialise session state variables."""
    if "history" not in st.session_state:
        st.session_state.history = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

## display image as base64 content to embed using img or CSS tags
def img_to_base64(image_path):
    """Convert image to base64."""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        print(f"Error converting image to base64: {str(e)}")
        return None
    
## for streaming of chat convo
def chat_stream(response):
    for char in response:
        yield char
        time.sleep(0.02)

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

def on_chat_submit(chat_input):
    """
    Handle chat input submissions and interact with the OpenAI API.

    Parameters:
    - chat_input (str): The chat input from the user.
    - latest_updates (dict): The latest Streamlit updates fetched from a JSON file or API.

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

## [FOR TESTING!!!] of another interface only
def display_streamlit_updates():
    """Display the latest updates of the Streamlit."""
    with st.expander("Streamlit 1.36 Announcement", expanded=False):
        st.markdown('''For more details on this version, check out the [Streamlit Forum post](https://docs.streamlit.io/library/changelog#version).''')



####################################################################################
# Streamlit app UI
####################################################################################

## hide footer, header, main menu
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

## page layout
st.set_page_config(page_title="Product Marketing Studio", 
                   page_icon="📢",
                   layout='wide', 
                   initial_sidebar_state='auto',
                #    menu_items={
                #     "Get help": "https://github.com/AdieLaine/Streamly",
                #     # "Report a bug": "https://github.com/AdieLaine/Streamly",
                #     "About": """
                #         ### Product Marketing Studio (PMS)
                #         #### Powered by Agents | Tools | OpenAI LLMs

                #         The platform, PMS assists our Operations Manager (OM) to design a marketing strategy to reach their product's marketing goals through various tools (e.g., competitive analysis, marketing knowledge base, collaterals generator).
                #     """
                # }
                )



def main():
    """
    Display Streamlit updates and handle the chat interface.
    """
    initialise_session_state()

    # if not st.session_state.history:
    #     initial_bot_message = "Hello! How can I assist you with Streamlit today?"
    #     st.session_state.history.append({"role": "assistant", "content": initial_bot_message})
    #     st.session_state.conversation_history = initialise_conversation()
    
    # hamburger icon
    # st.logo("./images/hamburger.jpg", icon_image="./images/hamburger.jpg")

    # # Load and display sidebar image
    # img_path = "./images/sidebar toolkit.jpg"
    # img_base64 = img_to_base64(img_path)
    # if img_base64:
    #     st.sidebar.markdown(
    #         f'<img src="data:image/png;base64,{img_base64}">',
    #         unsafe_allow_html=True,
    #     )
    
    # st.title("Discover your marketing needs ⭐")
    # st.image("./images/marketing.jpg", use_container_width=True)

    ## sidebar
    # sidebar for platform descriptions
    st.sidebar.header("⭐ About")
    st.sidebar.markdown('''
                ### Product Marketing Studio
                #### Powered by Agents

                The platform, PMS assists our Operations Manager (OM) to design a marketing strategy to achieve product's marketing goals through various tools (e.g., competitive analysis, marketing knowledge base, collaterals generator).
                ''')
    
    st.sidebar.markdown("---")
    st.sidebar.header("🧰 Resources")

    # sidebar for pages
    mode = st.sidebar.radio(label="Choose one:", options=["Chat with Marketing Guru", "Generate Campaign Collaterals"], index=0)

    ## main page
    # CHAT WITH MARKETING GURU #############################################
    if mode == "Chat with Marketing Guru": 

        st.header("💬 Chat with Marketing Guru")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        user_input = st.chat_input("Hello! How can I assist you today?")
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
                        args=[i],
                    )
        
    # DESIGN YOUR COLLATERALS #############################################
    else:
        st.header("😎 Generate Campaign Collaterals")

        if "stage" not in st.session_state:
            st.session_state.stage = "user"
            st.session_state.pending = None
            st.session_state.history2 = []
        
        # user_input = st.chat_input("What collaterals do you need?")
        # if user_input:
        #     on_chat_submit(user_input)

        # Allow editing of generated response - text
        if st.session_state.stage == "user":
            if user_input := st.chat_input("Hello! What collaterals do you need?"):
                st.session_state.history2.append({"role": "user", "content": user_input})
                on_chat_submit(user_input)
                with st.chat_message("user", avatar="./images/user.png"):
                    st.write(user_input)
                with st.chat_message("assistant", avatar="./images/guru2.jpg"):
                    response = st.write_stream(chat_stream("what is this?"))
                    st.session_state.pending = response
                    st.session_state.stage = "validate"
                    st.rerun()

        elif st.session_state.stage == "validate":
            st.chat_input("Accept, or rewrite the answer above", disabled=True)
            with st.chat_message("assistant"):
                st.markdown(st.session_state.pending)
                st.divider()
                cols = st.columns(2)
                if cols[0].button("Accept"):
                    st.session_state.history2.append(
                        {"role": "assistant", "content": st.session_state.pending}
                    )
                    st.session_state.pending = None
                    st.session_state.stage = "user"
                    st.rerun()
                if cols[1].button("Rewrite answer", type="tertiary"):
                    st.session_state.stage = "rewrite"
                    st.rerun()

        elif st.session_state.stage == "rewrite":
            st.chat_input("AAccept, or rewrite the answer above", disabled=True)
            with st.chat_message("assistant"):
                new = st.text_area("Rewrite the answer", value=st.session_state.pending)
                if st.button(
                    "Update", type="primary", disabled=new is None or new.strip(". ") == ""
                ):
                    st.session_state.history2.append({"role": "assistant", "content": new})
                    st.session_state.pending = None
                    st.session_state.stage = "user"
                    st.rerun()
        
        ## Display chat conversations + feedback
        for i, message in enumerate(st.session_state.history2):
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
                        args=[i],
                    )

        # Display chats with images - allow download button of the images/ copy of text

        # A/B testing

        


if __name__ == "__main__":
    main()

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
