import pandas as pd
import numpy as np

def recession_start_end_list(data):
    '''
    make a list of lists that details recessions start and end dates
    ex: [[rec_date_start, rec_date_end], [rec_date_start, rec_date_end], ...]

    :param data: a dataframe that contains at least columns 'date' and 'recession' where
    recession is a binary 0/1 indicator of a recession
    :return: each recession start and end date, as list
    '''

    df = data[['date', 'recession']].copy()
    df.sort_values(by='date', inplace=True)
    df.reset_index(inplace=True, drop=True)

    # init a list to store recessions
    recessions = []

    # only keep rows (dates) that were under a recession
    df = df.query('recession==1')

    # convert the dataframe into a list of named tuples
    # each named tuple will represent a row of the recession dataframe
    # (this will just be easier to iterate over)
    months = list(df.itertuples())

    current_recession = []
    first = True

    # iterate through months
    for i in range(len(months) - 1):

        # get the current month and the next month
        _curr = months[i]
        _next = months[i + 1]

        # if first month of a recession, then append the date to get the start date
        if first:
            current_recession.append(_curr.date)
            first = False

        # if not the first month of a recession
        else:
            # if not the last month of a recession do nothing
            # (because the next recession month immediately follows the current month
            # and is therefore part of the same recession)
            if _curr.Index == (_next.Index - 1):
                pass

            # otherwise, this month is the last month of the current recession
            # let's 'close' the recession and reset
            else:
                current_recession.append(_curr.date)
                recessions.append(current_recession)
                current_recession = []
                first = True

    # add the close date of the last recession
    current_recession.append(months[len(months) - 1].date)
    recessions.append(current_recession)
    return recessions

def analyze_into_recessions(data, col, preceding_months=60, trailing_months=60):
    '''
    make a dataframe that shows how a variable behaved leading into and out of a recession.
    The dataframe will have a relative date column (..., -3, -2, -1, 0, ,1, 2, 3, ...)
    and then columns for each recession.
    '''

    assert col in data.columns, f'error: the selected col {col} is not in the dataset'
    assert 'recession' in data.columns, 'error: recession indicator missing in the dataset'

    df = data.copy()
    df.sort_values(by='date', inplace=True)
    df.reset_index(inplace=True, drop=True)

    # get the recessions and store as a list of lists:
    # [[rec_date_start, rec_date_end], [rec_date_start, rec_date_end], ..]
    recessions = recession_start_end_list(df)
    num_recessions = len(recessions)

    # iterate through each recession and capture the t1 preceding periods
    # and t2 trailing periods relative to the start date of the recession
    result = pd.DataFrame({'relative_date': []})
    for recession in recessions:

        # get the start and end dates of each recession
        start = recession[0]
        end = recession[1]

        # get the index of the start date of the recession
        # (what row of the dataset is the start date in?)
        temp = df.copy()
        idx = temp[temp['date'] == start].index[0]

        # make a new column that shows the number of periods the date is relative to the start date
        temp['relative_date'] = np.NaN
        temp.loc[idx, 'relative_date'] = 0

        # label each date as the number of relative observations before the start of the recession
        for i in range(1, preceding_months + 1):
            # ex: if the observation five periods forward is the start date (0th period), then
            # this period is the -5th period
            mask = temp['relative_date'].shift(-i) == 0
            temp.loc[mask, 'relative_date'] = -i

        # label each date as the number of relative observations after the start of the reservatino
        for j in range(1, trailing_months + 1):
            # ex: if the observation five periods prior is the start date (0th period), then
            # this period is the 5th period
            mask = temp['relative_date'].shift(j) == 0
            temp.loc[mask, 'relative_date'] = j

        # format results
        recession_label = start.strftime('%Y-%m')
        temp.rename(columns={'date': 'absolute_date_{}'.format(recession_label),
                             col: '{}_{}'.format(col, recession_label)}, inplace=True)

        temp = temp[['relative_date',
                     'absolute_date_{}'.format(recession_label),
                     '{}_{}'.format(col, recession_label)]]
        temp = temp[temp['relative_date'].notnull()]

        result = result.merge(temp, how='outer', on='relative_date')

    result.sort_values(by='relative_date', inplace=True)
    return result



def plot_into_recessions(data, col):
    # 1. get a list of recession end and start dates and extract the start date so that
    # we can refer to each recession series
    # (each data series from analyze_into_recessions is labeled like ust10yminus2y_1980-02,
    # ust10yminus2y_1990-08, etc which gives the variable name and which recession it is showing)
    recessions = recession_start_end_list(data)
    start_dates = [r[0].strftime('%Y-%m') for r in recessions]

    # 2. isolate the variable behavior around each recession
    df = analyze_into_recessions(data, col)

    # get the column names of all the data values
    # (exclude the date-related columns)
    value_columns = [c for c in df.columns if not 'date' in c]

    # 3. generate new columns that give each series indexed to 100 on the start of the recession

    # iterate through each recession
    for recession in start_dates:
        # get the series value at the 0th period for the given recession
        idx0 = df[df['relative_date'] == 0]
        idx0 = idx0[f'{col}_{recession}'].iloc[0]

        # reindex data series
        df[f'{col}_{recession}_index'] = df[f'{col}_{recession}'] / idx0 * 100

    # 4. calculate the average of the series (level)
    df[f'avg_{col}'] = df[value_columns].mean(axis=1)

    # 5. calculate the average of the indexed series
    indexed_columns = [f'{c}_index' for c in value_columns]
    df[f'avg_{col}_index'] = df[indexed_columns].mean(axis=1)

    # 6. make plots

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    # 6a. plot the level values of the series in the first chart
    df.set_index('relative_date')[value_columns].plot(title=f'{col} level values over time',
                                                      color='#DE3C4B',
                                                      alpha=0.15,
                                                      ax=axes[0],
                                                      legend=False)
    df.set_index('relative_date')[f'avg_{col}'].plot(color='#DE3C4B',
                                                     alpha=1.0,
                                                     ax=axes[0],
                                                     legend=False)

    # 6b. plot the indexed values of the series in the second chart
    df.set_index('relative_date')[indexed_columns].plot(title=f'{col} indexed values over time',
                                                        color='#AFBBF2',
                                                        alpha=0.15,
                                                        ax=axes[1],
                                                        legend=False)
    df.set_index('relative_date')[f'avg_{col}_index'].plot(color='#AFBBF2',
                                                           alpha=1.0,
                                                           ax=axes[1],
                                                           legend=False)

    # add vertical lines to show years before and after recessions
    for i in range(-5, 6):
        axes[0].axvline(x=12 * i, linestyle='--', alpha=0.2, color='#49A078')
        axes[1].axvline(x=12 * i, linestyle='--', alpha=0.2, color='#49A078')

    axes[0].axvline(x=0, linestyle='--', alpha=0.8, color='#49A078')
    axes[1].axvline(x=0, linestyle='--', alpha=0.8, color='#49A078')

    return df


def multi_plot_into_recessions(data, series='auto'):
    assert (series in ['all', 'auto']) or isinstance(data, list), 'error, invalid series argument'

    # given the inputted dataframe, search for series to plot
    # (we want to plot unemployment (unrate) but not derivative or meta data columns related to unemployment
    # such as unrate_date, unrate_available_date, unrate_norm, etc)
    if series == 'auto':
        metrics = [col for col in data.columns if (not 'date' in col) and (not 'norm' in col) and (not 'delta' in col)]
    elif series == 'all':
        metrics = data.columns.tolist()
    else:
        metrics = series

    num_metrics = len(metrics)

    for metric in metrics:
        plot_into_recessions(data, metric)