import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import math
from utilities import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# slate grey: 3f4d5e

colors = {
    'background': '#0C1B33',
    'plot_background': '#0C1B33',
    'paper_background': '#0C1B33',
    'line': '#03B5AA',
    'line2': '#FF6978',
    'line3': '#A42CD6',
    'font': '#03B5AA',
    'axis': 'white',
    'title': '#0C1B33',
    'zero_vertical': 'red'
}

var_names ={'unrate': 'Unemployment Rate',
            'consumer_conf': 'Consumer Confidence',
            'business_conf': 'Business Confidence',
            'ust10yminus2y': 'Slope of the Yield Curve (10Y minus 2Y)',
            'inflation': 'Inflation',
            'c0a0': 'IG Spreads',
            'h0a0': 'HY Spreads',
            'vix': 'VIX',
            'gdp_growth_pp_saar': 'GDP Growth'
            }

xaxis_ticks=[-60,-48,-36,-24,-12,0,12,24,36,48,60]

def id_generator(id, base):

    ''' return a string that gives the name of an object'''

    return f'{base}_{id}'

df = pd.read_pickle('macro_series_monthly_data.pkl')
col = 'unrate'


# 1. get a list of recession end and start dates and extract the start date so that
# we can refer to each recession series
# (each data series from analyze_into_recessions is labeled like ust10yminus2y_1980-02,
# ust10yminus2y_1990-08, etc which gives the variable name and which recession it is showing)
recessions = recession_start_end_list(df)
start_dates = [r[0].strftime('%Y-%m') for r in recessions]


def build_chart_data(df, col):
    # 2. isolate the variable behavior around each recession
    df = analyze_into_recessions(df, col)

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

    chart_data = [{'x': df['relative_date'],
                      'y': df[f'{col}_{recession}'],
                   'name': f'{recession} recession',
                      'mode': 'lines',
                      'line': {'color': colors['line']},
                      'opacity': 0.25,
                   'showlegend': False} for recession in start_dates]

    chart_data.append({'x': df['relative_date'],
                      'y': df[f'avg_{col}'],
                       'name': 'Average',
                      'mode': 'lines',
                      'line': {'color': colors['line']},
                      'opacity': 1.0,
                       'showlegend': False})

    return chart_data

def build_row(df, col1, col2):

    '''
    return a html.Div() that contains two charts in a row. This automates and standardizes
    the process of adding a row of charts to the html layout of a page

    :param df:
    :param col1:
    :param col2:
    :return: an html.Div() object with a row of two charts
    '''

    row_list = [

        dcc.Graph(
            figure={'data': build_chart_data(df, col1),

                 'layout': {'title': {'text': var_names[col1],
                                      'color': colors['title']},
                            'font': {'family': 'Courier New, monospace',
                                     'color': 'white'},
                            'plot_bgcolor': colors['plot_background'],
                            'paper_bgcolor': colors['paper_background'],
                            'xaxis': {'linecolor': colors['axis'],
                                      'zeroline': True,
                                      'zerolinecolor': colors['zero_vertical'],
                                      'tickvals': xaxis_ticks},
                            'yaxis': {'linecolor': colors['axis'],
                                      'zeroline': False}}
                 },
            style={'width': '50%', 'display': 'inline-block'}),
    ]

    if col2 != None:
        row_list.append(
            dcc.Graph(
                figure={'data': build_chart_data(df, col2),

                     'layout': {'title': {'text': var_names[col2],
                                          'color': colors['title']},
                                'font': {'family': 'Courier New, monospace',
                                         'color': 'white'},
                                'plot_bgcolor': colors['plot_background'],
                                'paper_bgcolor': colors['paper_background'],
                                'xaxis': {'linecolor': colors['axis'],
                                          'zeroline': True,
                                          'zerolinecolor': colors['zero_vertical'],
                                          'tickvals': xaxis_ticks},
                                'yaxis': {'linecolor': colors['axis'],
                                          'zeroline': False},}
                     },
            style={'width': '50%', 'display': 'inline-block'})

        )


    return html.Div(row_list, className='row')


############################################################################################
# BUILD THE CONTENTS OF THE PAGE
# construct a list and append new html objects into the list. You can then insert this list
# into an html.Div() object that defines the page layout
this_page = [

    # website header
    html.H3(children='QIS - Quantitative Investment Strategy Applications and Research Group',
            style={'backgroundColor': colors['background'],
                   'color': colors['font']}),

    html.H5(children='A ROI Project - Reproduce, Open-source and Improve Investment Research',
            style={'backgroundColor': colors['background'],
                   'color': colors['font']}),

    # app description
    html.Div([

        # left - app description
        html.Div([
            html.Div(children='''Historical Downturn Analysis: The Path of a Recession''',
                     style={'backgroundColor': colors['background'],
                            'color': '#79C99E', 'font-size': 24}),

            html.Div(children='''What does a recession look like? Economic contractions are, thankfully, rare
                              occurrences but that means we may have a hard time recognizing when we are
                              heading into or perhaps already in the midst of one. These charts illustrate how economic indicators
                              behaved in the five years period preceding and trailing the five historical US recessions since 1980.

                              Optionally overlay the current trailing five years of each indicator to compare how
                              well the current economic environment compares to the archetypal path to recession.

                              ''',
                     style={'width': 600, 'color': '#79C99E'})
        ], style={'width': '50%', 'display': 'inline-block'}),

        # right - page description
        html.Div([
            html.Div(children='''Data Sourcing''',
                     style={'backgroundColor': colors['background'],
                            'color': '#E4BE9E', 'font-size': 24}),

            html.Div(children='''All data originates from open source databases and we share both our data
                              and our code. We share the data, the python code that downloads the data, the code
                              in jupyter notebooks that analyze the data, and free web apps (like this one!) so
                              that all people with an interest in the subject matter can engage with the material even
                              if you don't have a programming background.

                              ''',
                     style={'width': 600, 'color': '#E4BE9E'}),

            html.Div(children='''DATA UPDATED THROUGH: 2019-12-31
                              ''',
                     style={'width': 600, 'color': '#E4BE9E'})

        ], style={'width': '50%', 'display': 'inline-block'}),



    ], className = 'row')

    ]

############################################################################################

# add content to the page
# define the variables to display in the app
vars_to_plot = ['unrate', 'ust10yminus2y',
                'consumer_conf', 'business_conf',
                'c0a0', 'h0a0',
                'gdp_growth_pp_saar']

# if odd number of vars, then add a placeholder (because we want two vars in each row)
if not len(vars_to_plot) % 2 == 0:
    vars_to_plot.append(None)

# make a list of lists that give all the rows to make and the two vars that go into each row
vars_in_rows = []
for i in range(0,len(vars_to_plot), 2):
    vars_in_rows.append([vars_to_plot[i], vars_to_plot[i+1]])

for row in vars_in_rows:
    this_page.append(build_row(df, row[0], row[1]))

############################################################################################

# set the layout of this page
app.layout = html.Div(style={'backgroundColor': colors['background']},
                             children=this_page)



if __name__ == '__main__':
    app.run_server(debug=True)