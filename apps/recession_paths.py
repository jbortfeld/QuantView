
import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import math
from utilities import *
import config

# slate grey: 3f4d5e


var_names ={'unrate': 'Unemployment Rate',
            'consumer_conf': 'Consumer Confidence',
            'business_conf': 'Business Confidence',
            'ust10yminus2y': 'Slope of the Yield Curve (10Y minus 2Y)',
            'inflation': 'Inflation',
            'c0a0': 'IG Spreads',
            'h0a0': 'HY Spreads',
            'vix': 'VIX'}

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
                      'line': {'color': config.colors['line']},
                      'opacity': 0.25,
                   'showlegend': False} for recession in start_dates]

    chart_data.append({'x': df['relative_date'],
                      'y': df[f'avg_{col}'],
                       'name': 'Average',
                      'mode': 'lines',
                      'line': {'color': config.colors['line']},
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
                                          'color': config.colors['chart_title']},
                                'font': {'family': 'Courier New, monospace',
                                         'color': config.colors['axis_label']},
                                'plot_bgcolor': config.colors['plot_background'],
                                'paper_bgcolor': config.colors['paper_background'],
                                'xaxis': {'linecolor': config.colors['axis'],
                                          'zeroline': True,
                                          'zerolinecolor': config.colors['zero_vertical'],
                                          'tickvals': xaxis_ticks},
                                'yaxis': {'linecolor': config.colors['axis'],
                                          'zeroline': False}}
                     },
        style = {'width': '50%', 'display': 'inline-block'}),

    ]

    if col2 != None:
        row_list.append(
            dcc.Graph(
                figure={'data': build_chart_data(df, col2),

                     'layout': {'title': {'text': var_names[col2],
                                          'color': config.colors['chart_title']},
                                'font': {'family': 'Courier New, monospace',
                                         'color': config.colors['axis_label']},
                                'plot_bgcolor': config.colors['plot_background'],
                                'paper_bgcolor': config.colors['paper_background'],
                                'xaxis': {'linecolor': config.colors['axis'],
                                          'zeroline': True,
                                          'zerolinecolor': config.colors['zero_vertical'],
                                          'tickvals': xaxis_ticks},
                                'yaxis': {'linecolor': config.colors['axis'],
                                          'zeroline': False},}
                     },
            style={'width': '50%', 'display': 'inline-block'})

        )


    return html.Div(row_list, className='row')


##############################################
###############################################
# BUILD THE CONTENTS OF THE PAGE
##############################################
###############################################

# CONTENT
# add content to the page
# define the variables to display in the app

this_page_content = [
    # app description
        html.Div([

            # left - app description
            html.Div([
                html.Div(children='''Historical Downturn Analysis: The Path of a Recession''',
                         style={'font-size': 24}),

                html.Div(children='''What does a recession look like? Economic contractions are, thankfully, rare
                                  occurrences but that means we may have a hard time recognizing when we are
                                  heading into or perhaps already in the midst of one. These charts illustrate how economic indicators
                                  behaved in the five years period preceding and trailing the five historical US recessions since 1980.



                                  Optionally overlay the current trailing five years of each indicator to compare how
                                  well the current economic environment compares to the archetypal path to recession.

                                  ''',
                         style={'font-size': 20})
            ], style={'color': config.colors['discussion_text'],
                      'width': '50%',
                      'display': 'inline-block',
                      'vertical-align': 'top' }),

            # right - page description
            html.Div([
                html.Div(children='''Data Sourcing''',
                         style={'font-size': 24, 'color': config.colors['discussion_text_2']}),

                html.Div(children='''All data originates from open source databases and we share both our data
                                  and our code. We share the data, the python code that downloads the data, the code
                                  in jupyter notebooks that analyze the data, and free web apps (like this one!) so
                                  that all people with an interest in the subject matter can engage with the material even
                                  if you don't have a programming background.

                                  ''',
                         style={'width': 600, 'color': config.colors['discussion_text_2']}),

                html.Div(children='''DATA UPDATED THROUGH: 2019-12-31
                                  ''',
                         style={'width': 600, 'color': '#E4BE9E'})

            ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),



        ], style={'backgroundColor': config.colors['background']}, className = 'row')

]

vars_to_plot = ['unrate', 'ust10yminus2y',
                'consumer_conf', 'business_conf',
                'c0a0', 'h0a0',
                 'vix',
                ]

# if odd number of vars, then add a placeholder (because we want two vars in each row)
if not len(vars_to_plot) % 2 == 0:
    vars_to_plot.append(None)

# make a list of lists that give all the rows to make and the two vars that go into each row
vars_in_rows = []
for i in range(0,len(vars_to_plot), 2):
    vars_in_rows.append([vars_to_plot[i], vars_to_plot[i+1]])

this_page_content.append(html.Br())
for row in vars_in_rows:
    this_page_content.append(build_row(df, row[0], row[1]))


# set the layout of this page
this_page = [

             html.Div([

                 html.Div(this_page_content, style={'width': '91.666%', 'display': 'inline-block'})

             ], className = 'row')
]

def serve_layout():

    return [html.Div(style={'backgroundColor': config.colors['background'],
                         'border': config.border,
                                  },
                  children=this_page)]


layout = serve_layout





