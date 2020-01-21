import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd
import math
from utilities import *

import config
from app import app
from apps import recession_paths
from apps import nav_bar
from apps import markets_in_rear_view

# APP HEADER
# this will appear as the header of every page of the app

this_page_header = html.Div([

    # website header
    html.H1(children='QIS - Quantitative Investment Strategy (v0.2)',
            style={'backgroundColor': config.colors['background'],
                   'color': config.colors['font'],
                   'margin-bottom': 0}),

    html.Div(children='''A ROI Project - To Reproduce, Open-source and Improve Investment Research''',
            style={'backgroundColor': config.colors['background'],
                   'color': config.colors['font'],
                   'font-size': 20}),

], style = {'backgroundColor': config.colors['background'], 'border': '1px solid pink'})


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    html.Div(this_page_header),

    html.Br(),

    html.Div([

        html.Div(nav_bar.nav_bar, style={'width': '8.%',
                                         'display': 'inline-block',
                                         'vertical-align': 'top',
                                         'background-color': '#183463',
                                         'border': '1px solid purple'
                                         }),

        html.Div(id='page-content', style={'width': '91.666%',
                                           'display': 'inline-block',
                                           'vertical-align': 'top',
                                           })

    ], style={'border': '1px solid green'})

], style = {'backgroundColor': config.colors['background'],
            'margin': -10,
            'padding': 10})


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return recession_paths.layout
    if pathname == '/markets_in_rear_view':
        return markets_in_rear_view.layout()
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)