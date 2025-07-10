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