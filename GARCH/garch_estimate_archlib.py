import finpy_tse as fpy
import pandas as pd
import numpy as np
from arch.univariate import arch_model, ConstantMean, GARCH, Normal

# info about the stock`s data
stock_name = 'فولاد'
start_date = '1380-01-01'
end_date = '1402-01-01'
stock_english_name = 'S*Mobarakeh.Steel'

# getting data and preparation
base_df = fpy.Get_Price_History(
    stock=stock_name,
    start_date=start_date,
    end_date=end_date,
    adjust_price=True,
    double_date=True,
)
base_df = base_df.reset_index()
base_df = base_df.rename(columns={'index': 'J-Date'})
base_df['Date'] = pd.to_datetime(base_df['Date'], format="%Y-%m-%d")
base_df['Date'] = base_df['Date'].apply(lambda x: x.replace(hour=12, minute=30))
base_df['Adj Close'] = base_df['Adj Close'].astype(np.longdouble)

# copying required columns into the df
df = base_df[[
    'Date', 'Adj Close'
]].copy()
df.insert(loc=0, column='Ticker', value=f"{stock_english_name}")

# calculating simple return
df['ui'] = (df['Adj Close'] - df['Adj Close'].shift(1)) / df['Adj Close'].shift(1)
df['ui'] = df['ui'] * 100


am = arch_model(df['ui'].iloc[1:], vol="GARCH", mean='constant', p=1, o=0, q=1, dist="normal")
res = am.fit()
print(res.summary())
print("code by A.H. Nejadkoorki")