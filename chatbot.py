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