import streamlit as st

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input(
    "Say something and/or attach an image",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
):
    user_input = prompt.text.strip()

    # Show user input in the chat
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Check if user input is "2 columns"
    if user_input == "2 columns":
        # Simulate bot response with two columns
        col1, col2 = st.columns(2)

        with col1:
            st.header("cat")
            # Append the columns as part of the message chain
            st.session_state.messages.append({"role": "assistant", "content": "cat"})
                    # Now append the Echo response under the columns
            response = f"Echo: {user_input}"
            with st.chat_message("assistant"):
                st.markdown(response)

        with col2:
            st.header("dog")
            # Append the columns as part of the message chain
            st.session_state.messages.append({"role": "assistant", "content": "dog"})
            # Now append the Echo response under the columns
            response = f"Echo: {user_input}"
            with st.chat_message("assistant"):
                st.markdown(response)


    else:
        # If not "2 columns", just echo the input in the message chain
        response = f"Echo: {user_input}"
        with st.chat_message("assistant"):
            st.markdown(response)

        # Append the echo response to the message chain
        st.session_state.messages.append({"role": "assistant", "content": response})















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

    if "convo_history" not in st.session_state:
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
        assistant_reply = response.json()["messages"][1]["content"]
        # assistant_reply = response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        assistant_reply = "Sorry, I couldn't process your request at the moment."

    # response = chatbot_response(user_input)
    # assistant_reply = response


    st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})

    st.session_state.history.append({"role": "user", "content": user_input})
    st.session_state.history.append({"role": "assistant", "content": assistant_reply})

