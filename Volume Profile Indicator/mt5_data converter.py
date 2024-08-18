import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('USDCHF_M1_202407290001_202408070000.csv', delimiter='\t')
df['DateTime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'], format='%Y.%m.%d %H:%M:%S')
df = df.rename(
    columns={'<OPEN>': 'Open', "<HIGH>": "High", '<LOW>': 'Low', '<CLOSE>': 'Close',
             '<VOL>': 'Vol', '<TICKVOL>': 'Volume', '<SPREAD>': 'Spread'})


# Drop the original DATE and TIME columns
df.drop(columns=['<DATE>', '<TIME>'], inplace=True)
df.set_index("DateTime", inplace=True)
df.index = pd.to_datetime(df.index)

to_excel = False
to_csv = True

if to_excel:
    path = "USDCHF.xlsx"
    df.to_excel(path, index=True, sheet_name="Sheet1")
if to_csv:
    path = "USDCHF.csv"
    df.to_csv(path, index=True)

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(df)

