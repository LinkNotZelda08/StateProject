import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from numpy import base_repr as br


class SingleState:
    def __init__(self, code, fname, default_value: int, invert: bool):
        self.code = code
        self.fname = fname
        self.default_value = default_value
        self.invert = invert

    @st.cache_data
    def namemkr(code):
        response = requests.get(
            f"https://api.census.gov/data/2023/acs/acs1/subject/variables/{code}.json"
        )
        data = response.json()
        return data["label"]

    @st.cache_data
    def process(_self, code, default_value, invert):
        response = requests.get(
            f"https://api.census.gov/data/2023/acs/acs1/subject?get=NAME,{code}&for=state:*"
        )
        data = response.json()
        data.pop(0)
        data = [i for i in data if i[2] not in ["11", "72"]]
        data = [[i[0], float(i[1]), int(i[2])] for i in data]
        stat = [i[1] for i in data]
        if invert:
            stat = [100 - i for i in minmax_scale(stat, (0, default_value))]
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
    def __init__(self, states: list, codeget: list):
        self.states = states
        if codeget != "":
            trans = listdecode(codeget)
            for i in range(len(states)):
                self.states[i].default_value = trans[i]
        for i in self.states:
            i.val = st.sidebar.number_input(i.fname, 0, 1000, i.default_value)
            i.df = i.process(i.code, i.val, i.invert)
        self.df = self.process()

    def process(self):
        data = SingleState.msh()
        for i in self.states:
            data = data.merge(i.df[["NAME", "score"]], on="NAME")
            data["score"] = data["score_x"] + data["score_y"]
            data = data.drop(columns=["score_x", "score_y"])
        data = data.sort_values(by=["score", "NAME"]).iloc[::-1]
        return data


def graph(state: SingleState):
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
    )
    st.plotly_chart(fig)


def minmax_scale(array: list, values: tuple):
    mini = min(array)
    maxi = max(array)
    final = [
        (values[0] + (((i - mini) * (values[1] - values[0])) / (maxi - mini)))
        for i in array
    ]
    return final


def encode(num: str):
    encoded = br(num, 36)
    return encoded.zfill(2)


def decode(num):
    return int(num, 36)


def listencode(array: list):
    final = ""
    for i in array:
        final += encode(i)
    return final


def listdecode(code: int):
    code2 = str(code)
    final = []
    for i in range(0, len(code2), 2):
        final.append(decode(code2[i : i + 2]))
    return final


def main():
    st.set_page_config(page_title="Main State Page")
    st.title("Main State Page")
    st.sidebar.header("Main State Page")
    codeget = st.sidebar.text_input("If you have a code, put it here!")
    states = []
    employment_status = SingleState("S2301_C04_001E", "Unemployment Rates", 100, True)
    states.append(employment_status)
    educational_attainment = SingleState(
        "S1501_C02_015E", "Educational Attainment Rates", 100, False
    )
    states.append(educational_attainment)
    states = sorted(states, key=lambda s: s.fname)
    big = MultiState(states, codeget)
    graph(big)
    st.sidebar.text(f"Your current code is {listencode([i.val for i in states])}")


if __name__ == "__main__":
    main()
