import os
import pandas as pd
from sqlalchemy import create_engine

#--- file configuration ----

DATA_DIR = r"C:\Users\poorn\Learning\Project\internation_debt_analysis\raw.py"

#--data conf--

DB_USER = "root"
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "International_debt"

# Make sure the password exists before trying to connect.
if not DB_PASSWORD:
    raise RuntimeError(
        "MYSQL_PASSWORD environment variable is not set."
    )

engine = create_engine(
    f"mysql+pymysql://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}"
) #Connecting part

#4.load raw data and meta data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

raw = pd.read_csv(
    os.path.join(BASE_DIR, "ids_cleaned_long.csv"),
    encoding="latin1"
)
cmeta = pd.read_csv(
    os.path.join(DATA_DIR, "IDS_CountryMetaData.csv"),
    encoding="latin1"
)

smeta = pd.read_csv(
    os.path.join(DATA_DIR, "IDS_SeriesMetaData.csv"),
    encoding="latin1"
)

print("CSV files loaded successfully.")

#----------------------------------------------------------------------------------------------------------------------------------------------

## -- Countries.df--> Countries table

countries_df = cmeta[["Code", "Table Name", "Region", "Income Group"]].copy()
# select only the 4 source columns we need; .
#.copy() create an independent dataframe
# without it pandas will treat as a view of cmeta
 
countries_df.columns = ["Country_Code", "Country_Name", "Region", "Income_group"]
# rename columns to match Countries table's column names EXACTLY (schema.sql is case-sensitive on column names in some MySQL configs)
 
countries_df["Country_Code"] = countries_df["Country_Code"].str.strip()
# removes any leading/trailing spaces, same fix as before
 
countries_df = countries_df.drop_duplicates(
    subset=["Country_Code"], keep="first"
)
# safety net -- ensures one row per country before inserting (PRIMARY KEY requires uniqueness)
 
countries_df = countries_df[countries_df["Income_group"].notna()]
print(f"countries_df: {len(countries_df):,} rows")

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 
## Indicator.df --> Indicator table

indicators_df = smeta[["Code","Indicator Name","Topic","Aggregation method"]].copy() # Select only the required columns from smeta and create a separate DataFrame copy.
# Double brackets are used because we are selecting multiple columns.
indicators_df.columns = ["Series_Code","Series_Name","Topic","Aggregation_Method"]
indicators_df["Series_Code"] = indicators_df["Series_Code"].str.strip()
indicators_df = indicators_df.drop_duplicates(subset=["Series_Code"],keep="first")
# Remove duplicate rows based on Series_Code, keeping the first occurrence.
print(f"indicators_df:{len(indicators_df):,}Rows")
#:, with commas as thousands seperator

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#debt_data.df

raw["Country Code"] = raw["Country Code"].str.strip()   # whitespace fix, same as before, just in case
raw["Series Code"] = raw["Series Code"].str.strip()

before = len(raw)   # remember row count before filtering, to report how many were dropped and why

debt_data_df = raw[
    raw["Series Code"].isin(indicators_df["Series_Code"])      # keep only rows whose indicator exists in Indicators
    & raw["Country Code"].isin(countries_df["Country_Code"])   # AND whose country exists in Countries
].copy()
print(f"Dropped {before - len(debt_data_df):,} rows with no matching country/indicator (FK safety)")

debt_data_df = debt_data_df.drop_duplicates(subset=["Country Code", "Series Code", "year"], keep="last")
debt_data_df = debt_data_df.rename(
    columns={"Country Code": "Country_Code", "Series Code": "Series_Code", "value": "Value"}
    # rename to match Debt_Data's exact column names: Country_Code, Series_Code, year, Value
)[["Country_Code", "Series_Code", "year", "Value"]]   # keep only the 4 columns Debt_Data actually needs, in order


print(f"debt_data_df: {len(debt_data_df):,} rows")

# --- 2. REMOVE NON-DEBT ROWS & CLEAN VALUES FOR SQL ---

# Define the non-monetary series codes to remove
exclude_codes = ["SP.POP.TOTL", "FI.RES.TOTL.MO", "FI.RES.TOTL.DT.ZS"]

# Filter out the unwanted codes
debt_data_df = debt_data_df[
    ~debt_data_df["Series_Code"].isin(exclude_codes)
].copy()
#-------------------------------------------------------------------------------------------------------------------------------------------------------
# New: Strip symbols and format 'Value' as numeric so it complies with SQL data types (INT/DECIMAL/FLOAT)
debt_data_df["Value"] = debt_data_df["Value"].astype(str)
debt_data_df["Value"] = debt_data_df["Value"].str.replace(
    "$", "", regex=False
)
debt_data_df["Value"] = debt_data_df["Value"].str.replace(
    ",", "", regex=False
)
debt_data_df["Value"] = pd.to_numeric(debt_data_df["Value"], errors="coerce")

print(f"Final clean debt_data_df for SQL: {len(debt_data_df):,} rows")

#PUSH TO MYSQL

countries_df.to_sql(
    "countries",          # target table name -- must match schema.sql exactly
    engine,                 # the connection object created earlier
    if_exists="append",      # add rows to the existing table instead of recreating it
    index=False,               # don't write pandas' row index as an extra column
    method="multi",             # batches multiple rows per INSERT statement -- much faster
    chunksize=500                # rows per batch
)
print("Loaded Countries")
 
indicators_df.to_sql("indicators", engine, if_exists="append", index=False, method="multi", chunksize=500)
print("Loaded Indicators")
 
# Debt_Data is over a million rows -- chunked to avoid one giant INSERT statement
debt_data_df.to_sql("debt_data", engine, if_exists="append", index=False, method="multi", chunksize=5000)
print("Loaded Debt_Data")
 
print("\nAll tables loaded successfully.")
#$env:MYSQL_PASSWORD="your_mysql_password"