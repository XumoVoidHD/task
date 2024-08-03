import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('USDJPY_M1_202407290001_202408022358.csv', delimiter='\t')
df['DateTime'] = pd.to_datetime(df['<DATE>'] + ' ' + df['<TIME>'], format='%Y.%m.%d %H:%M:%S')
df = df.rename(
    columns={'<OPEN>': 'Open', "<HIGH>": "High", '<LOW>': 'Low', '<CLOSE>': 'Close',
             '<VOL>': 'Volume', '<TICKVOL>': 'Tick Volume', '<SPREAD>': 'Spread'})



# Drop the original DATE and TIME columns
df.drop(columns=['<DATE>', '<TIME>'], inplace=True)
df.set_index("DateTime", inplace=True)
df.index = pd.to_datetime(df.index)

path = "USDJPY.xlsx"
df.to_excel(path, index=True, sheet_name="Sheet1")
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(df)

