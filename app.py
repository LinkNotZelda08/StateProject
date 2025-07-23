import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from numpy import base_repr as br

if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0


class SingleState:
    def __init__(
        self,
        code: str,
        friendly_name: str,
        category: str,
        sorting_name: str,
        default_value: int,
        invert: bool,
        states: dict,
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
        self.code = code
        self.friendly_name = friendly_name
        self.category = category
        self.sorting_name = sorting_name
        self.default_value = default_value
        self.invert = invert
        try:
            states[self.category].append(self)
        except KeyError:
            states[self.category] = []
            states[self.category].append(self)

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
    def __init__(self, states: dict, codeget: str, refresh_counter: int):
        """
        Creates a MultiState object based on the SingleStates contained within the states arg

        Args:
            states (str): A dictionary that holds the invidual SingleState objects by their category names
            codeget (str): The value of the code inputted in the text box on the Streamlit page
            refresh_counter (int): A value that counts the number of times the Streamlit app has rerun
        """
        self.states = states
        if codeget != "":
            trans = listdecode(codeget)
            for i in range(len(states)):
                self.states[i].default_value = trans[i]
        self.states = dict(sorted(self.states.items()))
        for p in self.states:
            self.states[p] = sorted(self.states[p], key=lambda item: item.friendly_name)
            st.sidebar.subheader(p)
            for i in self.states[p]:
                i.val = st.sidebar.number_input(
                    i.friendly_name,
                    0,
                    1000,
                    i.default_value,
                    key=f"{i.friendly_name}_{refresh_counter}",
                )
                i.df = i.process(i.code, i.val, i.invert)
        self.df = self.process()

    def process(self):
        """
        Creates a DataFrame template and adds the score values of every SingleState object within the states arg

        Returns:
            DataFrame: A Pandas DataFrame with the combined score values of the SingleStates within the states arg
        """
        data = SingleState.msh()
        for p in self.states.values():
            for i in p:
                data = data.merge(i.df[["NAME", "score"]], on="NAME")
                data["score"] = data["score_x"] + data["score_y"]
                data = data.drop(columns=["score_x", "score_y"])
            data = data.sort_values(by=["score", "NAME"]).iloc[::-1]
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
    st.set_page_config(page_title="Main State Page")
    st.title("Main State Page")
    st.sidebar.header("Main State Page")
    with st.sidebar.form("code_form"):
        codeget = st.text_input("If you have a code, put it here!")
        submitted = st.form_submit_button("Apply", use_container_width=True)
        if submitted:
            st.session_state.refresh_counter += 1
    states = {}
    SingleState(
        "S1501_C02_014E",
        "Percent of population 25+ with high school degree or higher",
        "Education",
        "high school degree",
        0,
        False,
        states,
    )
    SingleState(
        "S1501_C02_015E",
        "Percent of population 25+ with bachelor's degree or higher",
        "Education",
        "bachelor's degree",
        100,
        False,
        states,
    )
    SingleState(
        "S1501_C02_013E",
        "Percent of population 25+ with graduate degree or higher",
        "Education",
        "graduate degree",
        0,
        False,
        states,
    )
    SingleState(
        "S2701_C05_001E",
        "Percent of population without health insurance",
        "Healthcare",
        "health insurance",
        100,
        True,
        states,
    )
    SingleState(
        "S1901_C01_012E",
        "Median household income in the past 12 months",
        "Economy",
        "household income median",
        100,
        False,
        states,
    )
    SingleState(
        "S1901_C01_013E",
        "Mean household income in the past 12 months",
        "Economy",
        "household income mean",
        0,
        False,
        states,
    )
    SingleState(
        "S2301_C04_001E",
        "Unemployment rates for 16+",
        "Economy",
        "unemployment rates",
        100,
        True,
        states,
    )
    big = MultiState(states, codeget, st.session_state.refresh_counter)
    graph(big)
    st.sidebar.text(
        f"Your current code is {listencode([state.val for state_list in states.values() for state in state_list])}"
    )
    st.subheader("How do the calculations work?")
    st.write(
        "This program uses a function called [min-max normalization](https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)) to rescale all values in a list within a given range based on the maximum and minimum values. For example, let’s say that we wanted to scale [a state-by-state list detailing the percentage of the population 25 and older who have bachelor's degrees or higher taken from the U.S. Census Bureau](https://api.census.gov/data/2023/acs/acs1/subject?get=NAME,S1501_C02_015E&for=state:*). The highest percentage is Massachusetts at 47.8%. The lowest is West Virginia at 24%. Let’s say our range is [0,42]. Our function would be:"
    )
    st.latex(r""" x'=\frac{42\left(x-24\right)}{23.8} """)
    st.html(
        "<center><caption>It really is a beautiful function, isn't it?</caption></center>"
    )
    st.write(
        "Massachusetts becomes 42, West Virginia becomes 0, and all other states fall in between! If you doubt it, try the math yourself."
    )
    st.subheader("Why is this necessary?")
    st.write(
        "Imagine that we wanted to aggregate data from the previously mentioned survey along with another that details a state-by-state list detailing the number of people within 100,000 below the 100% poverty level, also from the U.S. Census Bureau. It would be impossible to aggregate these two data sets without converting one into the same metric as the other, and this becomes exponentially more difficult as more lists are added. By converting them all with [min-max normalization](https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)), we address this problem. \n\nSome metrics are also what I choose to call “inverse” functions. By this I mean that a lower number is actually good, and a higher number is bad. [Min-max normalization](https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)) easily addresses this by simply inverting the range of the function (i.e. [0,42] -> [42,0]), and now plugging in a higher value produces a lower result."
    )
    st.subheader("What are the benefits?")
    st.write(
        "This system allows you to individually control the weighting of each category. Say you care more about poverty levels compared to the bachelor’s degrees. Set the range of the poverty min-max function to [0,200] (or rather [200,0] because it's inverse) and the range of the bachelor’s degree function to [0,100], and poverty is worth double the weight of bachelor’s degrees! If you wanted to get rid of the bachelor’s degrees entirely, set the range to [0,0]. [Min-max normalization](https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)) allows for a degree of granularity otherwise not possible."
    )
    st.subheader("How do I use it?")
    st.write(
        "On the left, there should be a few titled boxes to input numbers. You can input any number between 1 and 1000, and I invite you to do so now if you haven’t already. When you input a number in that box, you are changing the maximum [or minimum if the data set is inverse] of the function to the inputted value. You should see the graph on the right update in response. The graph on the right is called a [choropleth map](https://en.wikipedia.org/wiki/Choropleth_map) ([despite the visual similarity, it is not a heat map](https://www.standardco.de/notes/heatmaps-vs-choropleths)). The intensity of the blue color in each state on the map is inversely proportional to its score value (calculated by adding up the points it received in each category on the left based on your input ranges). Essentially, lighter blue = better score. You can see the specific score associated with each state by hovering over said state, along with zooming and moving around the map. When you changed those variables, you also should have noticed the text at the bottom that says “Your current code is XXXX” change. This code system is designed to facilitate easy retention and distribution of scores among others despite the fact that this is a web app primarily. This code is based off of the numbers you input into the boxes on the left. At this point I invite you to remember or copy your code, refresh the page, input the code into the box that says “If you have a code, put it here!”, and press enter on your keyboard or hit “Apply.” You should see numbers identical to the ones before refreshing your page!"
    )
    st.write("\n\n\n")
    st.write("Happy data analysis!\n\n-Link")


if __name__ == "__main__":
    main()
