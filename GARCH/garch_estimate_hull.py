import finpy_tse as fpy
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize

# initial guess of GARCH(1,1) model parameters
params = (0.1, 0.1, 0.9)  # ω, α, β

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
df['ui(%)'] = (df['Adj Close'] - df['Adj Close'].shift(1)) / df['Adj Close'].shift(1)
df['ui(%)'] = df['ui(%)'] * 100

# normalization of stock returns
min_max_scaler = StandardScaler()  # min_max Method
min_max_scaler.fit(df[['ui(%)']])
df['normal_ui'] = min_max_scaler.transform(df[['ui(%)']])


# optimization using Maximum Likelihood Method
def objective_function(params, df):
    omega, alpha, beta = params
    # checking the stationarity constraint satisfaction
    lambdaa = 1 - alpha - beta
    if lambdaa < 0:
        return np.inf
    ui = df['normal_ui'].values
    ui = ui[1:]
    sygma_two = np.zeros_like(ui)
    sygma_two[0] = ui[0] ** 2
    for i in range(1, len(ui)):
        # GARCH(1,1) with initial parameters
        sygma_two[i] = omega + (alpha * ui[i - 1] ** 2) + (beta * sygma_two[i - 1])
    df['σ²'] = float('NaN')
    df.loc[1:, 'σ²'] = sygma_two
    # objective function
    df["-(− ln(vi) − u²i / vi)"] = float('NaN')
    df.loc[1:, '-(− ln(vi) − u²i / vi)'] = -1 * ((-1 * np.log(sygma_two)) - (ui ** 2 / sygma_two))
    # data cleaning
    df = df.fillna(0)
    df = df.replace([np.inf, -np.inf], 0)
    print(f"""
        sum of last column : {df["-(− ln(vi) − u²i / vi)"].sum()}
    """
          )
    return df["-(− ln(vi) − u²i / vi)"].sum()


# Define the bounds for omega, alpha, and beta
bnds = ((-np.inf, np.inf), (0, 1), (0, 1))

# minimization
print('Iterations : ')
result = minimize(
    objective_function,
    np.array(params),
    args=(df,),
    # constraints=(const,),
    # bounds=bnds,
    method='Nelder-Mead',
    # method='SLSQP',
    # method='Powell',
    options={'disp': True, 'maxiter': 10100},
)
# long term variance
VL = result.x[0] / (1 - result.x[1] - result.x[2])

# showing result
print(
    f"""
                                                    GARCH(1,1) RESULTS
        ---------------------------------------------------------------------------------------------------------
        ---------------------------------------------------------------------------------------------------------
        initial guess : 
        ω = {params[0]}
        α = {params[1]}
        β = {params[2]}
        -------------------------------------------------
        Method : \"Maximum Likelihood Estimate(MLE)\"
        -------------------------------------------------
        SCIPY estimate of optimum value of parameters :
        ω = {result.x[0]}
        α = {result.x[1]}
        β = {result.x[2]}
        lambda = {(1 - result.x[1] - result.x[2])}
        stationarity constraint : 
        α + β + lambda = {result.x[1] + result.x[2] + (1 - result.x[1] - result.x[2])}
        -------------------------------------------------
        SCIPY optimization success = {result.success}
        SCIPY optimization message :
        \"{result.message}\"
        -------------------------------------------------
        Long term Variance(VL) and long term volatility:
        VL = ω / (1 - α - β) = {VL}
        long term volatility = {(VL ** 0.5) * 100} %
        
    """
)
print(
    """
    Data Frame based on optimized parameters:
    """
)
print(df[['Ticker', 'Adj Close', 'ui(%)', 'normal_ui', 'σ²', '-(− ln(vi) − u²i / vi)']])
print('code by A.h. Nejadkoorki')
