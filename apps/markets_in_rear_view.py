
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt

import pandas as pd
import math
from utilities import *
import config


var_params = {'unrate': {'label': 'Unemployment Rate', 'weight': .08333},
             'inflation': {'label': 'Inflation', 'weight': .08333},
             'consumer_conf': {'label': 'Consumer Confidence', 'weight': .125},
             'business_conf': {'label': 'Business Confidence', 'weight': .125},
             'gdp_growth_pp_saar': {'label': 'GDP Growth', 'weight': .08333},
             'vix': {'label': 'Implied Vol (VIX)', 'weight': .125},
             'c0a0': {'label': 'Corporate IG Spreads', 'weight': .0625},
             'h0a0': {'label': 'Corporate HY Spreads', 'weight': .0625},
             'ust2y': {'label': 'UST 2Y', 'weight': .0625},
             'ust10y': {'label': 'UST 10Y', 'weight': .0625},
             'ust10yminus2y': {'label': 'Term Structure Slope', 'weight': .0625},
             'sp500_trailing_pe': {'label': 'S&P 500 Earnings Yield', 'weight': .0625},
             'sp500_forward_pe': {'label': 'S&P 500 Forward P/E', 'weight': .0625},
             }

var_names = {k: v['label'] for k,v in var_params.items()}
var_weights ={ k: v['weight'] for k,v in var_params.items()}

print(var_weights)

def serve_layout():

    data = pd.read_pickle('economic_states.pkl')
    print(data.columns)
    print(data['METRIC'])
    data['BENCH WEIGHT'] = data['METRIC'].map(var_weights)
    data['METRIC'] = data['METRIC'].map(var_names)
    print(data['BENCH WEIGHT'])
    # format for display
    for c in data.columns:
        if c != 'METRIC':
            data[c] = data[c].map(lambda x: round(x,2))

    table_columns_1 = [
        {'id': i, 'name': i} for i in ['METRIC']
    ]

    table_columns_2 = [
        {'id': i, 'name': i} for i in ['WEIGHT']
    ]

    table_columns_3 = [
        {'id': i, 'name': i} for i in ['BENCH WEIGHT',
                                       'VALUE', 'VALUE (NORM)',
                                       'DELTA 1Y', 'DELTA (NORM)',
                                       'MEDIAN', 'MAX', 'MIN',
                                       'DELTA MEDIAN', 'DELTA MAX', 'DELTA MIN'
                                       ]
        ]



    content = [

        html.Div([

            html.Div([
                dt.DataTable(columns = table_columns_1,
                             data=data.to_dict('rows'),
                             style_header={'background-color': config.colors['background'],
                                           'color': config.colors['table_font'],
                                           'font-weight': 'bold'},
                             style_cell={'background-color': config.colors['background'],
                                         'color': config.colors['table_font'],
                                         'text-align': 'left',
                                         },
                             style_as_list_view=True,
                             style_data = {'border': '0px solid white'},
                             editable=True
                             ),
            ], style={'display': 'inline-block'}),

            html.Div([
                dt.DataTable(columns=table_columns_2,
                             data=data.to_dict('rows'),
                             style_header={'background-color': 'yellow',
                                           'color': config.colors['table_font'],
                                           'font-weight': 'bold'},
                             style_cell={'background-color': 'yellow',
                                         'color': config.colors['table_font'],
                                         'min-width': '60px',
                                         'width': '60px',
                                         'max-width': '60px'},
                             style_as_list_view=True,
                             style_data={'border': '0px solid white'},
                             editable=True
                             ),
            ], style={'display': 'inline-block'}),

            html.Div([

                dt.DataTable(columns=table_columns_3,
                             data=data.to_dict('rows'),
                             style_header={'background-color': config.colors['background'],
                                           'color': config.colors['table_font'],
                                           'font-weight': 'bold',
                                           },
                             style_cell={'background-color': config.colors['background'],
                                         'color': config.colors['table_font'],
                                         },
                             style_as_list_view=True,
                             style_data={'border': '0px solid white'},
                             style_table={'overflowX': 'scroll'},
                             editable=False
                             )

            ], style={'display': 'inline-block', 'width': '400px'})

        ], className='row', style={'width': '50%'})

    ]


    return content

layout = serve_layout