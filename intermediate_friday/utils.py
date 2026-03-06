import pandas as pd
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