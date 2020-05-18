
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

# source data for actuarial calculations
# https://www.ssa.gov/oact/STATS/table4c6.html#fn2
# https://www.longevityillustrator.org

def serve_layout():


    return [

    html.Div([

        html.Div([

        html.Br(),

        dbc.Row(
            [
                dbc.Col(html.H1("Retirement Planning in Easy Mode",
                className='display-4',
                style={'text-align': 'center',
                'color': '#26BE81',}), width=12),
            ],
            align="center",
            no_gutters=True,
        ),

        html.Br(),

        html.Div('''Planning your finances can be complicated. Here are five questions that
        that can help you build a rough, but fast, roadmap for your future.''', style={'text-align': 'center',
        'color': 'grey'}),

        html.Br(),

        html.Br(),

        dbc.Row(
            [

                dbc.Col(width=1),

                dbc.Col(
                html.Div('How Old Are You Now?', className='input-questions')
               , width=2),

                dbc.Col(
                html.Div('At What Age Do You Want to Retire?', className='input-questions')
                , width=2),

                dbc.Col(
                html.Div([
                html.Div('How Much Have You Currently Saved?', className='input-questions'),
                ],  style={'text-align': 'center', 'font-size': '48px', 'color': 'green'}), width=2),

                dbc.Col(
                html.Div([
                html.Div('How Much Do You Save a Year?', className='input-questions'),
                ],  style={'text-align': 'center', 'font-size': '48px', 'color': 'green'}), width=2),

                dbc.Col(
                html.Div([
                html.Div('How Much Will You Spend Per Year in Retirement?', className='input-questions'),
                ],  style={'text-align': 'center', 'font-size': '48px', 'color': 'green'}), width=2),

                dbc.Col(width=1),


            ],
            align="center",
            no_gutters=True,
        ),

        dbc.Row(
            [

                dbc.Col(width=1),

                dbc.Col([
                        dcc.Input(id='my_age_input', value='39', className='input-box'),
                ], width=2),

                dbc.Col([
                        dcc.Input(id='retirement_age_input', value='46',className='input-box'),
                ], width=2),

                dbc.Col([
                    dcc.Input(id='my_wealth_input', value='1100000', className='input-box'),
                ], width=2),

                dbc.Col([
                        dcc.Input(id='my_save_input', value='105000', className='input-box'),
                ], width=2),

                dbc.Col([
                        dcc.Input(id='my_spend_input', value='70000', className='input-box'),
                ], width=2),

                dbc.Col(width=1),


            ],
            align="center",
            no_gutters=True,
        ),

        html.Br(),
        html.Br(),

        html.Div([
        dbc.Button("GO", id='start_input', style={'height': '100px', 'width': '200px', 'font-size': '80px',
        'text-align': 'center', 'background-color': '#26BE81', 'border': '5px solid #267B83',
        'margin-bottom': '30px'})],
        style={'text-align': 'center'}),

        html.Br(),
        html.Br(),
        html.Br(),

        html.Div(id='output'),
        ], className='body')

    ], style={'padding-left': '5%', 'padding-right': '5%'})

    ]


def calc_wealth_trajectory(starting_wealth, returns, contribution, add_first_obs_as_starting_wealth = True):
    
    # get the number of periods to simulate, based on the length of the returns simulation
    num_simulations = returns.shape[0]
    num_periods = returns.shape[1]

    # init an array that is the same shape as the inputted return
    # (this will be a [num_simulations x num_periods]-sized array)
    wealths = np.zeros_like(returns)
    
    # for every simulation, iterate through each period and update the wealth based on the prior period
    # wealth, the return in the given period and the contribution in that period
    current_wealths = np.copy(starting_wealth)
    
    if num_periods > 0:
        for i in range(num_periods):
            current_wealths = current_wealths.flatten() * (1 + returns[:,i]).flatten() + contribution
            wealths[:,i] = current_wealths
            
    if add_first_obs_as_starting_wealth:
        starts = np.full(shape=(num_simulations, 1), fill_value=starting_wealth)
        wealths = np.concatenate([starts, wealths], axis=1)
    
    return wealths

def random_walk_simulations(mean, stdev, periods, num_simulations):

    # draw random numbers from a normal distribution with specified mean and standard deviation
    # the result is an [num_simulations x periods] array of simulated returns
    random_returns = np.random.normal(mean, stdev, size=[num_simulations,periods])
    
    # convert to returns that can be cumulatively multiplied
    # for example, a 3.4% return is now 1.034
    cum_returns = random_returns.copy()
    cum_returns += 1
    
    # calculate the cumulative product
    cum_returns = np.cumprod(cum_returns, axis=1)

    return random_returns, cum_returns


def wealth_distributions(x):
    '''
    calculate the distribution statistics for a set of wealth trajectories over time. 
    for each period, calculate the mean, median, 25th, 10th, 5th and 1st percentiles of wealth across
    the simulated wealth trajectories
     
     
    let the input x be an array of size [num_simulations x num_periods].
    :return: a dictionary of arrays. For example, given an input array x that represents 
    m simulations with each simulation covering n periods, the 'means' key in the dictionary will return 
    an array of n elements, representing the n periods, and the ith element represents the 
    mean across the m simulations for the ith period. 
    '''
        
    means = np.mean(x, axis=0)
    medians = np.median(x, axis=0)
    p25 = np.percentile(x, 25, axis=0)
    p10 = np.percentile(x, 10, axis=0)
    p5 = np.percentile(x, 5, axis=0)
    p1 = np.percentile(x, 1, axis=0)

    return {'mean': means, 
           'median': medians,
           'pct25': p25,
            'pct10': p10,
            'pct5': p5,
            'pct1': p1
           }


layout = serve_layout

mortality_df = pd.read_csv('mortality_table.csv')
mortality_df.set_index('current_age', inplace=True)
mortality_df['forward_survival_prob_1y'] = 1- ((mortality_df['forward_death_prob_1y_male'] +
    mortality_df['forward_death_prob_1y_female']) / 2)



# calculate account trajectory
@app.callback(dash.dependencies.Output('output', 'children'),

            [dash.dependencies.Input('start_input', 'n_clicks')],
              
              [dash.dependencies.State('my_age_input', 'value'),
              dash.dependencies.State('retirement_age_input', 'value'),
              dash.dependencies.State('my_wealth_input', 'value'),
              dash.dependencies.State('my_save_input', 'value'),
              dash.dependencies.State('my_spend_input', 'value')
              ])
def display_page(n_clicks, 
    user_age,
    user_retirement_age, 
    user_wealth,
    user_save,
    user_spend):

    print(n_clicks)

    #if n_clicks is None:
    if n_clicks == 0:
        return html.Div()

    else:

        # derive extra parameters for modelling wealth trajectory
        user_age = int(user_age)
        user_retirement_age = int(user_retirement_age)
        user_wealth = int(user_wealth)
        user_save = int(user_save)
        user_spend=int(user_spend)

        years_to_retire = user_retirement_age - user_age
        years_in_retirement = 105 - user_retirement_age
        current_year = datetime.datetime.now().year
        years_to_105 = 105-user_age + 1


        # expected age at death based on mortality tables
        this_mortality_df = mortality_df.copy()
        expected_age_at_death = this_mortality_df.loc[user_age,'expected_years_till_death_male']
        expected_age_at_death += this_mortality_df.loc[user_age,'expected_years_till_death_female']
        expected_age_at_death /= 2
        expected_age_at_death = int(expected_age_at_death) + user_age

        # calculate the cumulative survival probabilities 
        # (what age is the user expected to live to with 25%, 5%, 1% probability conditional
        # on their current age)

        # first, subset the dataset to drop ages that are less than the users expected age at death
        # (this is going to be the 50% survivial probability)
        this_mortality_df = this_mortality_df[user_age:]
        this_mortality_df['cum_survival_prob'] = this_mortality_df['forward_survival_prob_1y'].cumprod()
        
        age_list = this_mortality_df.index.tolist()
        cum_survival_prob_list = this_mortality_df['cum_survival_prob'].tolist()

        def calc_age_for_survival_prob(target_survival_prob, age_list, cum_survival_prob_list):
            for i in range(len(age_list)):
                if cum_survival_prob_list[i] <= target_survival_prob:
                    return age_list[i]
            return 999

        age_at_25_pct_survival_prob = calc_age_for_survival_prob(0.25, age_list, cum_survival_prob_list)
        age_at_10_pct_survival_prob = calc_age_for_survival_prob(0.10, age_list, cum_survival_prob_list)
        age_at_5_pct_survival_prob = calc_age_for_survival_prob(0.05, age_list, cum_survival_prob_list)
        age_at_1_pct_survival_prob = calc_age_for_survival_prob(0.01, age_list, cum_survival_prob_list)
        years_to_1_pct_survival_prob = age_at_1_pct_survival_prob - user_age
        years_in_retirement = age_at_1_pct_survival_prob - user_retirement_age + 1

        # init a dataframe with ages and calendar years in the rows
        # the ages range from the current user age to the age that the user has a 1% probability of reaching
        # (for example, a 40 year old today might have a 1% chance of living to 100 so let's have the
        # chart x-axis show values from age 39 to age 100)
        df = pd.DataFrame({'age': list(range(user_age, age_at_1_pct_survival_prob + 1))})
        df['year'] = list(range(current_year, current_year + years_to_1_pct_survival_prob + 1))

        # generate random market returns
        return_simulations, cum_return_simulations = random_walk_simulations(0.04, 0.14, years_to_1_pct_survival_prob, 10000)
        
        # calc wealth during savings phase
        # init an [num_simulations x 1]-sized array with the starting wealth 
        starting_wealth_array = np.full(shape=(return_simulations.shape[0], 1), 
            fill_value=user_wealth)

        # calculate the growth of wealth given market returns and contributions during the savings phase
        wealths1 = calc_wealth_trajectory(starting_wealth=starting_wealth_array,
            returns=return_simulations[:,:years_to_retire],
            contribution=user_save,
            add_first_obs_as_starting_wealth=True)

        # get the final wealth values (as array) at the end of the last year of the savings phase
        # (the wealth at the start of retiremente)
        wealth_at_retirement = wealths1[:,-1]

        # calc wealth during retirement phase
        wealths2 = calc_wealth_trajectory(starting_wealth=wealth_at_retirement,
            returns=return_simulations[:, years_to_retire:],
            contribution=-user_spend,
            add_first_obs_as_starting_wealth=False)

        wealths3 = np.concatenate([wealths1, wealths2], axis=1)
        trajectories = wealth_distributions(wealths3)
        mean_trajectory = trajectories['median']


        df['wealth'] = mean_trajectory
        
        # make a chart with wealth over time
        

        # the bars that represent wealth during the savings phase should be green
        # and the bars during the retirement phase are blue
        #bar_colors = ['#26BE81'] * (years_to_retire)
        bar_colors = ['#7971ea'] * (years_to_retire)
        #bar_colors = bar_colors + ['#2663be'] * (years_in_retirement + 1)
        bar_colors = bar_colors + ['#f8615a'] * (years_in_retirement + 1)

        # make chart
        data = [
            {'x': df['age'],
            'y': df['wealth'],
            'type': 'bar',
            'marker': {'color': bar_colors}},
        ]
        
        chart_lines = [
        
            # vertical line at expected age at death (50% survival probability)
            {
            'x0': expected_age_at_death,
            'y0': 0,
            'x1': expected_age_at_death,
            'y1': 1,
            'yref': 'paper',
            'type': 'line',
            'line': {'color': 'orange', 'width': 5, 'dash': 'dot'}
            },

            {
            'x0': age_at_25_pct_survival_prob,
            'y0': 0,
            'x1': age_at_25_pct_survival_prob,
            'y1': 1,
            'yref': 'paper',
            'type': 'line',
            'line': {'color': 'orange', 'width': 4, 'dash': 'dot'}
            },

            {
            'x0': age_at_5_pct_survival_prob,
            'y0': 0,
            'x1': age_at_5_pct_survival_prob,
            'y1': 1,
            'yref': 'paper',
            'type': 'line',
            'line': {'color': 'orange', 'width': 3, 'dash': 'dot'}
            },

            {
            'x0': age_at_1_pct_survival_prob,
            'y0': 0,
            'x1': age_at_1_pct_survival_prob,
            'y1': 1,
            'yref': 'paper',
            'type': 'line',
            'line': {'color': 'orange', 'width': 2, 'dash': 'dot'}
            },

        ]

        chart_annotations = [
            {'x': expected_age_at_death,
             'y': -0.2,
             'yref': 'paper',
             'text': 'Your Life Expectancy'.format(expected_age_at_death),
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 16}},

            {'x': age_at_10_pct_survival_prob,
             'y': -0.3,
             'yref': 'paper',
             'text': 'Probabilities of Living To These Ages',
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 12}},


              {'x': age_at_25_pct_survival_prob,
             'y': -0.2,
             'yref': 'paper',
             'text': '25%',
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 12}},

              {'x': age_at_5_pct_survival_prob,
             'y': -0.2,
             'yref': 'paper',
             'text': '5%',
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 12}},

              {'x': age_at_1_pct_survival_prob,
             'y': -0.2,
             'yref': 'paper',
             'text': '1%',
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 12}}

        ]


        layout={'title': 'Your Expected Wealth Over Time',
        'annotations': chart_annotations,
        'height': 300,
        'margin': {'t': 30},
        'shapes': chart_lines,
        }

        figure = {'data': data,
        'layout': layout}


        mortality_x = np.arange(expected_age_at_death,105, .01)
        mortality_y = scipy.stats.norm.pdf(mortality_x, expected_age_at_death, 15)


        return html.Div([

            # first result section
            dbc.Row(
            [
                dbc.Col(

                    html.Div([

                        html.H1("You're in Excellent Shape!", className='display-6', 
                            style={'text-align': 'center','color': '#26BE81',}),

                        html.H4("You are on track for financial security for the rest of your life", className='display-6', 
                            style={'text-align': 'center','color': '#grey',})

                    ])


                , width=5),
                
                dbc.Col(
                    dcc.Graph(id='chart', figure = figure)
                , width=7),


            ], align="center", no_gutters=True,
            ),

            html.Br(),

            # second result section
            html.Div([

                dbc.Row([
                    dbc.Col(

                        html.Div([

                            html.H1("In 2024, as your target retirement age of 46:", className='display-6', 
                                style={'text-align': 'center','color': 'white',}),

                        ])
                    , width=12),


                ], align="center", no_gutters=True),


                dbc.Row([
                    dbc.Col(

                        html.Div([

                            html.H1("hello my world", className='display-6', 
                                style={'text-align': 'center','color': 'white',}),

                        ])
                    , width=6),

                    dbc.Col(

                        html.Div([

                            html.H3("You are projected to retire with $2.3M in savings", className='display-6', 
                                style={'text-align': 'center','color': 'white',}),

                        ])
                    , width=6),


                ], align="center", no_gutters=True),

                html.Br(),

                dbc.Row([
                    dbc.Col(

                        html.Div([

                            html.H1("hello my world", className='display-6', 
                                style={'text-align': 'center','color': 'white',}),

                        ])
                    , width=6),

                    dbc.Col(

                        html.Div([

                            html.H3("This is based on average market returns of 6% per year", className='display-6', 
                                style={'text-align': 'center','color': 'white',}),

                        ])
                    , width=6),


                ], align="center", no_gutters=True),

                html.Br(),

                dbc.Row([
                    dbc.Col(

                        html.Div([

                            html.H1("hello my world", className='display-6', 
                                style={'text-align': 'center','color': 'white',}),

                        ])
                    , width=6),

                    dbc.Col(

                        html.Div([

                            html.H3("And an eventual portfolio balance that is 60% stocks, 40% bonds", className='display-6', 
                                style={'text-align': 'center','color': 'white',}),

                        ])
                    , width=6),


                ], align="center", no_gutters=True),

            ], className='green-background')

          
        ])
