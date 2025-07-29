import streamlit as st


def main():
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
