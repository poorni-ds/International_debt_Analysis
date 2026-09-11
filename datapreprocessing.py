from data import df
import pandas as pd


# -- filtering the relevant columns --
id_cols = ["Country Name", "Country Code", "Series Name", "Series Code"]
year_cols = [str(y) for y in range(2000, 2025)] # Convert year column names to strings
df = df[id_cols + year_cols] # combining the required columns for further analysis
df_long = df.melt(
    id_vars=id_cols, # telling pandas this column should remain as they are
    value_vars=year_cols, # take these values and transform them
    var_name="year", #becomes a new column called year
    value_name="value" #The actual numbers from those year columns go into a new column called value.
)

#-- datatype conversion & data cleaning--

df_long["Country Code"] = df_long["Country Code"].str.strip() # this removes the leading and the trailing spaces if any
df_long["Country Name"] = df_long["Country Name"].str.strip()
df_long["Series Name"] = df_long["Series Name"].str.strip()
df_long["Series Code"] = df_long["Series Code"].str.strip()

df_long["year"] = pd.to_numeric(df_long["year"], errors="coerce").astype("Int64") # ierrors="coerce" doesn't itself "prevent the code from crashing" in every situation; specifically, it tells pd.to_numeric() to replace values that cannot be converted with NaN.
#---- Capital Int64--- Int64 is Pandas' nullable integer data type. It allows the column to contain integer values as well as missing values
df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")

#-- handling the missing values--
df_long.isna().sum() # give the sum of missing values

# Country Name        75
# Country Code       125
# Series Name        125
# Series Code        125
# year                 0
# value           327640
# dtype: int64

(df_long.isna().mean() * 100).round(2) # gives the percentage of the missing datas

# Country Name     0.00
# Country Code     0.01
# Series Name      0.01
# Series Code      0.01
# year             0.00
# value           20.81
# dtype: float64

df_long = df_long.dropna(subset=["Country Name","Series Name"])
#drop if either of the value is missing in the dataset

df_long = df_long.drop_duplicates(subset=["Country Name","Series Name","year"])
# remove the duplicate rows where the combination of country name, series name and year is repeated
# In pandas drop_duplicates keeps the first occurance and removes the subsequent duplicates

import numpy as np

df_long = df_long.sort_values(["Country Code", "Series Code", "year"]).reset_index(drop=True)

# a "known" column that's only populated where value isn't missing --
# this is what ffill/bfill will carry forward/backward within each group
df_long["known_year"] = df_long["year"].where(df_long["value"].notna()).astype("float64")
df_long["known_value"] = df_long["value"]

g = df_long.groupby(["Country Code", "Series Code"])
df_long["ffill_year"] = g["known_year"].ffill()    # nearest known year at or before this row
df_long["ffill_value"] = g["known_value"].ffill()  # its value
df_long["bfill_year"] = g["known_year"].bfill()    # nearest known year at or after this row
df_long["bfill_value"] = g["known_value"].bfill()  # its value

dist_f = (df_long["year"].astype("float64") - df_long["ffill_year"]).abs()
dist_b = (df_long["bfill_year"] - df_long["year"].astype("float64")).abs()

# pick whichever neighbor is closer in time; ties go to the earlier (forward) value
use_forward = dist_f.fillna(np.inf) <= dist_b.fillna(np.inf)
nearest_value = np.where(use_forward, df_long["ffill_value"], df_long["bfill_value"])

df_long["value"] = df_long["value"].fillna(pd.Series(nearest_value, index=df_long.index))
df_long = df_long.drop(columns=["known_year", "known_value", "ffill_year", "ffill_value", "bfill_year", "bfill_value"])

print(f"Final shape: {df_long.shape}")
print(f"Remaining missing values: {df_long['value'].isna().sum()}")

df_long.to_csv("ids_cleaned_long.csv", index=False)
print("Saved: ids_cleaned_long.csv")