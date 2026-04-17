# This file was made in session 6

# Taken from last session which I missed!
# This file is what we have been working on over the last few weeks - this is utils file
# I've added notes about bits I've added in this session 6

# We need to install sf nova from the Extensions
# We are going to make an app that takes the processing we did for the 903
# but allows users without Python to access it.

# Session 6 - API bit comes from streamlit
import streamlit as st
import pandas as pd
from enum import Enum

from dateutil.relativedelta import relativedelta
from datetime import datetime
# Session 6 - numpy does maths stuff
import numpy as np

# Session 6 - Below line was used in beginner session (not intermediate sessions)
# It was causing an error in the sf-nova for me so I commented out the below seeing as we weren't using it anyway
# import plotly.express as px

# Session 6 - We've done hard coding below for session variables
# Session Variables
collection_year = 2014
collection_end = datetime(collection_year, 3, 31)


# Session 6 - config files here
class EthnicSubcategories(Enum):
    WBRI = "White"
    WIRI = "White"
    WIRT = "White"
    WROM = "White"
    WOTH = "White"
    MWBC = "Mixed"
    MWBA = "Mixed"
    MWAS = "Mixed"
    MOTH = "Mixed"
    AIND = "Asian"
    APKN = "Asian"
    ABAN = "Asian"
    AOTH = "Asian"
    BCRB = "Black"
    BAFR = "Black"
    BOTH = "Black"
    CHNE = "Chinese"
    OOTH = "Other"
    REFU = "Refused"
    NOBT = "Not Obtained"


class DateCols903(Enum):
    cols = [
        "DOB",
        "DATE_INT",
        "DATE_MATCH",
        "DECOM",
        "DEC",
        "MC_DOB",
        "MIS_START",
        "MIS_END",
        "DATE_PLACED",
        "DATE_PLACED_CEASED",
        "DATE_PERM",
        "REVIEW",
        "DUC",
    ]


# Session 6 - Below came from utils.py file I think
# Utility functions
def format_dates(column):
    # Will make dates for Y/m/d or d/m/Y
    # The 903 has set date formats so we technically don't need to do this,
    # also pd.to_datetime is intelligent and can work out date formats pretty well,
    # so it's also unnecessary, but it's good to be introduced to the idea of tye/except blocks

    # replaces empty strings that may appear with actual empty cells
    column.replace(r"^\s*$", pd.NaT, regex=True)
    column = column.fillna(pd.NaT)
    try:
        column = pd.to_datetime(column, format="%d/%m/%Y")
        # We can check that it handles empty cells by using below, just whilst building
        # but don't include this in actual code
        # print(column[column.isna()])
        return column
    except:
        raise ValueError(
            f"Unknown date format in {column.name}, expected dd/mm/YYYY or YYYY/mm/dd, please check column"
        )


def calculate_age_buckets(age):
    # Used to make age buckets matching published data
    if age < 1:
        return "a) Under 1 year"
    elif age < 5:
        return "b) 1 to 4 years"
    elif age < 10:
        return "c) 5 to 9 years"
    elif age < 16:
        return "d) 10 to 16 years"
    elif age >= 16:
        return "e) 16 years and over"
    else:
        return "f) Age error"


def clean_903_table(df: pd.DataFrame, collection_end: pd.Timestamp):
    df = df.copy()
    clean_df = df.copy()

    if "index" in df.columns:
        clean_df.drop("index", axis=1, inplace=True)

    for column in clean_df.columns:
        if column in DateCols903.cols.value:
            clean_df[f"{column}_dt"] = format_dates(clean_df[column])

    if "ETHNIC" in df.columns:
        clean_df["ETHNICITY"] = clean_df["ETHNIC"].apply(
            lambda x: EthnicSubcategories[x].value
        )

    if "DOB_dt" in clean_df.columns:
        # print(clean_df['DOB_dt'].max()) - we don't need this, we can just use it to find the latest DOB
        clean_df["AGE"] = clean_df["DOB_dt"].apply(
            lambda x: relativedelta(dt1=collection_end, dt2=x).normalized().years
        )
        clean_df["AGE_BUCKETS"] = clean_df["AGE"].apply(calculate_age_buckets)

    return clean_df


def group_calculation(df, col_to_group, measure_name):
    df = df.copy()
    grouped = df.groupby([col_to_group]).size()
    grouped = grouped.to_frame("Count").reset_index()
    grouped = grouped.rename(columns={col_to_group: "Value"})

    grouped["Percentage"] = (grouped["Count"] / grouped["Count"].sum()) * 100

    grouped["Measure"] = measure_name

    grouped_ordered = grouped[["Measure", "Value", "Count", "Percentage"]]

    return grouped_ordered


def time_difference(start_col, end_col, business_days=False):
    if business_days:
        time_diff = np.busday_count(
            start_col.values.astype("datetime64[D]"),
            end_col.values.astype("datetime64[D]"),
        )
    else:
        time_diff = end_col - start_col
        time_diff = time_diff / pd.Timedelta(days=1)

    return time_diff.astype("int")


def multiples_same_event(df, event_name, multiples_column=False):
    df = df.copy()
    if multiples_column == False:
        multiples = (
            df.groupby(["CHILD"]).size().to_frame("Number of events").reset_index()
        )

    else:
        multiples = (
            df.groupby([multiples_column])
            .size()
            .to_frame("Number of events")
            .reset_index()
        )

    multiples = (
        multiples.groupby(["Number of events"])
        .size()
        .to_frame("Children with number of events")
        .reset_index()
    )

    multiples["Event type"] = event_name

    multiples = multiples[
        ["Event type", "Number of events", "Children with number of events"]
    ]
    return multiples


def group_calculation_year(df, year_col, col_to_group, measure_name):
    df = df.copy()
    grouped = df.groupby([year_col, col_to_group]).size()
    grouped = grouped.to_frame("Count").reset_index()
    grouped = grouped.rename(columns={col_to_group: "Value"})

    grouped["Percentage by year"] = grouped.apply(
        lambda x: x["Count"]
        / grouped.loc[grouped[year_col] == x[year_col]].Count.sum()
        * 100,
        axis=1,
    )

    grouped["Measure"] = measure_name

    grouped_ordered = grouped[
        [year_col, "Measure", "Value", "Count", "Percentage by year"]
    ]

    return grouped_ordered


def percent_of_col_with_value(df, col, measure_name):
    """
    Percentage for yes out of all possible values. If needed for
    just yes/no excluding other, filter before use.
    """
    df = df.copy()
    df[col] = df[col].fillna("No")

    grouped = group_calculation(df, "on_both", measure_name)

    return grouped


def appears_on_both(df1, df2, measure_name):
    """
    Finds unique values in two dataframes and inner merges to find children who are in
    both. Then merges back to the dataframe of interest adding a column highlighting
    whether children appear on both. Returns a dict of percentages.
    """
    df1_unique = df1.drop_duplicates(subset=["CHILD"]).copy()
    df2_unique = df2.drop_duplicates(subset=["CHILD"]).copy()

    merged_df = df1_unique.merge(df2_unique, how="inner", on=["CHILD"])

    merged_df["on_both"] = "Yes"

    df = (
        df1_unique[["CHILD"]]
        .merge(merged_df[["CHILD", "on_both"]], how="left", on=["CHILD"])
        .copy()
    )

    # The below method is better than df['on_both'].fillna("no", inplace=True)
    # as it avoids a chained assignment error
    df.fillna({"on_both": "No"}, inplace=True)

    # let's write a function to do this, we can use this elsewhere too, for instance
    # if finding percentage of referrals NFA with other returns
    output = percent_of_col_with_value(df, "on_both", measure_name)

    return output
 
# Session 6 - Additions below 

# Main pipeline
# Making our app starts here
# Main app
# Let's add the title - that's the first thing we ought to do
# streamlit api - Type this into Google and it tells you docs of how to write streamlit docs
# pandas docs / spotly(?) docs - alternatives you can type into Google which we've done before
# st for streamlit
# Title is '903 pipeline app'
st.title("903 pipeline app")

# Now go to sf-nova new extension icon on LHS then click 'Launch preview'
# Doing this might result in a blank tab opening - if so, close it then click 'Launch preview' again
# requirements.txt file - add 2 lines of coding in there
# Then try launching sf-nova again while you're still in the 903 file you made
# When I tried to launch sf-nova, it came up with error 'ModuleNotFoundError: No module named 'plotly''

# st.file_uploader function
# You can add file types here e.g. csv or whatever to give more info on line below for users
upload = st.file_uploader("Upload 903 here")

# We don't want the app to start running before a user has uploaded a file

# Check if a user has uploaded a file 
if upload:
    # st.write is same as writing... 
    st.write("File uploaded")

# We need an Excel to run this file
# Drag and drop the 903 file WLP put into the chat
# The file isn't opening for me when I do this...
# I used 'Browse' to get the file in, but error appeared saying 'ImportError: Missing optional dependency 'openpyxl'. Use pip or conda to install openpyx

# None - reads all sheets
    dfs = pd.read_excel(upload, sheet_name=None)

    for key, df in dfs.items():
        dfs[key] = clean_903_table(df, collection_end=collection_end)
    
    # We want function to remember the output and not run it again
    # To do this, we need to cache below age bit above - actually no

    # st.table - To format a table
    # st.table(dfs['header'])

    # {} - means empty dictionary
    measures = {}

    # The lines of code below was written in previous sessions
    measures["Header by ethnicity"] = group_calculation(
        dfs["header"], "ETHNICITY", "Header - Ethnicities"
    )

    measures["Header by age"] = group_calculation(
        dfs["header"], "AGE_BUCKETS", "Header - Age"
    )

    measures["ad1 by age"] = group_calculation(dfs["ad1"], "AGE_BUCKETS", "Ad1 - Age")

    # We want to do something similar to DfE so it's easy to slice for PBI dashboards
    # Use concatenate function for pandas
    # Use df for all items we want to concatenate
    # We want to concatenate all - we don't want to list them all out 1 by 1
    output_table = pd.concat(
        list(measures.values())
    )

    # st.table(output_table)

    # [] - new column, list of columns with strings
    # Split by space dash space
    # You have to do n=1 at the end to make the line below work
    output_table[["List", "Measure"]] = output_table["Measure"].str.split(" - ", expand=True, n=1)
    # The following 5 in "" seem to be the new column headings in the output table
    output_table = output_table[["List", "Measure", "Value", "Count", "Percentage"]]

    # st.table(output_table)

    # We need user to be able to download as a csv

    with st.expander("Download output"):
        # We need a download button
        # output_csv - variable name
        output_csv = output_table.to_csv(index=False)
        # Give variable name of csv file output and file name (last 2 in line below)
        st.download_button("Download processed data", output_csv, file_name="Processed 903.csv")
        st.table(output_table)
    # You can download the file at the end if you'd like to
    # The page isn't very nice, but it does what you need it to do
    # If you get an unexpected error, you can reupload the file in sf-nova to see how things change when you Rerun

    with st.expander("Plots"):
        # Make a plotly bar chart in here of header (which is in List column) by age (which is in Measure column)
        # Make 2 expressions
        plot_table = output_table[(output_table["List"] == "Header")
                                  & output_table["Measure"] == "Age"]
        
        # Let's make a plotly bar chart
        bar = px.bar(
            plot_table,
            x="Value",
            y="Count",
            title="Header by age",
            # Parse a dictionary - label the x- and y-axes
            labels={"Value":"Age",
                    "Count":"Number of children"}
        )

        # Add onto the page
        st.plotly_chart(bar)

        # We can't drilldown the data we have because of the nature of it sadly
        # However, we can make the chart interactive

    # Let's make an sidebar(?)/expander(?)
    # with st.sidebar:
        # st.write("Make slices here")
    
    # Missed 12 mins here
    # So, copied/pasted below from WLP's comments in the TEAMS chat

    with st.sidebar:
        st.write("Make slices here")
        
        list_options = output_table["List"].unique()
        list_selected = st.sidebar.radio(
            "Selcted list:", list_options
        )

        measure_options = output_table["Measure"][output_table["List"] == list_selected].unique()
        measure_selected = st.sidebar.radio(
            "Select measure:", measure_options
        )

    with st.expander("SLiced Plots"):
        plot_table = output_table[(output_table["List"] == list_selected)
                                  & (output_table["Measure"] == measure_selected)]
        
        bar = px.bar(
            plot_table,
            x="Value",
            y="Count",
            title=f"{list_selected} by {measure_selected}",
            labels={"Value":measure_selected,
                    "Count":"Number of children"}
        )

        st.plotly_chart(bar, use_container_width=True)
