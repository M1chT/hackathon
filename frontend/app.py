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
    st.sidebar.header("How to use")
    st.sidebar.markdown('''
               Blah blah blah
                ''')
    st.sidebar.markdown("---")
    st.sidebar.header("About")
    st.sidebar.markdown('''
                ### PromoGenie
                #### Powered by Agents

                The platform, PMS assists our Operations Manager (OM) to design a marketing strategy to achieve product's marketing goals through various tools (e.g., competitive analysis, marketing knowledge base, collaterals generator).
                ''')
    
    ## new chat page
    pg = st.navigation([new_chat])
    pg.run()


if __name__ == "__main__":
    main()
