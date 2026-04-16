# This file was made in session 6

# Taken from last session which I missed!
# I've added notes about bits I've added in this session 6

# We need to install sf nova from the Extensions
# We are going to make an app that takes the processing we did for the 903
# but allows users without Python to access it.

import streamlit as st
import pandas as pd
from enum import Enum

from dateutil.relativedelta import relativedelta
from datetime import datetime
# Session 6 - numpy does maths stuff
import numpy as np

import plotly.express as px

# Session 6 - We've done hard coding below for session variables
# Session Variables
collection_year = 2014
collection_end = datetime(collection_year, 3, 31)


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

    # let's write a function to do this, we can sue this elsewhere too, for instance
    # if finding percentage of referrals NFA with other returns
    output = percent_of_col_with_value(df, "on_both", measure_name)

    return output
 
# Session 6 - Additions below 

# Main app starts here
 # Main app
 # streamlit api - Type into Google and it tells you docs of how to write streamlit doc
 st.title("903 Processing app")

# Now go to sf-nova new extension icon on LHS then click 'Launch preview'