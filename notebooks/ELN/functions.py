import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader.data as web


big_drawdowns = [
    {'name': 'tech', 'start': '2000-03-24', 'end': '2002-10-29'},
    {'name': 'gfc', 'start': '2007-10-09', 'end': '2009-03-09'},
    {'name': 'covid', 'start': '2020-02-19', 'end': '2020-03-23'}
]


def get_market_cap(assets: list):
    df = web.get_quote_yahoo(assets)['marketCap']

    return df


def get_equity_prices(assets: list, start_date: str, end_date: str, type: str = 'Close', freq: str = 'daily'):
    '''
    download equity prices from yahoo finance (close or adjusted close) for specified tickers
    '''

    assert type in ['Close', 'Adj Close'], 'invalid type: {}'.format(type)
    assert freq in ['daily', 'monthly'], 'invalid freq: {}'.format(freq)

    df = web.DataReader(assets, 'yahoo', start_date, end_date)[type]

    if freq == 'monthly':
        df = df.resample('M').last()

    # rename date index
    df.index.name = 'date'

    return df


def get_equity_returns(assets: list, start_date: str, end_date: str, type: str = 'Close', freq: str = 'daily'):
    '''
    generate a time series of periodic returns
    '''

    prices = get_equity_prices(assets, start_date, end_date, type, freq)

    return prices / prices.shift(1) - 1.0


def get_cumulative_returns(assets: list, start_date: str, end_date: str, type: str = 'Close', freq: str = 'daily', final: bool = False):
    '''
    generate a time series with cumulative returns
    '''

    returns = get_equity_returns(assets, start_date, end_date, type, freq)
    returns = (1 + returns).cumprod()
    # returns.iloc[0].fillna(1.0, inplace=True)
    returns.iloc[0, :] = 1.0

    if final == True:
        return returns.iloc[-1]

    return returns


def infer_periodicity(df: pd.DataFrame):
    ''' infer the periodicity of a dataset given a dataframe with 'date' as the index
    and return the periodicity scaling factor'''

    assert df.index.name == 'date', 'error: index may not be a date'

    # get the mode time elapsed between observations
    dff = pd.DataFrame({'date': df.index})
    mode = (dff['date'] - dff['date'].shift(1)).mode().iloc[0]

    if mode == pd.Timedelta('1 days'):
        return 252
    elif mode == pd.Timedelta('7 days'):
        return 52
    else:
        return 12


def infer_days_in_first_period(df):
    ''' infer the number of days in the first observatipn of the dataset. For example, if you are
    using a weekly dataset then the number of days in a period is 7. If daily, then 1. But if monthly,
    then the number of days could be 28,29,30,31. In this case determine based on the actual month.

    this function is used mostly when calculating the geometric return (CAGR) of a a monthly datset using
    the calc_mean_returns() function and you need to add in the time elapsed over the first observation.

    '''
    assert df.index.name in ['Date', 'date'], 'error: index may not be a date'

    # get the mode time elapsed between observations
    df = pd.DataFrame({'date': df.index})
    mode = (df['date'] - df['date'].shift(1)).mode().iloc[0]

    if mode == pd.Timedelta('1 days'):
        return 1
    elif mode == pd.Timedelta('7 days'):
        return 7
    else:
        # if monthly, get the number of days in the specific month
        month = df['date'][0].month
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 28


def calc_mean_returns(df: pd.DataFrame, annualize: bool = True, geometric: bool = False):
    '''calculate the mean returns from a dataframe of returns'''

    # 1. calculate the arithmetic mean (the simple average of all observations)
    if geometric == False:
        if annualize == True:
            return df.mean(axis=0) * infer_periodicity(df)

        else:
            return df.mean(axis=0)

    # 2. calculate the geometric mean (the compound annual growth rate)
    # (we assume/override the 'annualize' argument and set this to True)
    cum_returns = (df + 1.0).prod(axis=0)
    elapsed_days = (df.index.max() - df.index.min()).days

    # we need to add on one more period. For example, if we are using monthly data and the first observation
    # is Jan 31, 2016 and the last observation is December 31, 2016 then the diff is only 335 days but in reality
    # the first day that we start accumulating returns starts on December 31, 2015. So let's add one more period to the
    # elapsed_days count
    elapsed_days += infer_days_in_first_period(df)
    return (cum_returns) ** (365 / elapsed_days) - 1.0


def calc_drawdown(df: pd.DataFrame):
    '''
    given a dataframe of cumulative returns, calculate a time series with the drawdown
    '''

    prior_max = df.cummax()
    drawdown = df / prior_max - 1.0
    return drawdown
