
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
            this topic deserves a multidisciplinary approach with perspectives from historians, statisticians,
            economists and others.''',
                   style={'background-color': 'lightyellow',
                          'border': '2px solid black',
                          'border-radius': '20px',
                          'padding': '6px'}),

            html.Br(),

            html.H3('''Agent-based Modeling Philosophy'''),

            html.P('''The objective of agent-based modeling is to replicate reality using a computer
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

            html.H3('''Simulation Methodology'''),

            html.P('''To program our segregation simulation we model a simplified reality. We represent a city as a
            2D grid, like a checkerboard, and each square in the grid represents a residence that can be occupied by
            a household. Our course, real neighborhoods do not physically look like a crowded checkboard but we assume
            that this simplification, amongst many assumptions we’ll make, is not material to the analysis.'''),

            html.P('''Next we assume in our model that there are two types of households (say White and Asian or
            Houses Gryffindor and Voldemort) and that each household is primarily concerned about belonging to a neighborhood
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
            html.Br(),


            html.Div([

                html.P('''Our analysis proceeds using the methodology described above, which is based around the
                simple premise that households might have a preference to live in a neighborhood that reflects their
                ethnic identity. When that preference is very strong, a White household might only be content if 90%
                of their neighbors are also White. On the other hand, if the preference is relatively weak then a
                Hispanic household might be perfectly content in a neighborhood that is only 20% Hispanic. '''),

                html.P('''Before we run the experiment and bias our opinions, it is an opportune time to ask what are
                our expectations? Without overthinking the question, here are two uneducated though reasonable guesses
                on what we might observe from the simulation:'''),

                html.Ul([

                    dcc.Markdown('''*Inclusive racial attitudes should lead to integrated neighborhoods.* If
                    households have a low in-group preference, then we expect to see more mixed neighborhoods over time.
                    Conversely, if households have a high in-group preference, then we would expect to see more
                    segregated neighborhoods.'''),

                ]),

                html.Ul([

                    dcc.Markdown('''*The level of diversity in a neighborhood is likely to be equal to the average
                    preference level.* If the average household preference is 55%, then we might expect that that the
                    average neighborhood will be composed of a 55-45 split between the two groups (or replace 55% with
                    any percentage and matching split)''')

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



        ], style={'font-size': '1.1rem',
                  'margin': 'auto',
                  'max-width': '750px',
                  'text-align': 'left',
                  }),

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
            # https://github.com/jbortfeld/QuantView

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