import streamlit as st

from components.faq import faq
#from dotenv import load_dotenv
import os

#load_dotenv()


def sidebar():
    with st.sidebar:
        
        st.markdown("# About")
        st.markdown(
            "Chess GPT allows you to ask questions about the John G. White "
            "chess collection in Cleveland Public Library "
        )

        faq()