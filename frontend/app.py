import streamlit as st
import base64
import io
import time
from PIL import Image

# convert image to base64
def sidebar_img_to_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.sidebar.error("Image not found.")
        return None

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
    img_path = "./frontend/images/logo white.png"
    img_base64 = sidebar_img_to_base64(img_path)
    if img_base64:
        st.sidebar.markdown(
            f'<img src="data:image/png;base64,{img_base64}">',
            unsafe_allow_html=True,
        )

    st.sidebar.header("How to Use")
    st.sidebar.markdown('''
            1. Choose your feature (Discuss Marketing Strategy, Produce Marketing Collaterals)
            2. (optional) Upload relevant materials
            3. Generate responses 
                        
            Please note that chat sessions and history are not saved.
            ''')
    st.sidebar.markdown("---")
    st.sidebar.header("About PromoGenie")
    st.sidebar.markdown('''
                PromoGenie is an AI-powered tool that helps Operations Managers design targeted marketing strategies using features such as competitive analysis, marketing knowledge base, and collateral generation.
                ''')
    
    st.sidebar.markdown("---")
    
    ## new chat page
    pg = st.navigation([new_chat])
    pg.run()


if __name__ == "__main__":
    main()