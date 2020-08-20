
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

import datetime
import pandas as pd
import numpy as np

def serve_layout():


    ar = pd.read_csv('data/absorption_ratio.csv')
    ar_data = [{'x': ar['date'],
                'y': ar['pc1'],
                'type': 'line_markers',
                'marker': {'color': '#267B83'}}]
    ar_layout={'height': 400,
               'title': 'Absorption Ratio'}

    ar_fig={'data': ar_data, 'layout': ar_layout}

    turb = pd.read_csv('data/turbulence.csv')
    turb['turbulence'] = turb['turbulence'].rolling(window=120).mean()
    turb_data = [{'x': turb['date'],
                'y': turb['turbulence'],
                'type': 'bar',
                'marker': { 'color': '#50D890'}}]
    turb_layout = {'height': 400,
                 'title': 'Financial Turbulence'}

    turb_fig = {'data': turb_data, 'layout': turb_layout}

    return [
        html.Div([

        html.H1('Systemic Risk Measures (DEMO ONLY)'),
        html.Br(),
        html.H4('''Based on 'Principal Components as a Measure of Systemic Risk' by Kritzman,
         Li, Page and Rigobon (2010)'''),
        html.Br(),
        html.Div('''The Absorption Ratio (AR) measures the degree to which different assets are being driven by a common
        factor. When assets are "tightly coupled", there is a risk that an adverse event could propagate widely across
         the entire market. For example, it is argued that in 2020 a wide variety of asset prices are rising
          due to common support from low interest rates and stimulative fiscal policy. If confidence in continued
          government support was to be undermined, then it is conceivable that the whole market would fall.
          From a technical standpoint, the AR is the fraction of total
        variance explained by variation in the first principal component.'''),
        html.Br(),
        html.Div('''Here we reproduce the AR from the paper which originally covered the period from 1998 to 2010
        and extend the history. Our calculation of AR is based on a rolling 2Y of daily equity returns across
        49 US Industry Groups.'''),

        html.Br(),
        dcc.Graph(id='absorption-ratio', figure=ar_fig),
        html.Br(),

        html.Div('''Turbulence is a measure of systemic surprise in financial asset returns, either because asset
        returns are deviating from the recent normal levels or because correlation across assets is changing. The
        original paper generated the turbulence metric using returns across asset classes (including stocks, bonds,
        real estate and commodities) and regions and covered the period from 1980 to 2010. Below we apply the
        methodology to the same 49 US industry groups above using the trailing 2Y of daily returns. '''),

        html.Br(),
        dcc.Graph(id='turbulence-ratio', figure=turb_fig),
        html.Br(),




        ], style={'text-align': 'left', 'margin': '5%'})
    ]

layout = serve_layout