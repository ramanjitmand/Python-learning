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
from utils import clean_903_table
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
    dfs[key] = clean_903_table(df, ...)

print(dfs['header'])