import streamlit as st


def session_state_create(name: str, value: int):
    if name not in st.session_state:
        st.session_state[name] = value


def session_state_create_mass(rangee: int, value: int):
    for i in range(rangee):
        if i not in st.session_state:
            st.session_state[i] = value


session_state_create("refresh_counter", 0)
session_state_create("max_points_toggle", False)
session_state_create("max_points_value", 100)
session_state_create("max_points_retention", 100)
session_state_create("table_round_toggle", False)
session_state_create("table_round_value", 2)
session_state_create("table_round_retention", 2)
session_state_create("graph_cscale_toggle", False)
session_state_create("graph_cscale_value", "reds")
session_state_create("graph_cscale_retention", "reds")
session_state_create("states", {})
session_state_create("processed_keys", [])
session_state_create_mass(7, 0)

main = st.Page("main.py", title="Main")
documentation = st.Page("documentation.py", title="Documentation")
settings = st.Page("settings.py", title="Settings")

pg = st.navigation([main, documentation, settings])
st.set_page_config(page_title="States Statistics Viewer", page_icon=":material/edit:")
pg.run()
