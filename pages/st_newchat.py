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

