import finpy_tse as fpy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# giving optimum parameters based on GARCH(1,1)
# ω, α, β respectively
omega, alpha, beta = (0.1266597473919886, 0.1668703358765673, 0.7271260077810778)

# info about the stock`s data
stock_name = 'فولاد'
start_date = '1380-01-01'
end_date = '1402-01-01'
stock_english_name = 'MobarakehSteel'

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

# copying required columns into the volatility_df
volatility_df = base_df[[
    'Date', 'Adj Close'
]].copy()
volatility_df.insert(loc=0, column='Ticker', value=f"{stock_english_name}")

# calculating returns
volatility_df['ui(%)'] = (volatility_df['Adj Close'] - volatility_df['Adj Close'].shift(1)) \
                         / volatility_df['Adj Close'].shift(1)
volatility_df['ui(%)'] = volatility_df['ui(%)'] * 100


# calculating volatility based on Garch(1,1)
ui = volatility_df['ui(%)'].values
ui = ui[1:]
sygma_two = np.zeros_like(ui)
sygma_two[0] = ui[0] ** 2
for i in range(1, len(ui)):
    sygma_two[i] = omega + (alpha * (ui[i - 1] ** 2)) + (beta * sygma_two[i - 1])
volatility_df['σ²(%)'] = float('NaN')
volatility_df.loc[1:, 'σ²(%)'] = sygma_two
volatility_df['volatility(%)'] = volatility_df['σ²(%)'] ** 0.5

print(
    f"""
               {stock_english_name} Volatility Data Frame
    ---------------------------------------------------------------
    ---------------------------------------------------------------       
    """
)
print(volatility_df[['Date', 'Adj Close', 'ui(%)', 'σ²(%)', 'volatility(%)']])
print("code by A.H. Nejadkoorki")

# plotting
plt.switch_backend('qt5Agg')
fig, ax = plt.subplots(figsize=(30, 10))
ax.plot(volatility_df['Date'], volatility_df['volatility(%)'], color='darkred')
ax.set_title(f'Conditional Volatility Of {stock_english_name} During The Time Period', fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('volatility(%)')
ax.legend(['volatility(%)'], loc='best')
plt.tight_layout()
plt.savefig(f'your path')
plt.close()

