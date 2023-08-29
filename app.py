# Interface web para consulta na web das cartas escolhidas nas lojas de preferência.
# Dev: Lucca Mariano

# Imports -------------------------------------------------------------------------
from main_async import *
import streamlit as st
import time
from PIL import Image

# Sub Main ------------------------------------------------------------------------
def sel_callback():
    st.session_state.a = st.session_state.sel
    st.session_state.b = st.session_state.sel
    st.session_state.c = st.session_state.sel
    st.session_state.d = st.session_state.sel
    st.session_state.e = st.session_state.sel
    st.session_state.f = st.session_state.sel
    st.session_state.g = st.session_state.sel
    st.session_state.h = st.session_state.sel


def main():
    """MTG Search
    With Streamlit
    """
    st.set_page_config(
        page_title="Casualidade Dois.",
        page_icon="🃏")
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.title("Busca por cartas!")
    card_input = st.text_area("Coloque a lista de cartas aqui.")
    st.write('Selecione as lojas de interesse:')
    st.checkbox('Selecionar tudo!', key='sel', on_change=sel_callback)
    st.checkbox('Bazar', key='a')
    st.checkbox('Card Tutor', key='b')
    st.checkbox('CHQ', key='c')
    st.checkbox('Epic', key='d')
    st.checkbox('Flow', key='e')
    st.checkbox('Magic Domain', key='f')
    st.checkbox('Medieval', key='g')

    checkbox_list = [st.session_state.a, st.session_state.b, st.session_state.c, st.session_state.d, st.session_state.e,
                     st.session_state.f, st.session_state.g]

    if st.button("Buscar!"):
        result = main_module(card_input, checkbox_list)

if __name__ == "__main__":
    main()