
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

import datetime
import pandas as pd
import numpy as np
import scipy.stats

from utilities import *
import config
from app import app
from apps import functions as fn
import visdcc


def serve_layout():

    return [

        html.Div([

            dbc.Row([


                dbc.Col([

                    html.Br(),
                    html.Br(),
                    html.Br(),


                    html.Div(['QuantViews'], className='display-1 app-header'),

                    html.Div(['Financial Research and Personal Finance Tools'], className='display-1 text-note'),

                    html.Br(),
                    html.Br(),
                    html.Br(),





                ], width=6),

                dbc.Col([], width=6),

            ]),

            dbc.Row([

                dbc.Col([

                    dbc.Card(
                        [
                            dbc.CardImg(src="/assets/ar_cover.png", top=True, style={'height': '225px'}),
                            dbc.CardBody(
                                [
                                    html.H4("Research Replication: Systemic Risk", className="card-title", style={'height': '55px'}),
                                    html.P(
                                        "Measure systemic risk and market fragility in the US stock market using PCA.",
                                        className="card-text", style={'backgroundColor': 'white', 'color': 'grey', 'height': '55px'},
                                    ),
                                    dbc.CardLink("App", href='/systemic-risk'),
                                    #dbc.CardLink("Blog", href='#'),
                                ], style={'borderTop': '1px solid grey'}
                            ),
                        ],
                        style={'border': '5px #26BE81 solid', 'borderRadius': '25px', 'paddingTop': '3%', 'height': '450px'}, outline=False,
                    )

                ], width=4),

                dbc.Col([

                    dbc.Card(
                        [
                            html.Img(src="/assets/line-chart2.png", style={'maxWidth': 'auto', 'marginLeft': '15%', 'marginRight': '15%', 'marginBottom': '5%', 'height': '225px'}),
                            dbc.CardBody(
                                [
                                    html.H4("On the Merits of Replicable Research", className="card-title", style={'height': '55px'}),
                                    html.P(
                                        "Research needs to be verified. Let's do that.",
                                        className="card-text", style={'color': 'grey', 'height': '55px'},
                                    ),
                                    dbc.CardLink("Blog", href='https://jbortfeld.medium.com/replicable-research-in-finance-adb0b6387c3f'),
                                ], style={'borderTop': '1px solid grey'}
                            ),
                        ],style={'border': '5px #26BE81 solid', 'borderRadius': '25px',  'paddingTop': '3%', 'height': '450px'},
                    )

                ], width=4),

                dbc.Col([

                    dbc.Card(
                        [
                            dbc.CardImg(src="/assets/retirement_planning_cover.png", top=True, style={'height': '225px'}),
                            dbc.CardBody(
                                [
                                    html.H4("Retirement Planning in Easy Mode", className="card-title",  style={'height': '55px'}),
                                    html.P(
                                        "Quick personal finance projections from five easy questions.",
                                        className="card-text", style={'color': 'grey', 'height': '55px'}
                                    ),
                                    dbc.CardLink("App", href='/retirement-planning-in-easy-mode'),
                                    dbc.CardLink("Blog", href='https://medium.com/@jbortfeld/an-easy-app-for-retirement-planning-59dcf37be97'),
                                ], style={'borderTop': '1px solid grey'}
                            ),
                        ], style={'border': '5px #26BE81 solid', 'borderRadius': '25px',  'paddingTop': '3%', 'height': '450px'},
                    )



                ], width=4),

            ]),

        ], style={'margin': '0% 5% 0% 5%'})

    ]


layout = serve_layout