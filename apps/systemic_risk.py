
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

import datetime
import pandas as pd
import numpy as np

def serve_layout():

    recession_dates = [
        ('1973-11-30', '1975-03-31'),
        ('1980-01-31', '1980-07-31'),
        ('1981-07-31', '1982-11-30'),
        ('1990-07-31', '1991-03-31'),
        ('2001-03-31', '2001-11-30'),
        ('2007-12-31', '2009-06-30'),
        ('2020-02-29', '2020-06-30'),
    ]


    ar = pd.read_csv('data/absorption_ratio.csv')
    ar_shapes=[
        {
            'type': 'rect',
            'x0': r[0],
            'y0': 0,
            'x1': r[1],
            'y1': 1,
            'xref': 'x',
            'yref': 'paper',
            'line': {'color': 'blue', 'width': 0},
            'fillcolor': '#5DADE2',
            'opacity': 0.2,
        } for r in recession_dates


    ]

    ar_data = [{'x': ar['date'],
                'y': ar['ar'],
                'type': 'line_markers',
                'marker': {'color': '#EC7063'},
                }]
    ar_layout={'height': 400,
               'margin': {'t': 0},
               'yaxis': {'range': [0.5, 1.0]},
               'shapes': ar_shapes}


    ar_fig={'data': ar_data, 'layout': ar_layout, }

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

            html.Br(),
            html.Br(),

            # "FRONT PAGE"
            dbc.Row([

               dbc.Col([

                   html.Br(),
                   html.Br(),
                   html.Br(),

                   html.Div('''QuantViews Pro | Replicating the paper:''', style={'fontSize': '1.5rem', 'fontWeight': 'bold', 'color': '#26BE81'}),
                   html.Div([
                       html.Span('''Principal Components as a Measure of Systemic Risk'''),
                       ],style={'fontSize': '4rem', 'fontStyle': 'normal', 'lineHeight': '110%'}),

                   html.Br(),
                   html.Br(),
                   html.Br(),

               ], width=7, style={'text-align': 'center'}),

                dbc.Col('', width=1, style={'border-right': '2px solid black'}),

                dbc.Col([
                    html.Div('''Original Authors:'''),
                    html.Div('''Mark Kritzman, Yuanzhen Li, Sébastien Page and Roberto Rigobon''', style={'margin-left': '20px'}),
                    html.Br(),

                    html.Div('Links:'),
                    html.A('''Journal of Portfolio Management''', href='https://jpm.pm-research.com/content/37/4/112', style={'margin-left': '20px'}),
                    html.Br(),

                    html.A('''SSRN''', href='https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1582687', style={'margin-left': '20px'}),
                    html.Br(),
                    html.Br(),

                    html.Div('About QuantViews Pro'),
                    html.Br(),

                    html.Div('Last Updated:'),
                    html.Div('June 2020',style={'margin-left': '20px'})

                ], width=4, style={'color': 'black', 'text-align': 'left', 'fontSize': '1.25rem'})

            ], style={'height': '30%'}),


            html.Br(),

            # RESEARCH INTRO AND CONCLUSION
            dbc.Row([

                # left column
                dbc.Col([

                    html.H1('Original Research', style={'color': '#26BE81', 'text-align': 'center'}),

                    html.H5('''The authors devise a measure of systemic risk, the Absorption Ratio (AR) that describes
                    the degree to which assets are being driven by common underlying risk factors. In addition to describing
                    the current level of systemic risk, the authors also claim that shifts in the AR (using a z-score) can
                    signal future market returns.
                    ''', style={'text-align': 'left', 'lineHeight': '200%'})

                ], width=5),

                dbc.Col('', width=2),

                # right column
                dbc.Col([

                    html.H1('Replication Effort', style={'color': '#26BE81', 'text-align': 'center'}),

                    html.H5('''Our replication finds that the authors' conclusions are plausible though we found lower
                    effect magnitudes on an in-sample replicated dataset. We also extended the analysis to a longer time
                    period and continued to find predictive power in AR shifts but the benefit has declined.''', style={'lineHeight': '200%'})

                ],width=5),

            ], style={'margin': '2%', 'text-align': 'left', 'color': 'grey', 'lineHeight': '200%'}),

        html.Br(),
        html.Br(),


        html.Hr(style={'border': '1px solid grey'}),

        html.Br(),
        html.Br(),

        html.H3('Theory and Intuition', style={'text-align': 'left', 'color': 'grey'}),

        html.Br(),
        html.Br(),

        html.Div([

            html.P('''The authors devise a measure of systemic risk that describes the degree to which assets
            are being driven by common underlying risk factors.'''),

            html.P('''
            For example, in an environment characterized by
            low systemic risk there are a million different things affecting the stock market: AAPL will be driven
            by iPhone sales while T-Mobile will be driven by regulatory risk from the Sprint merger. Elsewhere Bank of
            America will be driven by
            the risk of rising mortgage delinquencies. In this scenario each stock is driven
            by a separate narrative. In contrast, in an environment characterized by high systemic risk the range
            of narratives narrow and we find that the same story is driving AAPL, TMS and BOA: They are all down because
            investors are scared of a pandemic that will shut down the economy.'''),

            html.P('''It is important to note that from this perspective high levels of systemic risk does not necessarily mean
            that returns have been low nor will they be low in the future. When assets are tightly coupled however,
            there is a risk that an adverse event could propagate widely across the entire market.
            For example, if in 2020 a wide variety of asset prices are rising due to common
            support from low interest rates and stimulative fiscal policy, then if confidence in continued
            government support was to be undermined it is conceivable that the whole market would fall.'''),

            html.P('''In this sense, systemic risk is a measure of fragility. It will indicate whether the market is made
            of glass but not whether there is anyone swinging a hammer.'''),


            html.P('''From a technical standpoint, the measure of a common underlying factor is calculated using
            principal component analysis (PCA). The authors use daily stock returns of 50 industries from 1997 to 2010.
            For each date, they use the trailing two years of data to calculate principal components and
            the variance of each principal component is calculated using exponentially-decaying weights over the prior two
            years. The Absorption Ratio then is the total variance of the first 10 principal components (1/5th of the
            original number of features) as a fraction of the original total variance of the 50 sector returns.
            '''),

            html.P('''As calculated using this method, the AR is a measure of how much of the variation across
            the 50 industries is "explained" by common factors and is therefore driven by systemic risk.
            '''),

            html.P('''Finally, the authors use changes in the Absorption Ratio (z-score) to signal potential
            market movements in the future. They found that, on average, a sudden rise in systemic risk tends to be
            followed by low returns while sudden drops in systemic risk are followed by periods of higher returns. '''),



        ], className='multi-column', style={'lineHeight': '200%', 'fontSize': '1.25rem'}),

        html.Br(),
        html.Br(),

        html.H3('''Replicated Absorption Ratio (Extended History)''', style={'text-align': 'left', 'margin-bottom': '0%'}),
        dcc.Graph(id='absorption-ratio', figure=ar_fig),

        html.Br(),
        html.Br(),

        html.H2('Summary', style={'color': 'grey'}),

        ], style={'margin': '0% 5% 0% 5%', 'text-align': 'left'}),

    ]

layout = serve_layout