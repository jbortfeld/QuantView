
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_table as dt
import dash_table.FormatTemplate as FormatTemplate

import datetime
import pandas as pd
import numpy as np

from app import app

def serve_layout():

    custom_tab_selected = {'borderTop': '6px solid #26BE81'}


    # 1. Figure 1: Absorption Ratio level over time
    ar = pd.read_csv('data/absorption_ratio.csv')

    ar_dict = ar[['ar', 'date']].copy()
    ar_dict['date'] = pd.to_datetime(ar_dict['date'])
    ar_dict = ar_dict.set_index('date').to_dict(orient='index')

    def get_ar_value_on_date(ar_dict: dict, date: pd.Timestamp) -> float:

        if date < min(ar_dict.keys()):
            return -99

        if date in ar_dict.keys():
            return ar_dict[date]['ar']
        else:
            return get_ar_value_on_date(ar_dict, date-pd.Timedelta(days=1))

    # build data for recession shading on charts
    recession_dates = [
        ('1973-11-30', '1975-03-31'),
        ('1980-01-31', '1980-07-31'),
        ('1981-07-31', '1982-11-30'),
        ('1990-07-31', '1991-03-31'),
        ('2001-03-31', '2001-11-30'),
        ('2007-12-31', '2009-06-30'),
        ('2020-02-29', '2020-06-30'),
    ]

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

    # build data for event annotions on charts
    annotations = [
        ('1973-10-31', 'Oil Embargo'),
        ('1987-10-31', 'Black Monday'),
        ('1990-08-31', 'Iraq'),
        #('1998-08-31', 'Russia Default'),
        ('1998-09-30', 'LTCM'),
        #('2008-03-14', 'Bear Stearns'),
        ('2008-09-13', 'Lehman'),
        ('2001-09-30', '9/11'),
        ('2020-02-29', 'COVID'),

    ]
    ar_annotations = [
        {'x': a[0],
         'y': get_ar_value_on_date(ar_dict, pd.to_datetime(a[0])) + 0.03,
         'text': a[1],
         'font': {'color': 'red'}
         } for a in annotations

    ]

    ar_data = [{'x': ar['date'],
                'y': ar['ar'],
                'type': 'line_markers',
                'marker': {'color': '#26BE81'},
                }]
    ar_layout={'height': 400,
               'margin': {'t': 5, 'l': 40, 'b': 40},
               'yaxis': {'range': [0.5, 1.0]},
               'shapes': ar_shapes,
               'annotations': ar_annotations}


    ar_fig={'data': ar_data, 'layout': ar_layout, }

    # Figure 2: AR Shift
    ar_shift = pd.read_csv('data/ar_shift.csv')
    ar_shift_dict = ar_shift[['ar_shift', 'date']].copy()
    ar_shift_dict.rename(columns={'ar_shift': 'ar'}, inplace=True)
    ar_shift_dict['date'] = pd.to_datetime(ar_shift_dict['date'])
    ar_shift_dict = ar_shift_dict.set_index('date').to_dict(orient='index')

    ar_shift_annotations = [
        {'x': a[0],
         'y': get_ar_value_on_date(ar_shift_dict, pd.to_datetime(a[0])) + .5,
         'text': a[1],
         'font': {'color': 'red'}
         } for a in annotations

        ]

    ar_shift_data = [{'x': ar_shift['date'],
                'y': ar_shift['ar_shift'],
                'type': 'line_markers',
                'marker': {'color': '#26BE81'},
                },]

    ar_shift_layout = {'height': 400,
                       'margin': {'t': 5, 'l': 40, 'b': 40},
                       'shapes': ar_shapes,
                       'annotations': ar_shift_annotations
                 }

    ar_shift_fig = {'data': ar_shift_data, 'layout': ar_shift_layout, }


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


        dbc.Row([

            dbc.Col(
                html.H2('Theory and Purpose', style={'text-align': 'center', 'color': 'grey'})
            , width=4),

            html.Br(),


            dbc.Col(
                html.P('''The authors devise a measure of systemic risk that describes the degree to which assets
                are being driven by common underlying risk factors.''', style={'lineHeight': '200%', 'fontSize': '1.25rem'})
            , width=8)

        ]),


        html.Br(),
        html.Br(),

        dcc.Tabs(id='theory-purpose-tab', value='tab-1', children=[dcc.Tab(label='Intuition',
                                                                           value='tab-1',
                                                                           selected_style=custom_tab_selected),
                                                                   dcc.Tab(label='Technical',
                                                                           value='tab-2',
                                                                           selected_style=custom_tab_selected),
                                                                   dcc.Tab(label='Code',
                                                                           value='tab-3',
                                                                           selected_style=custom_tab_selected)
                                                                   ]),

        html.Br(),
        html.Br(),

        html.Div(id='theory-purpose-content', style={}),


        html.Br(),
        html.Br(),

        html.Hr(style={'border': '1px solid grey'}),

        html.Br(),
        html.Br(),

        html.H2('Key Result 1: Recognizable Events Correspond to Jumps in the Absorption Ratio', style={'color': 'grey'}),
        html.H5('''Our replication is in agreement''', style={'fontWeight': 'bold'}),

        html.Br(),
        html.Br(),

        dbc.Row([

            dbc.Col([

                html.P('''We were able to recreate the Absorption Ratio series and satisfactorily match the levels and
                trends in the original paper which covered 1998-2010. In the out-of-sample period recognizable events
                including Black Monday, Iraq’s invasion of Kuwait, and the COVID-19 pandemic all correspond to jumps
                in the Absorption Ratio.''', style={'fontSize': '1.25rem', 'lineHeight': '200%'}),


            ], width=4),

            dbc.Col([

                html.Div([

                    html.H4('''Figure 1: Replicated Absorption Ratio (Extended History)''',
                    style={'backgroundColor': '#267B83',
                             'color': 'white',
                             'paddingLeft': '10px'}),
                    dcc.Graph(id='absorption-ratio', figure=ar_fig),

                ], style={'border': '2px solid #267B83'})


            ], width=8, style={'paddingLeft': '20px', 'paddingRight': '20px'})

        ]),

            html.Br(),
            html.Br(),

            dbc.Row([

                dbc.Col([

                    html.P('''The AR Shift (z-score) is noiser however and it's not clear the degree to which all instances of
                    sharply rising or falling levels in the AR correspond to financial stress.''', style={'fontSize': '1.25rem', 'lineHeight': '200%'}),

                    html.P('''AR Shift values >0 indicate rising systemic risk (relative to the past 1Y) while
                    values <0 indicate falling systemic risk.''',
                           style={'fontSize': '1.25rem', 'lineHeight': '200%'}),

                ], width=4),

                dbc.Col([

                    html.Div([

                        html.H4('''Figure 2: AR Shifts Show Periods of Rising and Falling Systemic Risk''',
                        style={'backgroundColor': '#267B83',
                                 'color': 'white',
                                 'paddingLeft': '10px'}),
                        dcc.Graph(id='absorption-ratio-shift', figure=ar_shift_fig),

                    ], style={'border': '2px solid #267B83'}),

                ], width=8, style={'paddingLeft': '20px', 'paddingRight': '20px'})

            ]),

            html.Br(),
            html.Br(),

            html.Hr(style={'border': '1px solid grey'}),

            html.Br(),
            html.Br(),

            html.H2('Key Result 2: The Worst Days for the Market Were Preceded by Rising Systemic Risk',
                    style={'color': 'grey'}),
            html.H5('''Our replication is in agreement''', style={'fontWeight': 'bold'}),

            html.Br(),
            html.Br(),

            dbc.Row([

                dbc.Col([

                    html.P('''We identified the periods with the worst returns. For example October 19, 1987 "Black
                       Monday" was the worst one-day return (-20%) and March 23, 2020 was the worst trailing one-month
                       return (-33%). For each of those periods we took the AR Shift at the start of the period to see if
                       systemic risk was rapidly rising (AR Shift > 1) and thus preceded the market fall''',
                           style={'fontSize': '1.25rem', 'lineHeight': '200%'}),

                    html.Br(),

                    html.H4(
                        '''Figure 3: Percent of Worst Market Declines That Were Preceded by Rising Systemic Risk''',
                        style={'text-align': 'left', 'margin-bottom': '0%'}),

                    html.Br(),

                    dcc.Dropdown(id='figure3-input',
                                 options=[{'label': 'In-Sample (1998-2010)', 'value': 'in_sample'},
                                          {'label': 'Out-of-Sample (1972-2020)', 'value': 'out_of_sample'}],
                                 value='in_sample',
                                 style={'width': '100%'}),

                    html.Br(),

                    html.Div(id='figure3'),

                    html.Div(id='figure3-footnote',
                             style={'fontSize': '12px'}),

                ], width=6),

                dbc.Col([

                    html.P('''The adjacent table shows the proportion of extreme market declines. For example,
                                    taking the worst 1% of one-day market returns in the in-sample period from 1998-2010 yields
                                    32 observations. Of those 32 declines, systemic risk was rapidly rising (AR Shift > 1) in 24 of
                                    those cases (75%). Using monthly returns, the worst 1% of cases were preceded by rising systemic
                                    risk 84% of the time.''',
                           style={'fontSize': '1.25rem', 'lineHeight': '200%'}),

                    html.P('''Performance generally declines out-of-sample however using the period from 1972 to 2020. The
                    worst 1% of daily return periods were preceded by rising systemic risk in 58% of the cases and the worst
                    1% of monthly returns was preceded by rising systemic risk in only 41% of the cases.''',
                           style={'fontSize': '1.25rem', 'lineHeight': '200%'}),


                ], width=6)

            ]),



            html.Br(),
            html.Br(),

            html.Div(['''''']),


            html.Br(),
            html.Br(),

            dbc.Row([

                dbc.Col([

                    html.H4('''Figure 5: Worst Market Declines''',
                            style={'text-align': 'left', 'margin-bottom': '0%'}),

                ], width=6),

                dbc.Col([

                    html.H4('''Figure 4: AR Shift Levels and Stock Market Index Levels''',
                            style={'text-align': 'left', 'margin-bottom': '0%'}),


                    html.Div(id='figure4')

                ], width=6),



            ]),

            html.Br(),
            html.Br(),

            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),

        ], style={'margin': '0% 5% 0% 5%', 'text-align': 'left'}),

    ]

layout = serve_layout

@app.callback(dash.dependencies.Output(component_id='theory-purpose-content', component_property='children'),
              [dash.dependencies.Input(component_id='theory-purpose-tab', component_property='value')])
def update_theory_purpose(tab):

    if tab == 'tab-1':

        high_df = pd.read_csv('data/high_systemic_risk_returns.csv')
        low_df = pd.read_csv('data/low_systemic_risk_returns.csv')

        high_data = [
            {'x': high_df['date'],
             'y': high_df[s],
             'name': s,
             'kind': 'line'} for s in ['Agric', 'Autos', 'Oil', 'Telcm', 'Util']
        ]

        low_data = [
            {'x': low_df['date'],
             'y': low_df[s],
             'name': s,
             'kind': 'line'} for s in ['Agric', 'Autos', 'Oil', 'Telcm', 'Util']
            ]

        layout={'height': 300,
                'margin': {'t': 5, 'l': 40, 'b': 40},}

        high_fig = {'data': high_data, 'layout': layout}
        low_fig = {'data': low_data, 'layout': layout}

        content =  [


            html.Div([

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

            ], className='multi-column', style={'lineHeight': '200%', 'fontSize': '1.25rem'}),

            html.Br(),

            dbc.Row([

                dbc.Col([

                    html.Div([

                        html.H4('''A Period of High Systemic Risk''', style={'backgroundColor': '#267B83',
                                                                             'color': 'white',
                                                                             'paddingLeft': '10px'}),

                        dcc.Graph(figure=high_fig),

                        html.Div('''Oil, Telecom and Utilities follow the same trend. Autos does as well but with higher
                        "beta" post March 2009. The average pair-wise correlation of these sectors is 68%.''',
                                 style={'fontSize': '14px', 'marginLeft': '2%', 'marginRight': '2%'}),

                    ], style={'border': '2px solid #267B83'}),

                ], width=6),

                dbc.Col([

                    html.Div([

                        html.H4('''... Versus a Period of Low Systemic Risk''', style={'backgroundColor': '#267B83',
                                                                                       'color': 'white',
                                                                                       'paddingLeft': '10px'}),

                        dcc.Graph(figure=low_fig),

                        html.Div('''The five sectors show greater idiosyncracies and do not more together. The average
                        pair-wise correlation over the period is 44%.''', style={'fontSize': '14px', 'marginLeft': '2%', 'marginRight': '2%'}),

                    ], style={'border': '2px solid #267B83'})

                ], width=6),



            ])


        ]

    elif tab  == 'tab-2':

        df = pd.read_csv('data/absorption_ratio.csv')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.resample('M').last()
        df.reset_index(inplace=True, drop=False)

        cum_variance_data = [
            {'x': df['date'],
             'y': df[pc],
             'type': 'line',
             'name': pc,
             'market': {'color': 'red'}} for pc in ['ar', 'ar9', 'ar8', 'ar7', 'ar6', 'ar5', 'ar4', 'ar3', 'ar2', 'ar1']
        ]

        cum_variance_layout = {'height': 400,
               'margin': {'t': 5, 'l': 40, 'b': 40},
               'yaxis': {'range': [0.0, 1.0]}
                               }


        cum_variance_fig={'data': cum_variance_data, 'layout': cum_variance_layout, }

        df2 = pd.read_csv('data/weighted_and_unweighted_absorption_ratio.csv')
        df2['date'] = pd.to_datetime(df2['date'])
        df2.set_index('date', inplace=True)
        df2 = df2.resample('M').last()
        df2.reset_index(inplace=True, drop=False)

        weighted_data = [
            {'x': df2['date'],
             'y': df2[s],
             'type': 'line',
             'name': s,
             'market': {'color': 'red'}} for s in ['ar', 'unweighted AR']
            ]

        weighted_layout = {'height': 300,
                               'margin': {'t': 5, 'l': 20},
                               'yaxis': {'range': [0.4, 1.0]}
                               }

        weighted_fig = {'data': weighted_data, 'layout': weighted_layout, }


        content = html.Div([

            html.Div([

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

            ],  className='multi-column', style={'lineHeight': '200%', 'fontSize': '1.25rem'}),

            html.Br(),

            dbc.Row([

                dbc.Col([

                    html.Div([

                        html.H4('''Cumulative Proportion of Total Variance Explained by PCs''', style={'backgroundColor': '#267B83',
                                                                                           'color': 'white',
                                                                                           'paddingLeft': '10px'}),

                        dcc.Graph(figure=cum_variance_fig),

                        html.Div('''The first principal component explains a large fraction of the total variance and has
                         historically averaged around 60%. The next nine principal components then explain an average of 20%
                         more of the total variance.''', style={'fontSize': '14px', 'marginLeft': '2%', 'marginRight': '2%'}),

                    ], style={'border': '2px solid #267B83'}),

                ], width=6),

                dbc.Col([

                    html.Div([

                        html.H4('''Weighted vs Unweighted Variance''', style={'backgroundColor': '#267B83',
                                                                                           'color': 'white',
                                                                                           'paddingLeft': '10px'}),

                        dcc.Graph(figure=weighted_fig),

                        html.Div('''Using the weighted variance provides more timely responses to rapid spikes or drops
                        in the systemic risk measure.''', style={'fontSize': '14px', 'marginLeft': '2%', 'marginRight': '2%'})

                    ], style={'border': '2px solid #267B83'})

                ], width=6)


            ])


        ])

    else:

        content = [

            dcc.Markdown('''


        ```py
        def absorption_ratio(df: pd.DataFrame, half_life: int) -> np.ndarray:

            """
            calculate the sum of weighted variances of the principal components
            as a percentage of the total weighted variance of the original data

            :param df: returns in the columns and date as index, as dataframe
            :half_life: the half-life to use that parameterizes the decay of exponential weights, as int
            :return: the cumulative proportion of total variance for each pc, as numpy array
            """

            # deconstructed pca from scratch taken from:
            # https://towardsdatascience.com/principal-component-analysis-pca-from-scratch-in-python-7f3e2a540c51

            # 1. transform X data
            # data is in the form of observations in rows and features in columns
            X = df.values
            X = normalize(X)

            # reshape data so that features in rows and obs in columns
            X_transpose = X.T

            # 2. calc covariance matrix
            cov_matrix = np.cov(X_transpose)

            # 3. eigen decomposition
            values, vectors = np.linalg.eig(cov_matrix)

            # 4. construct the principal components from the original data and the eigenvectors
            pcs = X.dot(vectors)

            # pcs is with observations in rows and pc features in columns

            # 5. construct exponential weights
            num_obs = X.shape[0]
            weights = calc_exponential_weights(num_obs=num_obs, half_life=half_life)

            # 6. discard the eigenvalues from (3) above (which is the variance of each eigenvector or the sum of squared distances of each element in the eigenvector) and calculate weighted variance for each principal component
            pc_variances = []

            # iterate through each column (principal component)
            for i in range(pcs.shape[1]):

                # calculate weighted variance of the given principal component
                pc_variances.append(calc_weighted_variance(x=pcs[:, i], weights=weights))

            total_variance = sum(pc_variances)
            explanatory_power = np.array(pc_variances) / total_variance
            cum_explanatory_power = explanatory_power.cumsum()

            # 7. diagnostic: check that the total weighted variance of original features is equal to the total weighted variance of the PCs
            feature_variances = []

            for i in range(X.shape[1]):

                # calculate weighted variance of the given principal component
                feature_variances.append(calc_weighted_variance(x=X[:, i], weights=weights))

            assert np.isclose(
                sum(pc_variances), sum(feature_variances), 0.00001
            ), """error: pc variance {} does not equal feature
            variance {}""".format(
                sum(pc_variances), sum(feature_variances)
            )

            return cum_explanatory_power

        def calc_weighted_variance(x: np.array, weights: np.array) -> float:

            """
            calc weighted variance of an array. Weights are used to calculate the weighted average mean
            and weights are used to calculate the weighted average deviation of the observations from the
            weighed average mean
            """

            x = np.array(x)
            weights = np.array(weights)
            assert len(x) == len(
                weights
            ), "error: x {} and weights {} are of unequal lengths".format(len(x), len(weights))

            # calc deviation of each element from weighted mean
            mean = (x * weights).sum()
            sq_deviation = (x - mean) ** 2

            # calc weighted average deviation

            return (sq_deviation * weights).sum()

        def calc_ar_shift(df: pd.DataFrame) -> pd.DataFrame:

            """
            calculate AR Shit, a z-score that indicates rapidly rising or falling systemic risk
            :param df: data with columns date and ar, as dataframe
            :return: ar shift values, as dataframe
            """

            df = df[["date", "ar"]]
            df.set_index("date", inplace=True)

            # calculate trend
            df["avg_15"] = df["ar"].rolling(window=15).mean()
            df["avg_252"] = df["ar"].rolling(window=252).mean()
            df["std_252"] = df["ar"].rolling(window=252).std()
            df["ar_shift"] = (df["avg_15"] - df["avg_252"]) / df["std_252"]

            return df


        ```

        ''')


        ]


    return content


@app.callback([dash.dependencies.Output(component_id='figure3', component_property='children'),
               dash.dependencies.Output(component_id='figure3-footnote', component_property='children')],
              [dash.dependencies.Input(component_id='figure3-input', component_property='value')])

def update_figure3(in_sample):

    in_sample = True if in_sample == 'in_sample' else False

    worst_periods = pd.read_csv('data/absorption_ratio_worst_return_periods.csv')
    df = worst_periods.copy()
    df = df[df['in_sample'] == in_sample]
    df = df[df['overlapping'] == True]
    df = df.pivot(index='period', columns='proportion', values='ar_greater_1')
    df.reset_index(inplace=True, drop=False)
    df.rename(columns={'period': 'Period', .01: '1%', .02: '2%', .05: '5%'}, inplace=True)
    cols = [{'name': ['', 'Period'], 'id': 'Period'},
            {'name': ['Worst N Periods', '1%'], 'id': '1%', 'type': 'numeric', 'format': FormatTemplate.percentage(1)},
            {'name': ['Worst N Periods', '2%'], 'id': '2%', 'type': 'numeric', 'format': FormatTemplate.percentage(1)},
            {'name': ['Worst N Periods', '5%'], 'id': '5%', 'type': 'numeric', 'format': FormatTemplate.percentage(1)},]

    style_cell_conditional = [
        {'if': {'column_id': i},
         'textAlign': 'center'} for i in ['Period', '1%', '2%', '5%']
    ]

    footnote = '''N = 32, 63, 156 for worst 1%, 2%, 5% of periods, respectively'''
    if in_sample == False:
        footnote = '''N = 123, 245, 612 for worst 1%, 2%, 5% of periods, respectively'''

    return dt.DataTable(id = 'table',
                        columns=cols,
                        data= df.to_dict('records'),
                        merge_duplicate_headers=True,
                        style_cell_conditional=style_cell_conditional,
                        style_header={'background_color': '#26BE81'}), footnote