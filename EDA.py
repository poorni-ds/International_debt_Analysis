from datapreprocessing import df_long
import pandas as pd

smeta = pd.read_csv(
    r"C:\Users\poorn\Downloads\drive-download-20260825T050739Z-1-001\IDS_SeriesMetaData.csv",
    encoding="latin1"
)
cmeta = pd.read_csv(
    r"C:\Users\poorn\Downloads\drive-download-20260825T050739Z-1-001\IDS_CountryMetaData.csv",
    encoding="latin1"
)
df_long = df_long.merge(
    cmeta[["Code", "Income Group", "Region"]],
    left_on="Country Code", right_on="Code", how="left", suffixes=("", "_c")
)
#-- sorting the values--

df_long.groupby("Country Name")["value"].sum().sort_values().head() # -----least 10 countries-----

df_long = df_long.merge(
    smeta[["Code", "Topic", "Aggregation method"]], # required columns in the series meta data
    left_on="Series Code", #match the existing records from the right to to the left and the missing value columns will be present
    right_on="Code",
    how="left"# explained at the top
)

#----spliting the indicators by aggregation method____

# Split the indicators into separate groups based on their aggregation method so each category can be processed using the appropriate aggregation rule.

summable = df_long[df_long["Aggregation method"] == "Sum"] #This creates a new DataFrame containing only rows whose metadata says Sum.  
# Filter df_long to keep only the rows where the Aggregation method is "Sum".
ratios   = df_long[df_long["Aggregation method"] == "Weighted average"] #"Give me only the rows where the aggregation method is Weighted average."
# Filter df_long to keep only the rows where the Aggregation method is "weighted average".




#-- grouping the topic--before going into individual indicator

real_countries = summable[summable["Income Group"].notna() & (summable["year"] <= 2024)] # From summable, select rows where Income Group is not empty
# and the relevant year is up to 2024.
# the dataset contains both individual countries and World Bank aggregate groups.
#The World Bank publishes statistics not only for individual countries, but also for groups of economies so analysts can compare broader categories.

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

print("1. Country-wise debt distribution (Sum indicators, real countries only)")

Country_totals = real_countries.groupby("Country Name")["value"].sum().sort_values(ascending= False)
print("\n Top 10 Countries by total debt related value:")
#\n means start a new line before printing the heading.
print(Country_totals 
      .head(10)# from country_totals pick top10 countries
      .apply(lambda x: f"{x:,.0f}"))
# take each value and temporarily call it as x
#, adds thousands seperator
#0f displays zero decimal places

print("\n Bottom 10 countries by Total debt related value:")
print(Country_totals
      .tail(10)
      .apply(lambda x: f"{x:,.0f}"))



#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------        

#Topic-level grouping, then top individual indicators

print("2. Total value by Topic (summable indicators only)")
Topics = (summable
        .groupby("Topic")["value"]
        .sum()
        .sort_values(ascending=False)
)
print(Topics
      .head(8)
      .apply(lambda x: f"{x:,.0f}"))

print("3.Top 10 individual indicator by Topic")
Top_indicators = (summable
                .groupby("Series Name")["value"]
                .sum()
                .sort_values(ascending=False)
                .head(10))
print(Top_indicators
      .apply(lambda x: f"{x:,.0f}"))

#---------------------------------------------------------------------------------------------------------------------------------------------------

#      trend over time + correlation between top indicators 
#     (inserted here -- right after you know which indicators are "top",
#      before moving on to the income-group/region cross-tab)

import matplotlib.pyplot as plt

print("4a. Trend over time -- top 3 indicators, 2000-2024")
Top3_names = Top_indicators.index[:3].tolist()
Trend = (
    summable[summable["Series Name"].isin(Top3_names) & (summable["year"] <= 2024)]
    .groupby(["Series Name", "year"])["value"].sum().reset_index()
)
Trend_pivot = Trend.pivot(index="year", columns="Series Name", values="value").sort_index() # index = rows, columns = columns, values =cells
print(Trend_pivot.tail(5))

fig, ax = plt.subplots(figsize=(9, 5)) 

#   figure contains everything ie., chart,label etc (9,5) 9 inches wide and 5 inches height
#ax is the actual plotting area - one figure with one axes

for col in Trend_pivot.columns: # takes one indicator at each time
    ax.plot(Trend_pivot.index, Trend_pivot[col], marker="o", markersize=3, label=col[:40])
ax.set_title("Global Trend of Top 3 Debt Indicators (2000-2024)") # give this plotting area a title
ax.set_xlabel("Year") 
ax.set_ylabel("Total value (current US$)")
ax.legend(fontsize=7, loc="upper left") # legend tells the reader which indicator represents which line
ax.tick_params(axis="x", rotation=90) # rotates the text to 90 degree so they wont over lap
fig.tight_layout()
fig.savefig("trend_top3_indicators.png", dpi=150)
print("Saved chart: trend_top3_indicators.png")


#--------------------------------------------------------------------------------------------------------------------------------------------------------------


print("5. 'External debt stocks, total' by Income Group and Region (2024)")
 
focus = real_countries[real_countries["Series Name"].str.contains("External debt stocks, total", na=False)]

#From real_countries, keep only the rows whose Series Name contains "External debt stocks, total".

latest = focus[focus["year"] == 2024]   
#From focus, keep only rows where the year is 2024.

print("\nBy Income Group:")
print(latest.groupby("Income Group")["value"].sum().sort_values(ascending=False).apply(lambda x: f"{x:,.0f}"))

#Group all countries according to their Income Group and add their debt values together.

## lambda takes each resulting total value one at a time
# and formats it with commas and no decimal places

print("\nBy Region:")
print(latest.groupby("Region")["value"].sum().sort_values(ascending=False).apply(lambda x: f"{x:,.0f}"))


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

print("6a. Overall statistical summary (Sum indicators only)")
summable["value"].describe().apply(lambda x: f"{x:,.0f}")

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

print("6b. Statistical summary by Income Group")
print(
    real_countries.groupby("Income Group")["value"].describe()[["count", "mean", "50%", "std", "min", "max"]] # as we dont want 25%,75% we have done so
    .rename(columns={"50%": "median"})
)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

print("6c. Statistical summary by Topic")

print(
    summable.groupby("Topic")["value"].describe()[["count", "mean", "50%", "std", "min", "max"]]
    .rename(columns={"50%": "median"})
)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

### link for EDA Result data ######

### https://docs.google.com/document/d/1Cpw2zMVeHypCb4egjbletNN0h-bPZbQ1ogiRSHTH69c/edit?usp=sharing