import pandas as pd
# Did line below in session 3
import numpy as np
# Import class below
from dateutil.relativedelta import relativedelta
# Add this from having made __init__.py in new config_903 folder
from config_903 import DateCols903, EthnicSubcategories

# Then do this:
def format_dates(column):
    # Replace any blank space with NaT (NaT is N/A)
    # Method 1 - column.replace(" ", pd.NaT)
    # Method 2 better:
    # Arabic keyboard may be different - below says 'any space'
    column.replace(r"^\s*$", pd.NaT, regex=True)
    column = column.fillna(pd.NaT)
    # If there's an error give the error we want it to, not the general error so need to add 'try' on line below and a bit more
    try:
        # Write code to do datetime bit
        # # str needs to be used
        # # 2 digit day and month with 4 digit year
        column = pd.to_datetime(column, format="%d/%m/%Y")
        return column
    # Continue writing error message
    except:
        raise ValueError(
            # Write string on a new line how user has messed up
            # Good to write errors into your code, making them clear so user knows what has gone wrong
                f"Unknown date format in {column.name}, expected dd/mm/YYYY"
                # Blank entries with a space would end up in above so let's sort this out first - see line 9 addition
        )

# Let's add this function
def calculate_age_buckets(age):
    # Used to make age buckets matching published data
    if age < 1:
        return "a) Under 1 year"
    # if is done first then elif bit is 
    # a) helps ordering in dashboarding work
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

# define a function
# DataFrame bit below helps to do...
def clean_903_table(df: pd.DataFrame, collection_end: pd.Timestamp):
    """
    This function takes and cleans...
    """
    # clean_df is a copy of original df 
    clean_df = df.copy()

    # pass
    # print(df)

    # TODO - This let's you write a comment which you need to do later (highlighted blue)

# Let's get column names if index is in df.columns
    if "index" in df.columns:
        # Drop any columns called index - drop works going along (row is 0, column is 1)
        # We are mutating the object - use inplace = TRUE
        # Below stops your overwriting
        clean_df.drop("index", axis=1, inplace=True)

    # Convert date cols to dt
    # In 903 datetime is meant to be of the form ddmmyy(yy?)
    # Error needs to come out for the user 
    # We need a list of column names we want to convert to dates
    # Make a config_903 folder and in that another __init__.py file and add to __init__.py file

    for column in clean_df.columns:
        if column in DateCols903.cols.value:
            # This isn't very clean as we're overwriting - clean_df[column] = pd.to_datetime(clean_df[column], dayfirst=True)
            clean_df[f"{column}_dt"] = format_dates(clean_df[column])
            # I tried running but nothing was happening in terminal... Seems to be a problem in utils

    # TODO add ethnicity main groups col
    # Only in df where there's an ethnicity column 
    if "ETHNIC" in clean_df.columns:
        # Method 1 not very helpful, so just add to init file in config_903 folder - 
        #clean_df['ETHNICITY'] = clean_df['ETHNIC'].map({"WROM":"WHITE",
                                                        # "ABAN":"ASIAN"}
        clean_df['ETHNICITY'] = clean_df['ETHNIC'].apply(
            # Let's write lambda function
            lambda ethnicity: EthnicSubcategories[ethnicity].value
        )

    # TODO add age col
    # To get years you can't subtract one date from another, instead divide by 365.25 but even this isn't accurate if you want exact years
    if "DOB_dt" in clean_df.columns:
        clean_df['AGE'] = clean_df['DOB_dt'].apply(
            lambda dob: relativedelta(dt1=collection_end, dt2=dob).normalized().years
        )
    # First person in 2014 was 6 - can see when you run but running wasn't working for me

    # TODO add age buckets col
    clean_df['AGE_BUCKETS'] = clean_df['AGE'].apply(calculate_age_buckets)
    # Writing as a lambda will be massive so let's not do that

    return clean_df

# def group_calculation():
#     pass

def group_calculation(df, column):
    grouped = df.groupby([column]).size()
    grouped = grouped.to_frame('Count').reset_index()

    grouped['Percentage'] =  (grouped['Count'] / grouped['Count'].sum() ) * 100

    return grouped
# We need to put things into PBI or Tableu etc 
# DfE test data - time_period, time_identifier etc is always the same 
# We want to see number, rate, and value (categorical data)
# Another schools dataset - breakdowns; we want long data rather than wide data
# Slicer will choose a measure then our visuals will show different values on x-axis and count on y-axis
# Naming will be seen in next session

# Take grouped df and rewriting over it with another df of the same name
# Rename column to 'Value'
# Let's order so it stacks the way we want it to
    grouped = grouped.rename(columns={column:'Value'})
    # Let's add another variable which we'll then parse
    grouped['Measure'] = measure_name
    grouped_ordered = grouped[["Measure", 'Value', 'Coount', 'Percentage']]
    return grouped_ordered

def time_difference(start, end, business_days=False):
    if business_days:
        # pass
        # datetime64[D] is a numpy [num - pie] thing so we have to import numpy at top of this file
        time_diff = np.busday_count(start.astype('datetime64[D]'), end)
    else:
    time_diff = end - start
    time_diff = time_diff / pd.Timedelta(days=1)

    return time_diff

# You don't have to understand all code you do - lol

# Done below in session 4
# None of this worked like it hasn't been in previous session lol
def multiples_same_event(df, event_name)
    df = df.copy()
    # groupby is method used to group stuff
    # To have as a normal df do size on it - size gives you the counts
    multiples = df.groupby("CHILD").size().to_frame("Number of events").reset_index()
    # Let's make into a measure
    # Let's reassign to multiples
    multiples = multiples.groupby(["Number of events"]).size().to_frame("Children with number of events").reset_index()
    # You'll get 2 columns - 'Number of events' and 'Children with number of events' when you do return multiples on line below
    multiples['Event type'] = "Number of episodes"
    # Adds 'Event type' column - cell could say e.g. 'Number of episodes' when you do return multiples on line below
    multiples = multiples[["Event type", "Number of events", "Children with number of events"]]
                          
    return multiples

# Python dashboards need wide data (we'll cover in week 6) but PowerBI wants long data 

def group_calculate_year(df, year_col, col_to_group, measure_name):
    df = df.copy()

    grouped = df.groupby([year_col, col_to_group]).size()
    grouped = grouped.to_frame("Count").reset_index()
    # 4 columns (0, 1, 2 on LHS; DECOM_YEAR; Value ; Count) when you do return grouped on line below
    grouped = grouped.rename(columns[col_to_group:"Value"])
    
    # We want to apply to the whole row (earlier in the code we used lambda to do apply for just 1 part)
    # axis = 1 means we're going on columns not rows or vice versa?
    grouped["percentage by year"] = grouped.apply(
        # x refers to the whole row
        # We want to divide so need to put in / sign
        # grouped.loc let's us use square bracket notation to make a selection and do more interesting things
        # grouped.loc bit - We want grouped df where value in year column is same as year column
        # Let's rename the column using .Count.sum (basically put name of column at start)
        lambda x: x["Count"] / grouped.loc[grouped[year_col] == x[year_col]].Count.sum()
        *100,
        axis=1
        )

# Let's put in our measure name
grouped["Measure"] = measure_name

# We can't stack 2 tables - we'll do in PBI later

# We want output with columns in the following order
grouped = grouped[[year_col, "Measure", "Value", "Count", "Percentage by year"]]

    return grouped

# Let's see what appears in both tables
def appears_on_both(df1, df2, measure_name):
    # pass
    # For df1 drop rows where children appear multiple times
    df1 = df1.drop_duplicates(subset=["CHILD"]).copy()
    df2 = df2.drop_duplicates(subset=["CHILD"]).copy()

    # We can use Python to compare sets
    # set(df1["CHILD"])

    # Let's merge but only join rows where value in row is in both tables - we'll end up with children in both tables!
    # Do Google search on 'pandas merge type'
    # 1. Inner - gives overlap
    # 2. - Outer - gives everythiing
    # 3. Left - gives left...
    # 4. Right - same as left except do for right instead... 

    merged_df = df1.merge(df2, how="inner", on=["CHILD"])
    # If you do return merged_df it comes up with a horrible looking thing in terminal lol

    # Every child in this table will have a 'Yes' in 'on_both' column
    merged_df["on_both"] = "Yes"
    # Nothings will appear elsewhere for children not in both

    # Let's merge df1 on merged_df
    # We're merging on CHILD - you HAVE to merge using on_both otherwise it won't work! 
    # Let's do a left merge
    df = df1.merge(merged_df[["CHILD", "on_both"]], how="left", on="CHILD")

    return merged_df

    # on_both column says NaN for blanks which we don't like
    # Overwrite by doing this-
    # df = df.fillna({"on_both":"No"})
    # Rather than overwriting df, put new values in it using following-
    df.fillna("on_both":"No"), inplace=True

    output = group_calculation(df, "on_both", "measure_name")

    return output
