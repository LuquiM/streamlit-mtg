# Interface web para consulta na web das cartas escolhidas nas lojas de preferência.
# Dev: Lucca Mariano

# Imports -------------------------------------------------------------------------
from main_async import *
import streamlit as st
import time
from PIL import Image

# Sub Main ------------------------------------------------------------------------

def main():
    """MTG Search
    With Streamlit
    """
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.title("Busca por cartas!")
    deck_name = st.text_input("Escreva um nome para seu deck."," ")
    card_input = st.text_area("Coloque a lista de cartas aqui.")
    st.write('Selecione as lojas de interesse:')
    bazar = st.checkbox('Bazar')
    card_tutor = st.checkbox('Card Tutor')
    chq = st.checkbox('CHQ')
    epic = st.checkbox('Epic')
    flow = st.checkbox('Flow')
    magic_domain = st.checkbox('Magic Domain')
    medieval = st.checkbox('Medieval')

    checkbox_list = [bazar, card_tutor, epic, flow, medieval, magic_domain, chq]

    if st.button("Buscar!"):
        result = main_module(card_input, checkbox_list, deck_name)

if __name__ == "__main__":
    main()