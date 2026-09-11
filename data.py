import pandas as pd
df = pd.read_csv(
	r"C:\Users\poorn\Downloads\drive-download-20260825T050739Z-1-001\IDS_ALLCountries_Data.csv"
	, encoding="latin-1"
) #encoding latin as it pops unicoding error -- we have done file encoding

#cleaned CSV -- Drivelink --https://github.com/poorni-ds/International_debt_Analysis