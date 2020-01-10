import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
from utilities import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

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


def build_chart(df, col):
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




app.layout = html.Div(style={'backgroundColor': colors['background']},
                             children=[

    html.H1(children='Quantitative Strategy Applications and Research Group',
            style={'backgroundColor': colors['background'],
                   'color': colors['font']}),

    html.Div(children='''Historical Recession Analysis: Walking into a Downturn''',
             style={'backgroundColor': colors['background'],
                    'color': colors['font']}),


    html.Div([

        dcc.Graph(
            figure={'data': build_chart(df, 'unrate'),

                    'layout': {'title': {'text': 'Unemployment Rate',
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

        dcc.Graph(
            figure={'data': build_chart(df, 'ust10yminus2y'),

                    'layout': {'title': {'text': 'Slope of Term Structure (10Y minus 2Y)',
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

    ], className='row'),

    html.Div([

        dcc.Graph(
            figure={'data': build_chart(df, 'consumer_conf'),

                 'layout': {'title': {'text': 'Consumer Confidence',
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

        dcc.Graph(
            figure={'data': build_chart(df, 'business_conf'),

                 'layout': {'title': {'text': 'Business Confidence',
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

    ], className='row'),



    ])





if __name__ == '__main__':
    app.run_server(debug=True)