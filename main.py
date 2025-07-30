import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from numpy import base_repr as br

from storeandload import load_value, store_value


class SingleState:
    def __init__(
        self,
        code: str,
        friendly_name: str,
        category: str,
        sorting_name: str,
        default_value: int,
        invert: bool,
        states: str,
    ):
        """
        Initializes a SingleState object and adds it to a dictionary based on its category. If that category is not present in the dictionary, one is created.

        Args:
            code (str): The specific code that identifies the table to take US Census data from
            friendly_name (str): The name that will be shown along with a number input associated with this object on the Streamlit webpage
            category (str): The category that the SingleState falls under that will be shown on Streamlit
            sorting_name (str): The name that will be used for sorting all SingleState objects alphabetically within a specific category
            default_value (int): The default value that will be associated with the input on Streamlit
            invert (bool): Indicates if the function is inverse or not
            states (dict): The dictionary that the SingleState object is added to
        """
        saved_value = default_value
        for i in st.session_state[f"_{states}"].values():
            for p in i:
                if p.code == code and hasattr(p, "val"):
                    saved_value = p.val
                    break
        for i in st.session_state[f"_{states}"].values():
            i[:] = [p for p in i if p.code != code]
        self.code = code
        self.friendly_name = friendly_name
        self.category = category
        self.sorting_name = sorting_name
        self.default_value = saved_value
        self.invert = invert
        try:
            st.session_state[f"_{states}"][category].append(self)
        except:
            st.session_state[f"_{states}"][category] = []
            st.session_state[f"_{states}"][category].append(self)

    @st.cache_data
    def process(_self, code, default_value, invert):
        """
        Processes the data of a US Census table specified by the associated code argument.

        Args:
            code (str): The specific code that identifies the table to take US Census data from
            default_value (int): The default value that will be associated with the input on Streamlit
            invert (bool): Indicates if the function is inverse or not

        Returns:
            DataFrame: A Pandas DataFrame with columns of state name, the original stat from the table, the ANSI code of each state, and the converted score after min-max scaling
        """
        response = requests.get(
            f"https://api.census.gov/data/2023/acs/acs1/subject?get=NAME,{code}&for=state:*"
        )
        data = response.json()
        data.pop(0)
        data = [i for i in data if i[2] not in ["11", "72"]]
        data = [[i[0], float(i[1]), int(i[2])] for i in data]
        stat = [i[1] for i in data]
        if invert:
            stat = minmax_scale(stat, (default_value, 0))
        else:
            stat = minmax_scale(stat, (0, default_value))
        for i in range(len(data)):
            data[i].append(float(stat[i]))
        data = pd.DataFrame(data, columns=["NAME", "stat", "code", "score"])
        data.set_index("code", inplace=True)
        data = data.sort_values(by=["score", "NAME"]).iloc[::-1]
        return data

    @st.cache_data
    def msh():
        """
        Returns a template Pandas DataFrame with state names and ANSI codes, but zeroed stat and score columns.

        Returns:
            DataFrame: a template Pandas DataFrame with state names and ANSI codes, but zeroed stat and score columns.
        """
        response = requests.get(
            "https://api.census.gov/data/2023/acs/acs1/subject?get=NAME,S1501_C02_015E&for=state:*"
        )
        data = response.json()
        data.pop(0)
        data = [i for i in data if i[2] not in ["11", "72"]]
        data = [[i[0], float(0), int(i[2]), float(0)] for i in data]
        data = pd.DataFrame(data, columns=["NAME", "stat", "code", "score"])
        data.set_index("code", inplace=True)
        data = data.sort_values(by=["score", "NAME"]).iloc[::-1]
        return data


class MultiState:
    def __init__(self, states: str, codeget: str):
        """
        Creates a MultiState object based on the SingleStates contained within the states arg

        Args:
            states (str): A dictionary that holds the invidual SingleState objects by their category names
            codeget (str): The value of the code inputted in the text box on the Streamlit page
            refresh_counter (int): A value that counts the number of times the Streamlit app has rerun
        """
        st.session_state[f"_{states}"] = dict(
            sorted(st.session_state[f"_{states}"].items())
        )
        for p in st.session_state[f"_{states}"]:
            st.session_state[f"_{states}"][p] = sorted(
                st.session_state[f"_{states}"][p], key=lambda item: item.friendly_name
            )
        self.create_inputs(states)
        if codeget != "":
            count = 0
            trans = listdecode(codeget)
            for i in st.session_state[f"_{states}"].values():
                for p in i:
                    p.val = trans[count]
                    count += 1
        self.df = self.process(states)

    def create_inputs(_self, states):
        maxhelp = st.session_state["max_points_value"]
        usedhelp = sum(
            [
                p.default_value
                for i in st.session_state[f"_{states}"].values()
                for p in i
            ]
        )
        lefthelp = maxhelp - usedhelp
        for p in st.session_state[f"_{states}"]:
            st.sidebar.subheader(p)

            def change_number(i):
                i.val = st.session_state[i.friendly_name]

            for i in st.session_state[f"_{states}"][p]:
                st.sidebar.number_input(
                    i.friendly_name,
                    0,
                    i.default_value + lefthelp,
                    i.default_value,
                    key=i.friendly_name,
                    on_change=change_number,
                    args=[i],
                )
                i.val = st.session_state[i.friendly_name]
                i.df = i.process(i.code, i.val, i.invert)

    def process(self, states):
        """
        Creates a DataFrame template and adds the score values of every SingleState object within the states arg

        Returns:
            DataFrame: A Pandas DataFrame with the combined score values of the SingleStates within the states arg
        """
        data = SingleState.msh()
        for p in st.session_state[f"_{states}"].values():
            for i in p:
                data = data.merge(i.df[["NAME", "score"]], on="NAME")
                data["score"] = data["score_x"] + data["score_y"]
                data = data.drop(columns=["score_x", "score_y"])
            data = data.sort_values(by=["score", "NAME"])
        return data


def graph(state: MultiState):
    """
    Creates a map based on the values of the state arg

    Args:
        states (MultiState): The MultiState object that the values of the graph will be derived from
    """
    us_state_to_abbrev = {
        "Alabama": "AL",
        "Alaska": "AK",
        "Arizona": "AZ",
        "Arkansas": "AR",
        "California": "CA",
        "Colorado": "CO",
        "Connecticut": "CT",
        "Delaware": "DE",
        "Florida": "FL",
        "Georgia": "GA",
        "Hawaii": "HI",
        "Idaho": "ID",
        "Illinois": "IL",
        "Indiana": "IN",
        "Iowa": "IA",
        "Kansas": "KS",
        "Kentucky": "KY",
        "Louisiana": "LA",
        "Maine": "ME",
        "Maryland": "MD",
        "Massachusetts": "MA",
        "Michigan": "MI",
        "Minnesota": "MN",
        "Mississippi": "MS",
        "Missouri": "MO",
        "Montana": "MT",
        "Nebraska": "NE",
        "Nevada": "NV",
        "New Hampshire": "NH",
        "New Jersey": "NJ",
        "New Mexico": "NM",
        "New York": "NY",
        "North Carolina": "NC",
        "North Dakota": "ND",
        "Ohio": "OH",
        "Oklahoma": "OK",
        "Oregon": "OR",
        "Pennsylvania": "PA",
        "Rhode Island": "RI",
        "South Carolina": "SC",
        "South Dakota": "SD",
        "Tennessee": "TN",
        "Texas": "TX",
        "Utah": "UT",
        "Vermont": "VT",
        "Virginia": "VA",
        "Washington": "WA",
        "West Virginia": "WV",
        "Wisconsin": "WI",
        "Wyoming": "WY",
        "District of Columbia": "DC",
        "American Samoa": "AS",
        "Guam": "GU",
        "Northern Mariana Islands": "MP",
        "Puerto Rico": "PR",
        "United States Minor Outlying Islands": "UM",
        "Virgin Islands, U.S.": "VI",
    }
    df = state.df.reset_index()
    df["state_code"] = df["NAME"].map(us_state_to_abbrev)
    fig = px.choropleth(
        df,
        locations="state_code",
        color="score",
        locationmode="USA-states",
        scope="usa",
        hover_name="NAME",
        hover_data={"score": True, "state_code": False},
        color_continuous_scale=st.session_state["graph_cscale_value"],
    )
    fig.update_layout(
        geo=dict(bgcolor="#0e1117"),
    )
    st.plotly_chart(fig)


def minmax_scale(array: list, values: tuple):
    """
    Takes in a list, then returns a list with all of the objects within min max scaled

    Args:
        array (list): The list that is to be min max scaled
        values (tuple): The range of the returned list
    Returns:
        list: A min max scaled list based on the array arg
    """
    mini = min(array)
    maxi = max(array)
    final = [
        (values[0] + (((i - mini) * (values[1] - values[0])) / (maxi - mini)))
        for i in array
    ]
    return final


def encode(num: str):
    """
    Base36 encodes a number

    Args:
        num (str): The number to be encoded
    Returns:
        str: The encoded string
    """
    encoded = br(num, 36)
    return encoded.zfill(2)


def decode(num: str):
    """
    Decodes a number from Base36

    Args:
        num (str): The string to be decoded
    Returns:
        str: The decoded number
    """
    return int(num, 36)


def listencode(array: list):
    """
    Encodes a series of numbers from a list into Base36

    Args:
        array (list): The list holding the numbers to be encoded
    Returns:
        str: A string containing the encoded numbers
    """
    final = ""
    for i in array:
        final += encode(i)
    return final


def listdecode(code: str):
    """
    Decodes a series of numbers from a list out of Base36

    Args:
        code (str): The string to be decoded
    Returns:
        list: A list of the decoded numbers
    """
    final = []
    for i in range(0, len(code), 2):
        final.append(decode(code[i : i + 2]))
    return final


def main():
    st.session_state.refresh_counter += 1
    st.title("Main State Page")
    load_value("states")
    with st.sidebar.form("code_form"):
        codeget = st.text_input("If you have a code, put it here!")
        submitted = st.form_submit_button("Apply", use_container_width=True)
        if submitted:
            st.rerun()
    max = st.sidebar.subheader("Max points: ")
    used = st.sidebar.subheader("Used points: ")
    left = st.sidebar.subheader("Points left: ")
    SingleState(
        "S1501_C02_014E",
        "Percent of population 25+ with high school degree or higher",
        "Education",
        "high school degree",
        0,
        False,
        "states",
    )
    SingleState(
        "S1501_C02_015E",
        "Percent of population 25+ with bachelor's degree or higher",
        "Education",
        "bachelor's degree",
        0,
        False,
        "states",
    )
    SingleState(
        "S1501_C02_013E",
        "Percent of population 25+ with graduate degree or higher",
        "Education",
        "graduate degree",
        0,
        False,
        "states",
    )
    SingleState(
        "S2701_C05_001E",
        "Percent of population without health insurance",
        "Healthcare",
        "health insurance",
        0,
        True,
        "states",
    )
    SingleState(
        "S1901_C01_012E",
        "Median household income in the past 12 months",
        "Economy",
        "household income median",
        0,
        False,
        "states",
    )
    SingleState(
        "S1901_C01_013E",
        "Mean household income in the past 12 months",
        "Economy",
        "household income mean",
        0,
        False,
        "states",
    )
    SingleState(
        "S2301_C04_001E",
        "Unemployment rates for 16+",
        "Economy",
        "unemployment rates",
        0,
        True,
        "states",
    )
    big = MultiState("states", codeget)
    store_value("states")
    st.sidebar.text(
        f"Your current code is {listencode([p.val for i in st.session_state.states.values() for p in i])}"
    )
    maxhelp = st.session_state["max_points_value"]
    usedhelp = sum([p.val for i in st.session_state["states"].values() for p in i])
    max.subheader(f"Max points: {maxhelp}")
    used.subheader(f"Used points: {usedhelp}")
    left.subheader(f"Points left: {maxhelp - usedhelp}")
    graph(big)
    st.dataframe(
        big.df,
        hide_index=True,
        column_order=["NAME", "score"],
        column_config={
            "NAME": "State Name",
            "score": st.column_config.NumberColumn(
                "Total Score", format=f"%.{st.session_state['table_round_value']}f"
            ),
        },
        on_select="ignore",
    )


if __name__ == "__main__":
    main()
