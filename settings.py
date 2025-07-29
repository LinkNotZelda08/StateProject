import streamlit as st

from storeandload import load_value, store_value


def dual_value(key: str, key2: str):
    store_value(key)
    store_value(key2)


def gdbint(
    key1: str,
    key2: str,
    key3: str,
    togtext: str,
    inptext: str,
    min: int,
    max: int,
    default: int,
    states: dict,
):
    load_value(key1)
    load_value(key2)
    load_value(key3)
    currentuse = sum(
        [p.default_value for i in st.session_state["_states"].values() for p in i]
    )
    disable = currentuse <= default
    disable = st.session_state.get(f"_{key1}", False) and not disable
    if st.toggle(
        togtext,
        key=f"_{key1}",
        on_change=store_value,
        args=[key1],
        disabled=disable,
    ):
        st.session_state[f"_{key2}"] = st.number_input(
            inptext,
            min,
            max,
            key=f"_{key3}",
            on_change=dual_value,
            args=[key2, key3],
            label_visibility="collapsed",
        )
        if disable:
            st.info(
                "You cannot turn off the override because your current point usage exceeds the default maximum of 100. Reduce your point usage to turn off this feature."
            )
    else:
        st.session_state[f"_{key2}"] = default
    store_value(key1)
    store_value(key2)
    store_value(key3)


def gdbstr(key1: str, key2: str, key3: str, togtext: str, inptext: str, default: int):
    load_value(key1)
    load_value(key2)
    load_value(key3)
    if st.toggle(
        togtext,
        value=st.session_state.get(f"_{key1}", False),
        key=f"_{key1}",
        on_change=store_value,
        args=[key1],
    ):
        st.session_state[f"_{key2}"] = st.text_input(
            inptext,
            key=f"_{key3}",
            on_change=dual_value,
            args=[key2, key3],
            label_visibility="collapsed",
        )
    else:
        st.session_state[f"_{key2}"] = default
    store_value(key1)
    store_value(key2)
    store_value(key3)


gdbint(
    "max_points_toggle",
    "max_points_value",
    "max_points_retention",
    "Override max points",
    "New max points",
    sum([p.default_value for i in st.session_state["_states"].values() for p in i]),
    1000,
    100,
    st.session_state["states"],
)
gdbstr(
    "table_round_toggle",
    "table_round_value",
    "table_round_retention",
    "Override decimal rounding in tables",
    'New number of decimal points ("None" for no rounding)',
    2,
)
