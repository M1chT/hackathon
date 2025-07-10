import streamlit as st
import base64
import time


### functions for frontend #############################################
## streamlit - initialise session state
def initialise_session_state():
    """Initialise session state variables."""
    if "history" not in st.session_state:
        st.session_state.history = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

## login
def login():
    if st.button("Login"):
        st.session_state.logged_in = True
        st.rerun()

## logout
def logout():
    st.session_state["logged_in"] = False
    st.session_state["user"] = None
    st.rerun()

## login and logout pages
login_page = st.Page("login.py", title="Login", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

## other pages
new_chat = st.Page("pages/st_newchat.py", title="New Chat", icon=":material/chat:", default=True)


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
                )


def main():
    """
    Display Streamlit updates and handle the chat interface.
    """
    initialise_session_state()

    ## navigation (replacement of sidebar with clickable pages)
    if st.session_state.logged_in:
        pg = st.navigation(
            {
                "Account": [logout_page],
                "Pages": [new_chat],
            }
        )
    else:
        pg = st.navigation([login_page])

    pg.run()


    # # if not st.session_state.history:
    # #     initial_bot_message = "Hello! How can I assist you with Streamlit today?"
    # #     st.session_state.history.append({"role": "assistant", "content": initial_bot_message})
    # #     st.session_state.conversation_history = initialise_conversation()
    
    # # hamburger icon
    # # st.logo("./images/hamburger.jpg", icon_image="./images/hamburger.jpg")

    # # # Load and display sidebar image
    # # img_path = "./images/sidebar toolkit.jpg"
    # # img_base64 = img_to_base64(img_path)
    # # if img_base64:
    # #     st.sidebar.markdown(
    # #         f'<img src="data:image/png;base64,{img_base64}">',
    # #         unsafe_allow_html=True,
    # #     )
    
    # # st.title("Discover your marketing needs ⭐")
    # # st.image("./images/marketing.jpg", use_container_width=True)

    # ## sidebar
    # # sidebar for platform descriptions
    # st.sidebar.header("⭐ About")
    # st.sidebar.markdown('''
    #             ### Product Marketing Studio
    #             #### Powered by Agents

    #             The platform, PMS assists our Operations Manager (OM) to design a marketing strategy to achieve product's marketing goals through various tools (e.g., competitive analysis, marketing knowledge base, collaterals generator).
    #             ''')
    
    # st.sidebar.markdown("---")
    # st.sidebar.header("🧰 Resources")

    # # sidebar for pages
    # mode = st.sidebar.radio(label="Choose one:", options=["Chat with Marketing Guru", "Generate Campaign Collaterals"], index=0)
    

if __name__ == "__main__":
    main()