import streamlit as st
import base64
import time

####################################################################################
# Streamlit app UI
####################################################################################

new_chat = st.Page("st_newchat.py", title="New Chat", icon=":material/chat:", default=True)

## hide footer, header, main menu
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

## page layout
st.set_page_config(page_title="PromoGenie", 
                   page_icon="📢",
                   layout='wide', 
                   initial_sidebar_state='auto',
                )

def main():
    """
    Display Streamlit updates and handle the chat interface.
    """

    ## sidebar
    # sidebar for platform descriptions
    st.sidebar.header("How to Use")
    st.sidebar.markdown('''
            1. Choose your feature (Discuss Marketing Strategy, Produce Marketing Collaterals)
            2. (optional) Upload relevant materials
            3. Generate responses 
                        
            * Please note that chat sessions and history are not saved.
            ''')
    
    st.sidebar.markdown("---")

    st.sidebar.header("About Product Marketing Studio")
    st.sidebar.markdown('''
                Product Marketing Studio (PMS) is a marketing tool powered by AI that assists Operations Managers (OM) to design a marketing strategy to achieve product's marketing goals through various tools (e.g., competitive analysis, marketing knowledge base, collaterals generator).
                ''')
    
    st.sidebar.markdown("---")

    
    ## new chat page
    pg = st.navigation([new_chat])
    pg.run()


if __name__ == "__main__":
    main()