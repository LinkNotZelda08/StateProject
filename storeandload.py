import streamlit as st


def store_value(key):
    st.session_state[key] = st.session_state["_" + key]


def load_value(key):
    st.session_state["_" + key] = st.session_state[key]
