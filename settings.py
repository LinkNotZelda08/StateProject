import plotly.express as px
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
):
    load_value(key1)
    load_value(key2)
    load_value(key3)
    if key1 == "max_points_toggle":
        currentuse = sum(
            [p.default_value for i in st.session_state["_states"].values() for p in i]
        )
        disable = currentuse <= default
        disable = st.session_state.get(f"_{key1}", False) and not disable
    else:
        disable = False
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
        if key1 == "max_points_toggle" and disable:
            st.info(
                "You cannot turn off the override because your current point usage exceeds the default maximum of 100. Lower your point usage to a minimum of 100 to turn off this feature."
            )
    else:
        st.session_state[f"_{key2}"] = default
    store_value(key1)
    store_value(key2)
    store_value(key3)


def gdbstr(
    key1: str,
    key2: str,
    key3: str,
    togtext: str,
    inptext: str,
    default: int,
):
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
        if key1 == "graph_cscale_toggle":
            if st.button("See all color scales"):
                st.write(
                    "To use a specific scale, write the name associated with it on the left. Case insensitive"
                )
                st.plotly_chart(px.colors.sequential.swatches_continuous())
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
)
gdbint(
    "table_round_toggle",
    "table_round_value",
    "table_round_retention",
    "Override decimal rounding in tables",
    "New number of decimal points",
    0,
    10,
    2,
)
gdbstr(
    "graph_cscale_toggle",
    "graph_cscale_value",
    "graph_cscale_retention",
    "Override color scale of graph",
    'New color scale ("None" for no rounding)',
    "reds",
)
