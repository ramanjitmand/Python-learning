# Session on Fri 06/03/2026
# Today we'll start our .py file (normal Python file) not .ipynb like last week

# Control + j to open your terminal (if you don't have this already)

# pip is used to install packages like pandas
# Type pip install pandas in terminal
# Then pip install sqlalchemy

# Format/order we do our coding:
# import statements
# session variables
# classes
# functions
# main script

import pandas as pd
from sqlalchemy import (
    create_engine,
    inspect,
    text,
    select,
    MetaData,
    Table,
)

# Add this once utils made below
# Added group_calculation on 13/03/2026 in line below
# Added group_calculation_year and appears_on_both to line below on Fri 20/03/2026
from utils import (
    clean_903_table,
    group_calculation,
    time_difference,
    group_calculation_year,
    appears_on_both,
)
from datetime import datetime

# You can click and drag files if you've put them in the wrong bit in file structure on LHS

# Let's now create engine, server, drivers for server, connect method on engine, inspect and then add data tables to...

# Initialise Session variables
# Copy path from 903_database.db file
# You can use double or single quotes, doesn't matter
filepath = "/workspaces/Python-learning/intermediate_friday/data/903_database.db"

# We'll add collection year variable later
# The year the collection was in (let's pretend 2014)
collection_year = 2014
# Turn into a time stamp uisng datetime function which you have to import
# 2014, 03, 31
collection_end = datetime(collection_year, 3, 31)

# Read in 903 data frpm SQL db
# Need to make an engine - you can't call it 903_engine as it can't start with a number
# We'll only have 1 engine so could've just called it engine_903 but hey lol
# Method 1 - engine_903 = create_engine("sqlite+pysqlite:///" = filepath)
# Method 2 below has f strings which WLP prefers
# Make an engine to read database
engine_903 = create_engine(f"sqlite+pysqlite:///{filepath}")
# Set up connection to 903 db
connection = engine_903.connect()
# Inspect db
inspection = inspect(engine_903)

# This will give a list of table names
table_names = inspection.get_table_names()
# Let's check if it works!
print(table_names)

# Let's run this
# Best practice isn't using run button on the RHS
# Easiest way to run individual file is to copy 903 db file path then paste it in the terminal
# Didn't work for me - said Permission denied, oh well
# Someone had the same problem so I followed him and WLP when they went through it and I got it fixed! Basically you had to kill your
# terminals using '...' on RHS where Python is (click 'Python' underneath that to do this) and then type 'interpret' in search bar at
# the top and click on Python 3.12.1 bit (you'll be on another one which you don't want to be on)

metadata_903 = MetaData()

# Uncomment to check database connection
# print(table_names)
# In dictionaries we have key-value pairs
dfs = {}
# table = Table(table_name, metadata_object, engine)
for table in table_names:
    # Everything needs to be indented to be part of 'for' and same for 'with'
    # print(table)
    current_table = Table(table, metadata_903, autoload_with=engine_903)
    with engine_903.connect() as con:
        # current_table will change with each table
        stmt = select(current_table)
        result = con.execute(stmt).fetchall()
    dfs[table] = pd.DataFrame(result)
# For every table make a table, then connect to 903 db, take everything from there, then put into a dictionary called dfs as a df
# result is a df

# Uncomment to check reading of tables as dfs
# print(dfs.keys())
# print(dfs.values())

# Clean all tables in 903
# By end of this lesson we need to make all dates into dates, add ethnic main code (not WROM), age, and age bucket
# Let's do for loop
# dfs.items returns key and value as separately named things
for key, df in dfs.items():
    # dfs[key] = some kind of cleaning e.g. by writing a function in another file and writing that here
    # In another file as same director/folder as this intermediate_friday one make a utils.py file and fill it out (see utils.py file here)
    dfs[key] = clean_903_table(df, collection_end)

# print(dfs['header'])

# Below is from session 3 (Fri 13/03/2026)

# grouped = dfs['header'].groupby('ETHNICITY')
# print(grouped)
# Not working for me - some problem on line 28 in utils from last session lol

# grouped = dfs['header'].groupby('ETHNICITY').size()
# print(type(grouped))

# grouped = grouped.to_frame('Count')
# print(grouped)

# grouped = dfs['header'].groupby('ETHNICITY').size()
# grouped = grouped.to_frame('Count').reset_index()
# print(grouped)

# grouped['Percentage'] = grouped['Count'] / grouped['Count'].sum() * 100
# On a row wise basis, take row in row and divide by sum of whole column - will give 'Percentage' column

# print(grouped['Percentage'].sum())

# output_1 = group_calculation(dfs['header'], 'ETHNICITY', "Header - Ethnicities")
# output_2 = group_calculation(dfs['header'], 'AGE_BUCKETS', "Header - Age")
# print(output)

measures_dict = {}

measures_dict["Heady by Ethnicity"] = group_calculation(
    dfs["header"], "ETHNICITY", "Header - Ethnicities"
)

measures_dict["Header by Age"] = group_calculation(
    dfs["header"], "AGE_BUCKETS", "Header - Age"
)

output_table = pd.concat(list(measures_dict.values()))


# Let's do second part by doing difference in date times
# Add a new column by putting ['...']
# We did _dt bits last time (session 2)
# dfs['missing']['MISSING_DURATION'] = dfs['missing'].apply(
# lambda gets the whole row, and we need to find...
#     lambda row: relativedelta(row['MIS_START_dt'], row['MIS_END_dt']), axis=1)

# WLP put this in somewhere don't know where - from dateutil.relativedelta import relativedelta

# WLP put this in somewhere don't know where - from dateutil.relativedelta import relativedelta

# Missed below...
# dfs['missing']['MISSING_DURATION'] = time_difference(dfs['missing']['MIS_START_dt'], dfs['missing']['MIS_END_dt'], business_days=True)
# print(dfs['missing'])

# We haven't applied buckets for MISSING_DURATION in business days - e.g. MISSING DURATION BUCKETS
# Different measures are used with different buckets in children's services, so we'll need to write 5 buckets and apply the one we want

# There are ways in which you're meant to format in Python, e.g. classes are where each word is capitalised at start etc
# When using functions, have a space between arguments/parameters, but for equals don't have a space
# Have a space when you're writing a variable
# Let's import a package which can do this cleaning for us
# pip install black - put into terminal
# Then in terminal type 'black <PATH OF THIS 903 FILE' then do for utils.py as well
# Both of mine didn't work lol

# I think below done in session 4 when I missed first 10 mins
dfs["missing"]["MISSING_DURATION"] = time_difference(
    dfs["missing"]["MIS_START_dt"], dt["missing"]["MIS_ENF_dt"], business_days=True
)

# Session 4 and below for sure here-
measures_dict["Multiple episodes"] = multiples_same_event(
    dfs["episodes"], event_name="Number of episodes"
)

# Let's add a new DECOM_YEAR??
dfs["episodes"]["DECOM_YEAR"] = dfs["episodes"]["DECOM_dt"].dt.year

measures_dict["Episodes starting per year"] = group_calculation(
    dfs["episodes"], "DECOM_YEAR", "Episodes starting per year"
)
# print(measures_dict["Episodes starting per year"])
# We can add this data to a line chart
# It'd be good to see how things are broken down so let's do this

# We need to parse/pass our df through group_calculation_year and other things
# def group_calculation_year(df, year_col, col_to_group, measure_name):
#     pass

output = group_calculation_year(
    dfs["episodes"], "DECOM_YEAR", "PLACE", "Placments by year"
)

# df1 is first in brackets
output = appears_on_both(
    dfs["episodes"], dfs["missing", "CYP with episodes who have been missing"]
)
print(output)

# Type black . into terminal to format everything you've done - it'll change most things you have to follow PEP 8 (style guidelines for Python) guidelines (from year 2001)
# Coders in past used to just make 10-15 year old coding better but it was a boring job lol
# black won't fix syntax errors