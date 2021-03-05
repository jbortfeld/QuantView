
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_table as dt
import dash_table.FormatTemplate as FormatTemplate
from dash.dependencies import Input, Output


import datetime
import pandas as pd
import numpy as np

from app import app

def init_xs_os(n:int) -> list:

    xs_os = np.random.choice(['X', 'O', ''], size= n**2, p=[.46,.46, .08])
    xs_os[int(n**2 / 2)] = 'X'
    return xs_os

def populate_box(i, n, population):
    #return population[i]
    if i ==int(n ** 2 / 2):
        return 'X'
    else:
        return ''

def format_box(i: int, n: int, r: int, h: int, population: list) -> dict:

    '''
    set the styling for a box in the checkerboard. this will set the background color
    and also the borderof the neighborhood defined by the selected radius (relative to
    the center).
    '''


    style = {'height': '{}px'.format(h),
             'display': 'flex',
             'justify-content': 'center',
             'align-items': 'center',
             'color': 'white',
             'font-size': 14,
             'border': '2px solid black'}


    # 1. set background color

    # use checkerboard style
    # if i % 2 ==0:
    #     style['background-color'] = '#267B83'
    # else:
    #     style['background-color'] = '#26BE81'


    if population[i] == 'X':
        style['background-color'] = '#26BE81'


    elif population[i] == 'O':
        style['background-color'] = '#267B83'
        #style['background-color'] = '#3498DB'
        #style['background-color'] = '#444FAD'
    else:
        style['background-color'] = 'black'


    # 2.  set border (the area within the given radius)
    center = int(n * n / 2)
    if i == center:
        style['font-size'] = 22
        style['font-weight'] = 'bold'

    # the top or bottom is defined by going r rows up or down from the center
    # (which is an offset of n*r squares forward and back) and then r cells left or right
    top = list(range(center - r*n - r, center - r*n + r + 1))
    bottom = list(range(center + r*n - r, center + r*n + r + 1))
    left = []
    right = []

    for offset in range(r+1):
        right.append(center - offset*n + r)
        right.append(center + offset*n + r)

        left.append(center - offset * n - r)
        left.append(center + offset * n - r)

    if i in top:
        style['border-top'] = '5px solid red'
    elif i in bottom:
        style['border-bottom'] = '5px solid red'

    if i in left:
        style['border-left'] = '5px solid red'
    elif i in right:
        style['border-right'] = '5px solid red'

    return style

def format_grid(n:int, h: int):
    return {'display': 'grid',
            'grid-template-columns': '{}px '.format(h) * n}


def build_checkerboard(n:int, r:int, h:int, population: list):

    return [html.Div(populate_box(i, n, population), style=format_box(i=i, n=n, r=r, h=h, population=population)) for i in range(n**2)]



xs_os = init_xs_os(n=9)

sample_style_cell_conditional = [
    {'if': {'column_id': ''},
     'width': '60px'},

    {'if': {'column_id': 'Neighbor'},
     'width': '75px',
     'textAlign': 'left'},

    {'if': {'column_id': 'Count'},
     'width': '60px'},

    {'if': {'column_id': 'Pct'},
     'width': '60px'},
]

sample_style_data_conditional = [

    {'if': {'column_id': '', 'row_index': 0},
     'backgroundColor': '#26BE81'},

    {'if': {'column_id': '', 'row_index': 1},
         'backgroundColor': '#267B83'},

    {'if': {'column_id': '', 'row_index': 2},
         'backgroundColor': 'black'},

]

sample_columns = [{'name': c, 'id': c} for c in ['', 'Neighbor', 'Count']]
sample_columns.append({'name': 'Pct',
                       'id': 'Pct',
                       'type': 'numeric',
                       'format': FormatTemplate.percentage(1)})


############################################################
# figure 4: chart of preference level vs outcome
df4 = pd.read_csv('data/segregation_figure4.csv')
df4 = df4[df4['cut'] <= 0.5]

data4 = [{'x': df4['cut'],
          'y': df4['avg'],
          'type': 'line+markers',
          'name': 'series',
          'line': {'color': '#26BE81', 'width': 4},}]

layout4 =  {'height': 300,
                    'legend': {
                        'orientation': 'h'
                    },
                    'margin': {'t': 10, 'l': 50, 'b': 40},
                   'xaxis': {'title': 'In-group Preference'},
                   'yaxis': {'title': 'Avg End Similarity'}
                    }

figure4 = {'data': data4,
           'layout': layout4}

############################################################
# figure 5: avg similarity over time
df5 = pd.read_csv('data/segregation_figure5.csv')
df5.set_index('t', inplace=True)
show_cols = ['0.2', '0.25', '0.3', '0.35', '0.4', '0.45', '0.5', '0.6']
show_cols2 = ['0.2', '0.25', '0.3', '0.35', '0.4', '0.45']
end_values = df5.iloc[-1]


annotations5 = [{'xref': 'paper',
                 'x': 1.1,
                 'y': end_values[col],
                 'text': col,
                 'showarrow': False,
                 'font': {'color': 'orange', 'family': 'avenir', 'size': 12} } for col in show_cols2]

annotations5.append({'xref': 'paper',
                 'x': 1.15,
                 'y': end_values['0.5'],
                 'text': 'Pref = 0.5',
                 'showarrow': False,
                 'font': {'color': 'orange', 'family': 'avenir', 'size': 12} } )

annotations5.append({'xref': 'paper',
                 'x': 1.1,
                 'y': end_values['0.6'],
                 'text': '0.6',
                 'showarrow': False,
                 'font': {'color': 'red', 'family': 'avenir', 'size': 12} } )


# source: https://design.pega.com/data-viz-single-hue-color-palettes-continuous-data
colors5 = {'0.05': '#FFF8EE',
           '0.1': '#FFF1DC',
           '0.15': 'FFE9CB',
           '0.2': '#FFE2B9',
           '0.25': '#FFDAA7',
           '0.3': '#FFD395',
           '0.35': '#FFCB82',
           '0.4': '#FFC470',
           '0.45': '#FFB646',
           '0.5': '#FEA637',
           '0.6': 'red'}

df5 = df5[show_cols]

# source: https://design.pega.com/data-viz-single-hue-color-palettes-continuous-data
data5 = [{'x': df5.index,
          'y': df5[col],
          'type': 'line',
          'name': col,
          'opacity': col,
          'line': {'color': colors5[col], 'width': 4}} for col in show_cols]

layout5 = {'height': 400,
           'legend': {'orientation': 'h'},
           'showlegend': False,
           'plot_bgcolor': 'white',
           'margin': {'t': 10, 'l': 50, 'b': 40},
           'xaxis': {'title': 'Period'},
           'yaxis': {'title': 'Avg Similarity'},
           'annotations': annotations5
           }

figure5 = {'data': data5,
           'layout': layout5}
############################################################
# figure 6: discontents over time
df6 = pd.read_csv('data/segregation_figure6.csv')
df6.set_index('t', inplace=True)
show_cols = ['0.2', '0.25', '0.3', '0.35', '0.4', '0.45', '0.5']
show_cols2 = ['0.2', '0.25', '0.3', '0.35', '0.4', '0.45']
end_values = df6.iloc[-1]


annotations6 = [{'xref': 'paper',
                 'x': 1.1,
                 'y': end_values[col],
                 'text': col,
                 'showarrow': False,
                 'font': {'color': 'blue', 'family': 'avenir', 'size': 12} } for col in ['0.3']]

annotations6.append({'xref': 'paper',
                 'x': 1.15,
                 'y': end_values['0.5'],
                 'text': 'Pref = 0.5',
                 'showarrow': False,
                 'font': {'color': 'blue', 'family': 'avenir', 'size': 12} } )


# source: https://design.pega.com/data-viz-single-hue-color-palettes-continuous-data
colors6 = {'0.05': '#E7EFF7',
           '0.1': '#D1E0EE',
           '0.15': 'B9CFE5',
           '0.2': '#A2BFDD',
           '0.25': '#8BAFD3',
           '0.3': '#749FCB',
           '0.35': '#5D90C2',
           '0.4': '#427FBA',
           '0.45': '#005FA7',
           '0.5': '#00428B'}

df6 = df6[show_cols]

# source: https://design.pega.com/data-viz-single-hue-color-palettes-continuous-data
data6 = [{'x': df6.index,
          'y': df6[col],
          'type': 'line',
          'name': col,
          'opacity': col,
          'line': {'color': colors6[col], 'width': 4}} for col in show_cols]

layout6 = {'height': 400,
           'legend': {'orientation': 'h'},
           'showlegend': False,
           'plot_bgcolor': 'white',
           'margin': {'t': 10, 'l': 50, 'b': 40},
           'xaxis': {'title': 'Period'},
           'yaxis': {'title': 'Discontents (% of Households)'},
           'annotations': annotations6
           }

figure6 = {'data': data6,
           'layout': layout6}





def serve_layout():

    custom_tab_selected = {'borderTop': '6px solid #26BE81'}


    return [


        html.Div([

            html.Br(),
            html.Br(),


            html.H1("Why We Don't Live Together", style={'font-size': '4.5rem', 'font-weight': 'bold', 'color': '#26BE81'}),

            html.Br(),

            html.H3("Replicating residential segregation using agent-based modeling"),

            html.Br(),
            html.Br(),

            html.Img(src='/assets/philadelphia_segregation_dark.png', style={'max-width': '100%'}),

            html.Div([

                html.Section('''Figure 1: Ethnic populations in Philadelphia using data from the 2010 Census.
                Source:'''),

                html.A('''WashingtonPost''',
                       href='https://www.washingtonpost.com/graphics/2018/national/segregation-us-cities/',
                       style={'display': 'inline'})

            ]),

            html.Br(),
            html.Br(),

            html.Ul([

                html.Li('''We reproduce Thomas Schelling's landmark experiment from the 1970s that demonstrates housing
                segregation patterns using agent-based modeling (ABM).'''),

                html.Li('''This experiment shows that housing segregation, where individuals cluster with similar people,
                 can result even if all people have a preference for living in integrated neighborhoods.'''),

                html.Li('''This experiment is often used as an introduction to agent-based modeling and demonstrates
                that counter-intuitive results can emerge at the societal level due to the complexities of group
                dynamics.'''),

            ], style={'font-size': '1.25rem'}),


            html.Br(),
            html.Br(),


        ], style={'margin': 'auto',
               'text-align': 'left',
               'max-width': '750px'}),


        # intro
        html.Div([

            html.Br(),

            html.H3('''Introduction'''),

            html.P('''Social scientists have observed that people of similar ethnicities tend to cluster together,
            leading to predominantly White, Black or Hispanic neighborhoods rather than a multiracial mixed
            alternative. Why is this the case? Some might argue that racial progress, while volatile, has increased
            over the decades and that enduring segregation must therefore be the result of structural disparities.'''),


            html.P('''But do inclusive racial attitudes necessarily imply integrated racial outcomes? A perfectly
            intuitive line of thought would be if people were tolerant and inclusive in their individual outlooks,
            that the population as a whole would in turn develop into an integrated society.  Unfortunately, this
            may be an example of when intuition is faulty us and a perfectly plausible theory fails to reflect
            a complex reality.'''),

            html.P('''This tool will demonstrate the application of agent-based modeling (ABM) in explaining
            residential segregation and also expose the concept and process of ABM itself.  Agent-based modeling
            is a bottom-up framework that involves programming individual agents with behavior and goals and
            simulating their interactions with each other and the environment. The goal of this app is to show
            how ABM is often used to analyze group behavior and how ABM can reveal unexpected dynamics that emerge from
            seemingly simple setups.'''),

            html.Br(),

            html.H3('''Residential Segregation'''),

            html.P('''Chicago is one of the most diverse metropolises in America with nearly 3 million residents
            and large proportions from each major ethnic group (56% White, 32% Black, 29% Hispanic and 7% Asian).
            Chicago however, is also one of the most segregated big cities in America. For example, a map of
            demographic information using the latest 2010 census shows distinct neighborhoods bounded by ethnic
            composition.'''),

            html.Br(),

        ], style={'font-size': '1.1rem',
                  'margin': 'auto',
                  'max-width': '750px',
                  'text-align': 'left',
                  }),

        # example real segregation maps
        html.Div([

            html.Hr(),

            html.H5('Figure 1: Observed Segregation Across Two Cities'),

            html.Br(),

            dbc.Row([

                dbc.Col([
                    html.Div([
                        html.Img(src='/assets/chicago_segregation_dark.png')
                    ], style={'height': '200px', 'width': '300px'}),

                ], width=6),

                dbc.Col([

                    html.Img(src='/assets/nyc_segregation_dark.png')

                ], width=6),

            ], no_gutters=False),

            html.Br(),

            html.Div('''Each dot represents 150 people from the 2010 Census. Source: WashingtonPost'''),

            html.Hr(),

        ], style={'margin': 'auto',
                  'text-align': 'left',
                  'max-width': '1000px'}),

        html.Br(),

        html.Div([

            html.P('''The reality of racial segregation has many contributing factors, including deliberate government
            policies that have historically segregated minorities via land use regulations
            or mortgage discrimination. Furthermore, a more passive phenomena has been racial steering whereby real
            estate brokers are likely to steer clients towards particular neighborhoods based on race.'''),

            html.P('''In addition to these external factors however, housing patterns may also stem from personal
            preferences. These include households favoring certain neighborhoods due to proximity to family, the
            availability of familiar food options or the possibility of forming social networks with people of similar
            values. Collectively these preferences for amount to what social scientists call an in-group preference, or
            a preference for one’s own culture, and which will be the focus of this app.'''),

            html.P('''Though this app will use residential segregation as a way to discuss ABM, it is not a
            comprehensive overview of all the applicable social, political and economic dynamics. While computer
            scientists are able to contribute to the conversation, as will be demonstrated in this app, a serious
            discussion of this topic deserves a multidisciplinary approach with perspectives from historians,
            statisticians, economists and others.''',
                   style={'background-color': 'lightyellow',
                          'border': '2px solid black',
                          'border-radius': '20px',
                          'padding': '6px'}),

            html.Br(),

            html.H3('''Agent-based Modeling Philosophy'''),

            html.P('''The objective of agent-based modeling is to replicate reality using a computer
            simulation that is as simple as possible. In our case, we want to simulate residential dynamics that
            reproduce observed segregation patterns, or the clustering of different groups, based on as few factors
            as possible. If we are able to replicate observed reality we will have “explained”
            housing segregation in the sense that our simulation shows that housing segregation is an outcome of our
            programmed assumptions. '''),

            html.P('''It’s important to note that within the ABM framework “explanation” has a different meaning
            than in statistics. Whereas in statistics explanation is associated with correlation, within ABM the
            meaning of explanation has connotations of causality since we explicitly define cause and effect dynamics
            within our simulation (the challenge however is to encode accurate cause and effect relationships).
            Furthermore, whereas in statistics we usually try to control for many factors by including
            different variables in the analysis, within ABM it is preferable to construct a parsimonious model to
            show the minimum required assumptions that would be required to reproduce reality. '''),

            html.Br(),

            html.H3('''Simulation Methodology'''),

            html.P('''To program our segregation simulation we model a simplified reality. We represent a city as a
            2D grid, like a checkerboard, and each square in the grid represents a residence that can be occupied by
            a household. Our course, real neighborhoods do not physically look like a crowded checkerboard but we assume
            that this simplification, amongst many assumptions we’ll make, is not material to the analysis.'''),

            html.P('''Next we assume in our model that there are two types of households (say White and Asian))
            and that each household is primarily concerned about belonging to a neighborhood filled with families
            similar to themselves. To measure the similarity of a neighborhood with respect to a given household, we
            define a neighborhood as the adjacent houses within some radius and then calculate the proportion of
            households that belong to the “same” group and the proportion of households belonging to the “other” group.
            Depending on a household’s tolerance level, the household can then either decide to move to a new
            neighborhood or to stay.'''),



        ], style={'font-size': '1.1rem',
                  'margin': 'auto',
                  'max-width': '750px',
                  'text-align': 'left',
               }),

        html.Br(),

        # interactive tool: example neighborhood similarity calculation
        html.Div([

            html.Hr(),

            html.Br(),

            html.H4('Figure 2: Sample Similarity Calculation'),

            html.Br(),

            dbc.Row([

                # left column
                dbc.Col([

                    html.Div(id='sample-calc-grid')

                ], width=6),

                # right column
                dbc.Col([

                    html.Div('''We calculate the comfort of the center household, marked by the X,
                        by counting the number of similar and dissimilar households in the surrounding
                        neighborhood. In this example, assume that a household would prefer to live
                        in a neighborhood where at least 51% of her neighbors are like her.'''),

                    html.Br(),

                    dbc.Row([

                        dbc.Col([
                            html.Div('Select neighborhood:', style={'color': 'grey'}),
                            dcc.Dropdown(id='radius-input',
                                         options=[{'label': "Radius {}".format(i), 'value': i} for i in range(1, 5)],
                                         value=2,
                                         clearable=False,
                                         ),
                        ], width=5),

                        dbc.Col('', width=1),

                        dbc.Col([
                            html.Div([
                                dt.DataTable(id='sample-table',
                                             columns=sample_columns,
                                             style_cell_conditional=sample_style_cell_conditional,
                                             style_data_conditional=sample_style_data_conditional,
                                             style_as_list_view=True
                                             )
                            ])
                        ], width=6),

                    ]),

                    html.Br(),

                    html.Div(id='sample-conclusion', style={'font-weight': 'bold'})

                ], width=6),

            ]),

            html.Br(),

            html.Hr(),

            html.Br(),

        ], style={'margin': 'auto',
                  'text-align': 'left',
                  'max-width': '900px'}),



        html.Div([

            html.P('''Using this setting, we can plan our simulation. Below we present the methodology
            at three levels of abstraction, ranging from a qualitative description to technical code.'''),

            html.Br(),
            html.Br(),

            html.Div([

                dcc.Tabs(id='methodology-tabs', value='tab-1', children=[dcc.Tab(label='Intuition',
                                                                                 value='tab-1',
                                                                                 selected_style=custom_tab_selected),
                                                                         dcc.Tab(label='Pseudocode',
                                                                                 value='tab-2',
                                                                                 selected_style=custom_tab_selected),
                                                                         dcc.Tab(label='Code',
                                                                                 value='tab-3',
                                                                                 selected_style=custom_tab_selected)
                                                                         ]),

                html.Br(),
                html.Br(),

                html.Div(id='methodology-content'),

            ], style={'border': '4px solid #26BE81', 'padding': '5%'}),

            html.Br(),
            html.Br(),

            html.H3('''Results and Analysis'''),

            html.Br(),

            html.Div([

                html.P('''Our analysis proceeds using the methodology described above, which is based around the
                simple premise that households might have a preference to live in a neighborhood that reflects their
                ethnic identity. When that preference is very strong, a White household might only be content if 90%
                of their neighbors are also White. On the other hand, if the preference is relatively weak then a
                Hispanic household might be perfectly content in a neighborhood that is only 20% Hispanic. '''),

                html.P('''Before we run the experiment it is an opportune time, and also good research practice,
                to ask what are our expectations (do we have any hypotheses)? Without overthinking the question,
                here are two uneducated though reasonable guesses on what we might observe from the simulation:'''),

                html.Ul([


                    html.Li(
                    dcc.Markdown('''*Inclusive racial attitudes should lead to integrated neighborhoods.* If
                    households have a low in-group preference, then we expect to see more mixed neighborhoods over time.
                    Conversely, if households have a high in-group preference, then we would expect to see more
                    segregated neighborhoods.''')
                    ),

                    html.Li(
                    dcc.Markdown('''*The level of diversity in a neighborhood is likely to be equal to the average
                    preference level.* If the average household preference is 55%, then we might expect that that the
                    average neighborhood will be composed of a 55-45 split between the two groups (or replace 55% with
                    any percentage and matching split)''')
                    )

                ]),



                html.P('''Below we run our simulation using a small 16x32 grid with around 512 households.
                Each household has a relatively inclusive in-group preference of 40%.'''),


            ]),

            html.Br(),
            html.Br(),

        ], style={'font-size': '1.1rem',
                  'margin': 'auto',
                  'max-width': '750px',
                  'text-align': 'left',
                  }),


        html.Div([

            html.Hr(),

            html.H4('Figure 3: Migration Simulation'),

            dbc.Row([

                dbc.Col([

                    html.Img(src='/assets/test_gif.gif'),

                ], width=7),

                dbc.Col([

                    html.H5('''From an initial integrated state, two populations eventually segregate over
                    time.'''),

                    html.Br(),

                    html.P('''Each square represents a household that considers whether to remain or move to a different
                    spot in the grid (black squares are empty homes and households can move into them).
                    Households make the decision based on a simple logic: Stay if at least 40% of
                    its neighbors are a similar color, or else move otherwise. Even though everyone is content
                    to be a minority and live in an integrated neighborhood, over time the grid becomes
                    segregated with a clear separation between the two groups in comparison to the starting state.''')
                ], width=5),

            ]),

            html.Hr(),

        ] , style={'margin': 'auto',
               'text-align': 'left',
               'max-width': '1100px'}),

        html.Br(),
        html.Br(),

        html.Div([

            html.P('''The simulation shows that a segregated outcome results in the end even though 1)
            the landscape starts from an integrated state and 2) all the households are not averse to living
            in a mixed community. '''),

            html.P('''Why does this occur? Even though the households were placed at random, by chance a small number
            of households might find themselves as an uncomfortable minority (<40% average similarity in this case).
            When these households move out of their neighborhood, or new households move into a
            neighborhood, this will in turn have a small impact that causes a small number of household to want to move
            in the next period. Each time a household moves, it has cascading effects that compel other households to
            move later on until the end result is a system characterized by homogeneous neighborhoods. '''),

            html.P('''We rerun the simulation while varying the in-group preference levels in order to investigate
            whether more inclusive attitudes are associated with more integrated outcomes. At each preference level
            that we test, we run multiple simulations and record the average outcome by calculating the average
            similarity of the neighborhood from the point-of-view of each household.'''),

            html.P('''In the below chart (Figure 4) we see that below a 25% preference level, the neighborhoods in the
            last period are mostly heterogenous with an average similarity that doesn’t change from the initial
            integrated state. '''),

            html.P('''For preference levels above 25% however, the system crosses a tipping point and the end states
            start to show more segregated outcomes, rising to average neighborhood similarity of 90% given a 50% in-group
            preference level. Note that under our simulation the average similarity will never grow to 100% given that
            households on the border between two segregated neighbors will still count some out-of-group members in
            their neighborhood.'''),

            html.Br(),
            html.Br(),

            html.H4('''Figure 4: Outcomes for Various In-group Preference Levels'''),

            html.Br(),

            dcc.Graph(figure=figure4),

            html.Br(),
            html.Br(),

            html.P('''These results are consistent with our original prediction that rising in-group preference
            levels are associated with higher rates of homogeneous neighborhoods. Our predictions however underestimated
            the level of in-group preference that was needed to generate segregated neighborhoods.'''),

            html.P('''We present two more charts to show how the systems evolved over the simulation iterations.
            Figure 5 shows that the average similarity at each time step and illustrates the rate of segregation.
            Relatedly, Figure 6 shows the percentage of the population that is unhappy in their neighborhood over
            time. '''),

            html.Br(),
            html.Br(),


        ], style={'font-size': '1.1rem',
                  'margin': 'auto',
                  'max-width': '750px',
                  'text-align': 'left',
                  }),

        html.Div([

            dbc.Row([

                dbc.Col([

                    html.H4('''Figure 5: Mean Similarity Over Time'''),

                    dcc.Graph(figure=figure5)

                ], width=6),




                dbc.Col([

                    html.H4('''Figure 6: Discontents Over Time '''),

                    dcc.Graph(figure=figure6)

                ], width=6)



            ])


        ], style={'font-size': '1.1rem',
                  'margin': 'auto',
                  'max-width': '1100px',
                  'text-align': 'left',
                  }),

        html.Br(),
        html.Br(),

        html.Div([

            html.P('''Careful observation of Figure 5 shows the average similarity rises faster for medium levels of
            in-group preference than for stronger levels. For example, the series for an in-group preference of 40%
            crosses the 75% average similarity level before the series for the 50% in-group preference. This is
            mostly a function of the simulation setup and the frictions that occur when many households are seeking
            to move but only a limited number of vacant households are available. '''),

            html.P('''For example, a 60% in-group preference level will eventually produce a higher average similarity
            than a 50% in-group preference but the process moves considerably slower, as seen in Figure 5. Taken to an
            extreme, a 99% in-group preference will paradoxically never approach a segregated state in this simulation
            because households will never be content, will always be moving, and the system will never stabilize enough
            to allow the formation of homogeneous neighborhoods. '''),

            html.Br(),
            html.Br(),

            html.H4('''Conclusion: Thoughts on Segregation'''),

            html.P('''If we take this simple simulation’s conclusions seriously, we may come around to a pessimistic
            view that even if we were to eliminate all forms of structural discrimination, we’d find that those were not
            necessary to produce segregation and that preferences alone are totally sufficient.'''),

            html.P([

                html.Span('''As stated earlier however, this paper is not intended to speak to the full complexity of
            segregation nor on the efficacy of potential corrections. Ultimately though, the Schelling model
            shows that preferences may be an important part of the conversation insofar that preferences can possibly
            “explain” residential segregation. As summarized by '''),

            html.Span(

            html.A('''Clark and Fosset:''', href='https://www.pnas.org/content/105/11/4109')),

            ]),


            html.Div([
            dcc.Markdown('''*The more important distinction in the literature is the distinction between preferences and
            discrimination… policy options for promoting integration differ dramatically for these two
            factors.*'''),


            dcc.Markdown('''*Discrimination is prohibited by law and is subject to a variety of legal remedies. Preferences
            are outside the purview of fair housing law and remedies, if sought, will necessarily be fundamentally
            different. In view of this, it is crucial to gain a better understanding of the impact preferences may have
            on segregation.*'''),

            ], style={'background-color': 'lightyellow',
                          'border': '2px solid black',
                          'border-radius': '20px',
                          'padding': '6px'}),

            html.Br(),
            html.Br(),

            html.H4('''Conclusion: Thoughts on ABM'''),

            html.P('''The segregation model presented here is relatively simple, a version 1.0 if you will, that was
            first presented in the 1970s. As that was a time before personal computers, it is especially impressive
            to think that the initial research was developed by flipping coins and moving pieces around a
            board by hand. With the benefit of computational power, researchers have since expanded on this framework
            in numerous ways including:'''),

            html.Ul([

                html.Li('''Expanding the number of ethnic groups from two to many.'''),

                html.Li('''Modelling heterogenous preference levels across households-not everyone has the same
                in-group preference level.'''),

                html.Li('''Drawing richer models of landscapes by incorporating inclusive or exclusive community
                focal points such as commercial centers or churches.'''),

                html.Li('''Modelling dynamic household preferences that evolve over time and in reaction to their
                environment.'''),

                html.Li('''Incorporating other household motivations based on income, neighborhood affordability
                and non preference-based factors.''')

            ]),

            html.P('''Outside of modeling segregation, ABM has also spread with varying degrees of success across
            other fields such biology and physics. As of 2021, ABM has most recently and notably been used in
            epidemiology to model the spread of the coronavirus across communities and forecast transmission,
            hospitalization and fatality scenarios.'''),

            html.P('''Within finance and economics however, ABM has arguably not produced a large body of insights,
            though it does maintain its own group of advocates and there are notable achievements. For example, ABM
            can be used to explain the existence of so-called "fat-tails" in asset returns and volatility clustering
            as the systemic outcome of interactions between fundamental and technical traders. In economics, ABM may
            also explain economic contractions as the endogenous outcome of economic actors rather than modeling
            recessions as external shocks. We think that these are interesting applications of ABM with novel results.
            We hope to cover these in depth in the future.'''),


            html.Br(),
            html.Br(),

            html.P([
                html.Span(['Github ']),

                html.Span([html.A('''website ''',
                                  href='https://github.com/jbortfeld/QuantView/blob/master/apps/schelling_segregation.py')]),

                html.Span('and '),

                html.Span(html.A('analysis.',
                                 href='https://github.com/jbortfeld/QuantView/tree/master/notebooks/Segregation/abm.ipynb')),

            ]),



        ], style={'font-size': '1.1rem',
                  'margin': 'auto',
                  'max-width': '750px',
                  'text-align': 'left',
                  }),

        html.Br(),
        html.Br(),



    ]



layout = serve_layout



@app.callback([Output(component_id='sample-calc-grid', component_property='children'),
               Output(component_id='sample-table', component_property='data'),
               Output(component_id='sample-conclusion', component_property='children')],
              [Input(component_id='radius-input', component_property='value')])
def sample_calc(radius):

    print('radisu start', radius)

    n=9
    h=45

    # calculate the similarity of neighbors within the specified radius
    # start by collecting the neighbors into a list

    center = int(n** 2 / 2)
    neighborhood = []
    # get the squares above the center row
    for row in range(-radius, 0):
        for r in range(-radius, radius+1):
            neighborhood.append(xs_os[center + row*n + r])

    # get the squares in the center row
    neighborhood.extend(xs_os[center - radius: center + radius + 1])

    # get the squares below the center row
    for row in range(1, radius+1):
        for r in range(-radius, radius+1):
            neighborhood.append(xs_os[center + row*n + r])

    x_count = neighborhood.count('X') - 1
    o_count = neighborhood.count('O')
    blank_count = neighborhood.count('')
    neighbor_count = x_count + o_count

    df = pd.DataFrame({'': ['','',''],
                  'Neighbor': ['Similar', 'Dissimilar', 'Vacant'],
                  'Count': [x_count, o_count, blank_count],
                  'Pct': [x_count / neighbor_count, o_count/neighbor_count, np.NaN]})


    if x_count / neighbor_count >=0.51:
        text1 = 'stay put'
        text2 = 'many'
    else:
        text1 = 'move away'
        text2 = 'too few'
    conclusion_text='''Given an in-group preference of 51%, the center household will {} since
     {} ({:.2f}%) of her neighbor are like her'''.format(text1, text2, x_count/neighbor_count * 100)

    return html.Div(build_checkerboard(n=n, r=radius, h=h, population=xs_os), style=format_grid(n=n, h=h)),\
           df.to_dict('records'), conclusion_text





layout = serve_layout



@app.callback(dash.dependencies.Output(component_id='methodology-content', component_property='children'),
              [dash.dependencies.Input(component_id='methodology-tabs', component_property='value')])
def update_theory_purpose(tab):

    if tab == 'tab-1':

        content = html.Div([

            html.P('''We build a computer simulation by constructing a city and randomly placing Black and Hispanic
            families in the houses. We imagine that in month 1, each household evaluates how happy they are in their
            neighborhood based on the composition of their neighbors. Families that are surrounded by enough “similar”
            people are content and decide to stay in their home. Families that are discontent, because the number of
            similar families is below their comfort level, decide to move away to a different home. '''),

            html.P('''It is now month 2 and each family repeats their evaluation process and decides to stay in
            their home or move. We repeat this cycle until the city begins to stabilize, perhaps many months later,
            and very few families are moving around. The stabilization of the city signifys that almost all of the
            households are content in their respective neighborhoods. It is important to note that while a family be
            satisfied with their neighborhood in one period and therefore decide to stay, the neighborhood itself may
            change over time as older households move away and newer households move in. With these changes, a
            household that was formerly content may end up moving away in the future.''')

        ])



    elif tab == 'tab-2':

        content = html.Div([

            dcc.Markdown('''

            ```py

            Randomly place households across the city
            Calculate the % of similar households in the neighborhood for each household
            Determine which households want to move

            While (# of households that want to move) > 0:

                For every household that wants to move:
                    Randomly move the household to a new home

                For every household:
                    Calculate the % of similar households in the neighborhood
                    Determine if the household wants to move
            ```
            ''')


        ])

    else:

        content = html.Div([

            dcc.Markdown('''

            ```py

            # the main function for running the abm-based segregation simulation is below.
            # for the full code, including all functions, see the github
            # https://github.com/jbortfeld/QuantView/tree/master/notebooks/Segregation/abm.ipynb

            def simulate(grid: np.array, radius: int, cutpoint: float, num_iterations:int=50, verbose:int=0):

                """
                run the segregation simulation for a given landscape (grid)
                """

                # save the environment at eash iteration
                simulations = []
                simulations.append(grid.copy())

                all_spaces = get_all_spaces(grid=grid)

                system = calc_avg_similarity(grid=grid)

                if not verbose is False:
                    print('starting systemic similarity: {:.3f}'.format(np.array(system).mean()))

                start = time.time()

                for _ in range(num_iterations):

                    # 1. get available empty spaces
                    free_spaces = find_values(grid=grid, val='E')

                    # randomly shuffle the available spaces
                    random.shuffle(free_spaces)

                    # 2. get agents that want to move
                    wants_to_move = []
                    for agent in all_spaces:
                        if get_value(x=agent, grid=grid) != 'E':

                            _neighbors = neighbors(x=agent, grid=grid, radius=radius)
                            _similarity = similarity(x_value=get_value(x=agent, grid=grid), grid=grid, neighbors=_neighbors)

                            if _similarity < cutpoint:
                                wants_to_move.append(agent)

                    # randomly shuffle the agents that want to move
                    random.shuffle(wants_to_move)
                    print('{} agents want to move'.format(len(wants_to_move)))

                    # try to move each agent that is unhappy
                    for agent in wants_to_move:

                        # if there are free spaces still available (not including spaces that became free because someone
                        # moved in this period)
                        if len(free_spaces) > 0:

                            _free_space = free_spaces.pop()
                            grid = swap(grid=grid, source=agent, dest=_free_space)


                    # print avg similarity across the entire system
                    system = calc_avg_similarity(grid=grid)


                    if verbose == 0:
                        pass
                    elif verbose == 1:
                        print('--iteration {}: systemic similarity: {:.3f}'.format(_, np.array(system).mean()), end="")
                    elif verbose == 2:
                        print('--iteration {}: systemic similarity: {:.3f}'.format(_, np.array(system).mean()) )

                    # save the environment at the end of this iteration
                    simulations.append(grid.copy())

                if verbose:
                    print()
                    print('done in {}s'.format(time.time() - start))
                return np.array(system).mean(), simulations


            ```
            ''')
        ])

    return content