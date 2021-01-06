
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

def serve_layout():


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

                html.Li('''We reproduce a landmark experiment from the 1970s that demonstrates housing segregation patterns
                using agent-based modeling (ABM).'''),

                html.Li('''This experiment shows that housing segregation, where individuals cluster with similar people,
                 can result even if all people have a preference for living in integrated neighborhoods.'''),

                html.Li('''This experiment is often used as an introduction to agent-based modeling and demonstrates that
                counter-intuitive results can emerge at the societal level due to the complexities of group dynamics.'''),

            ], style={'font-size': '1.25rem'}),


            html.Br(),
            html.Br(),


        ], style={'margin': 'auto',
               'text-align': 'left',
               'max-width': '750px'}),

        html.Br(),
        html.Br(),

        # intro
        html.Div([

            html.H3('''Introduction'''),

            html.P('''Social scientists have observed that people of similar race tend to cluster together,
            leading to predominantly white, black or Hispanic neighborhoods rather than a multiracial mixed
            alternative. Why is this the case? The causes of this residential segregation are likely complex
            and motivated by social, economic and political factors but as a starting point let’s consider a
            simplifying thought experiment.'''),


            html.P('''Imagine that people are motivated solely by a personal preference to not be too much of an
            outsider. For example, say that a white household would be happy to live in a neighborhood as long as at
            least one out of every three of the residents in the neighborhood were also white. In this case,
            the white household would be perfectly content if the majority of his neighbors were “dissimilar” to
            him just so long as he wasn’t too heavily outnumbered.'''),

            html.P('''Now imagine the entire population, individuals of all races, held similar preferences.
            What do we think would happen? A perfectly intuitive line of thought would be that since everyone is
            accepting of people of other races in their neighborhood, even going so far as to be willing to be a
            minority, that neighborhoods would generally be mixed. Unfortunately, this is an example when our
            intuition fails us and a perfectly plausible theory fails to reflect the complexity of even an extremely
            simplified reality.'''),

            html.P('''This tool will demonstrate the application of agent-based modeling (ABM) to explaining
            residential segregation and also expose the concept and process of ABM itself.  Agent-based modeling
            is a bottom-up framework that involves programming individual agents with behavior and goals and
            simulating their interactions with each other and the environment. The goal of this app is to show
            how ABM is often used to analyze group behavior and can reveal unexpected dynamics that emerge from
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
            policies that have historically segregated minorities into localized neighborhoods via land use regulations
            or mortgage discrimination. Furthermore, a more passive phenomena that has been documented has been
            racial steering whereby real estate brokers are likely to steer clients towards particular neighborhoods
            based on race.'''),

            html.P('''In addition to these external factors, housing choices may of course also stem from personal
            preferences which may include favoring neighborhoods due to proximity to family, the availability of
            familiar food options or the possibility of forming social networks with people of similar values.
            Collectively these preferences for amount to what social scientists call an in-group preference, or
            a preference for one’s own culture, and which will be the focus of this app.'''),

            html.P('''Though this app will use residential segregation as a way to discuss ABM, it is not a
            comprehensive overview of the complex social, political and economic dynamics. While computer scientists
            are able to contribute to the conversation, as will be demonstrated in this app, a serious discussion of
            this topic deserves a multidisciplinary approach with perspectives from historians, statisticians and
            economists.''', style={'background-color': 'lightyellow', 'border': '2px solid black', 'border-radius': '20px', 'padding': '6px'}),

            html.Br(),

            html.H3('''Agent-based Modeling Methodology'''),

            html.P('''The objective of agent-based modeling is to replicate reality using a programmed computer
            simulation that is as simple as possible. In our case, we want to simulate residential evolutions that
            reproduce observed segregation patterns, or the clustering of different groups, based on as few factors
            in our computer program as possible. If we are able to replicate observed reality, we will have “explained”
            housing segregation in the sense that our simulation shows that housing segregation is an outcome of our
            programmed assumptions. '''),

            html.P('''It’s important to note that within the ABM framework “explanation” has a different meaning
            than in statistics. Where in statistics explanation is associated with correlation, within ABM the
            meaning of explanation has connotations of causality since we explicitly define cause and effect dynamics
            within our simulation (the challenge however is to encode accurate cause and effect relationships).
            Furthermore, whereas in statistics we usually try to control for many different factors by including
            different variables in the analysis, within ABM it is preferable to construct a parsimonious model to
            show the minimum required assumptions that would be required to reproduce reality. '''),

            html.Br(),

            html.H3('''Simulation'''),

            html.P('''To program our segregation simulation we model a simplified reality. We represent a city as a
            2D grid, like a checkerboard, and each square in the grid represents a residence that can be occupied by
            a household. Our course, real neighborhoods do not physically look like a crowded checkboard but we assume
            that this simplification, amongst many assumptions we’ll make, is not material to the analysis.'''),

            html.P('''Next we assume in our model that there are two types of households (say White and Asian or
            Lannister and Targaryen) and that each household is primarily concerned about belonging to a neighborhood
            filled with similar neighbors. To measure the similarity of a neighborhood for a given household, we define
            a neighborhood as the adjacent houses within some radius and then calculate the proportion of households
            that belong to the “same” group and the proportion of households belonging to the “other” group. Depending
            on a household’s tolerance level, the household can then either decide to move to a new neighborhood or to
            stay.'''),



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

        ], style={'margin': 'auto',
                  'text-align': 'left',
                  'max-width': '900px'}),

        html.Br(),
        html.Br(),




        # Introduction
        html.Div([

            html.Hr(),

            html.H4('Figure 1: Migration Simulation'),

            dbc.Row([

                dbc.Col([

                    html.Img(src='/assets/test_gif.gif'),

                ], width=7),

                dbc.Col([

                    html.H5('''From an initial integrated state, two populations eventually segregate over
                    time.'''),

                    html.Br(),

                    html.P('''Each square represents a household that considers whether to remain or move to a different
                    spot in the grid. Households make the decision based on a simple logic: Stay if at least 40% of
                    its neighbors are a similar color, or else move otherwise. Even though everyone is content
                    to be a minority and live in an integrated neighborhood, over time the grid becomes
                    segregated.''')
                ], width=5),

            ]),

            html.Hr(),

        ] , style={'margin': 'auto',
               'text-align': 'left',
               'max-width': '1100px'}),

        html.Br(),
        html.Br(),








        # interactive tool: example neighborhood similarity calculation
        html.Div([

            html.Hr(),

            html.Br(),

            html.H3('Segregation Simulation'),

            html.Br(),

            dbc.Row([

                dbc.Col([
                    html.Div('simulator here'),
                    html.Div(id='simulator')
                ], width=9),

                dbc.Col([

                    html.Div('''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
                    incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
                    ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit
                    in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat
                    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'''),

                    html.Br(),


                ], width=3),

            ]),

        ], style={'margin': 'auto',
                  'text-align': 'left',
                  'max-width': '1000px'}),



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

