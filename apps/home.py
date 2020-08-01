
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
                        dbc.Col(
                            html.H1("Retirement Planning in Easy Mode",
                                    className='display-4 app-header', id='app-title')
                        )
                    ],
                ),

                html.Br(),

                dbc.Row([

                    dbc.Col('', width=1),

                    dbc.Col(
                        html.Img(src='questionnaire.png', style={'height': '150px'}), width=2),

                    dbc.Col(
                        html.Div('''Planning your finances can be complicated. Here are five questions that
                                    that can help you build a rough, but fast, roadmap for your future.''', className='text-note', style={'text-align': 'left'})
                        , width=7),

                    dbc.Col('', width=2),



                ], no_gutters=True, align='center'),

                html.Br(),
                html.Br(),


                dbc.Row(
                    [

                        dbc.Col(width=1),

                        dbc.Col(
                            html.Div('How Old Are You Now?', className='input-questions', style={'width': '75%', 'margin': 'auto'}), width=2),

                        dbc.Col(
                            html.Div('At What Age Do You Want to Retire?', className='input-questions'), width=2),

                        dbc.Col(
                            html.Div('How Much Have You Currently Saved?', className='input-questions'), width=2),

                        dbc.Col(
                            html.Div('How Much Do You Save a Year?', className='input-questions'), width=2),

                        dbc.Col(
                            html.Div('How Much Will You Spend Per Year in Retirement?', className='input-questions'), width=2),

                        dbc.Col(width=1),


                    ],
                    align="center",
                    no_gutters=True,
                ),

                dbc.Row(
                    [

                        dbc.Col(width=1),

                        dbc.Col([
                            dcc.Input(id='my_age_input', value='30',
                                      className='input-box'),
                        ], width=2),

                        dbc.Col([
                            dcc.Input(id='retirement_age_input',
                                      value='60', className='input-box'),
                        ], width=2),

                        dbc.Col([
                            dcc.Input(id='my_wealth_input', value='$30,000',
                                      className='input-box'),
                        ], width=2),

                        dbc.Col([
                            dcc.Input(id='my_save_input', value='$9,000',
                                      className='input-box'),
                        ], width=2),

                        dbc.Col([
                            dcc.Input(id='my_spend_input', value='$60,000',
                                      className='input-box'),
                        ], width=2),

                        dbc.Col(width=1),


                    ],
                    align="center",
                    no_gutters=True,
                ),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),


                html.Div([
                    dbc.Button("GO",
                               id='start_input',
                               className='go-button',
                               )],
                         ),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),


                # THIS IS THE CONTAINER FOR THE MAIN APP OUTPUT
                dbc.Spinner(html.Div(id='output'), color='#2FC086', size='lg'),

            ], className='body')

        ], style={'padding-left': '0%', 'padding-right': '0%'}),
        visdcc.Run_js(id='javascript')

    ]


layout = serve_layout

mortality_df = pd.read_csv('mortality_table.csv')
mortality_df.set_index('current_age', inplace=True)
mortality_df['forward_survival_prob_1y'] = 1 - ((mortality_df['forward_death_prob_1y_male'] +
                                                 mortality_df['forward_death_prob_1y_female']) / 2)


@app.callback(dash.dependencies.Output('javascript', 'run'),
              [dash.dependencies.Input('my_wealth_input', 'n_blur'),
               dash.dependencies.Input('my_save_input', 'n_blur'),
               dash.dependencies.Input('my_spend_input', 'n_blur'),
               dash.dependencies.Input('my_wealth_input', 'value'),
               dash.dependencies.Input('my_save_input', 'value'),
               dash.dependencies.Input('my_spend_input', 'value'),
               ])
def reformat_input(wealth_change, save_change, spend_change,
                   user_wealth, user_save, user_spend):

    print(user_wealth, user_save, user_spend)

    if wealth_change or save_change or spend_change:

        try:
            num1 = int(float(user_wealth.replace(',', '').replace('$', '')))
            num1 = '${:,}'.format(num1)
        except:
            num1 = '$0'

        try:
            num2 = int(float(user_save.replace(',', '').replace('$', '')))
            num2 = '${:,}'.format(num2)
        except:
            num2 = '$0'

        try:
            num3 = int(float(user_spend.replace(',', '').replace('$', '')))
            num3 = '${:,}'.format(num3)
        except:
            num3 = '$0'

        js = '''
        var wealth = document.getElementById("my_wealth_input");
        wealth.value='{}'

        var save = document.getElementById("my_save_input");
        save.value='{}'

        var spend = document.getElementById("my_spend_input");
        spend.value='{}'
        '''.format(num1, num2, num3)

        return js


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

    if n_clicks is None:
        return html.Div(),

    else:

        # 1. set model parameters
        params = {'user_age': int(user_age),
                  'user_retirement_age': int(user_retirement_age),
                  'user_wealth': int(float(user_wealth.replace(',', '').replace('$', ''))),
                  'user_save': int(float(user_save.replace(',', '').replace('$', ''))),
                  'user_spend': int(float(user_spend.replace(',', '').replace('$', ''))),

                  'user_social_security_age': 67,
                  'user_social_security_benefit': 18000,
                  'num_simulations': 10000,

                  # derive extra parameters for modelling wealth trajectory
                  'years_to_retire': int(user_retirement_age) - int(user_age),
                  'years_to_retire_plus_one': int(user_retirement_age) - int(user_age) + 1,
                  'years_to_retire_minus_one': int(user_retirement_age) - int(user_age) - 1,
                  'current_year': datetime.datetime.now().year
                  }

        # expected age at death based on mortality tables
        user_mortality, age_list = fn.get_user_mortality_stats(
            params['user_age'], mortality_df)

        params['user_mortality'] = user_mortality
        params['age_list'] = age_list
        params['years_to_1_pct_survival_prob'] = user_mortality[
            '1%'] - params['user_age']
        params['years_in_retirement'] = user_mortality[
            '1%'] - params['user_retirement_age'] + 1
        params['num_periods'] = user_mortality['1%'] - params['user_age'] + 1

        # get the index at retirement and at the final age
        params['idx_at_retirement'] = params[
            'user_retirement_age'] - params['user_age']
        params['idx_at_final_age'] = user_mortality['1%'] - params['user_age']

        # 3. simulate equity market returns based on a random walk
        equity_return_sim1 = fn.random_walk_simulations(mean=0.08,
                                                        stdev=0.14,
                                                        periods=params[
                                                            'num_periods'],
                                                        num_simulations=params['num_simulations'])

        # set bond market returns
        bond_return_sim1 = np.full_like(equity_return_sim1, fill_value=0.01)
        bond_return_sim1[:, 0] = 0.0

        # INACTIVE FOR NOW, USE RANDOM WALK RETURNS FOR SIMULATIONS
        # (THE HISTORICAL RETURNS ARE CONSIDERED TP BE TOO HIGH TO BE USED FOR MODELING FUTURE RETURNS)
        # # get historical annual returns to use in sampling
        # years, sp500, ust_3m, ust, bbb = fn.get_historical_annual_returns()
        # num_historical_samples = len(years)

        # # simulate market returns based on continuous historical sampling
        # _, equity_return_sim2, bond_return_sim2 = fn.build_continuous_sampled_returns(num_periods_per_simulation=num_periods,
        #                                                                               num_simulations=num_simulations,
        #                                                                               year_list=years,
        #                                                                               sp500_list=sp500,
        # ust_list=ust)

        # # simulate market returns based on discontinuous historical sampling
        # _, equity_return_sim3, bond_return_sim3 = fn.build_discontinuous_sampled_returns(num_periods_per_simulation=num_periods,
        #                                                                                  sub_sample_length=5,
        #                                                                                  num_simulations=num_simulations,
        #                                                                                  year_list=years,
        #                                                                                  sp500_list=sp500,
        # ust_list=ust)

        # equity_returns = np.concatenate(
        #     [equity_return_sim1, equity_return_sim2, equity_return_sim2], axis=0)
        # bond_returns = np.concatenate(
        #     [bond_return_sim1, bond_return_sim2, bond_return_sim2], axis=0)

        equity_returns = equity_return_sim1
        bond_returns = bond_return_sim1

        # 5. calculate wealth scenarios

        # 5a. calculate asset allocation between equity and bonds in each
        # period
        contributions = fn.calc_contributions(user_age=params['user_age'],
                                              retirement_age=params[
                                                  'user_retirement_age'],
                                              final_age=params[
                                                  'user_mortality']['1%'],
                                              user_save=params['user_save'],
                                              user_spend=params['user_spend'],
                                              user_social_security_age=params[
                                                  'user_social_security_age'],
                                              user_social_security_benefit=params['user_social_security_benefit'])

        total_user_save, starting_wealth_array, allocations, contributions, wealths, trajectories, wealth_stats = fn.financial_plan(params, contributions, equity_returns,
                                                                                                                                    bond_returns)

        # 2. build a dataframe that we'll use for making charts that show wealth over time
        # the ages range from the current user age to the age that the user has a 1% probability of reaching
        # (for example, a 40 year old today might have a 1% chance of living to 100 so let's have the
        # chart x-axis show values from age 39 to age 100, inclusive)
        df = pd.DataFrame(
            {'age': list(range(params['user_age'], params['user_mortality']['1%'] + 1))})
        df['year'] = list(range(params['current_year'], params['current_year'] +
                                params['years_to_1_pct_survival_prob'] + 1))

        # add wealth paths to the chart data
        df['Optimistic (75th pct)'] = trajectories[75]
        df['Expected (Average Outcome)'] = trajectories['mean']
        df['Possible (25th pct)'] = trajectories[25]
        df['Pessimistic (5th pct)'] = trajectories[5]

        assert df.shape[0] == params['num_periods'], 'error'

        # make a table with information about wealth at the time of retirement
        retirement_df = pd.DataFrame({
            'Scenario': ['Optimistic (75th percentile)', 'Expected (Average Outcome)', 'Possible (25th pct)', 'Pessimistic (5th pct)'],
            '$ at Retirement': [fn.dollar_as_text(wealth_stats[i]['wealth_at_retirement']) for i in [75, 'mean', 25, 5]],
            'Stock Market Avg Return': [fn.percent_as_text(wealth_stats[i]['rate_of_return_at_retirement']) for i in [75, 'mean', 25, 5]],
            'Bond Return': ['1%', '1%', '1%', '1%'],
            '"Forever Income (4%)"': [fn.dollar_as_text(wealth_stats[i]['wealth_at_retirement'] * 0.04) for i in [75, 'mean', 25, 5]],

        })

        # make a table with information about when wealth may be depleted

        asset_depleted_text = [fn.depleted_text(wealth_stats[i]['age_at_negative_wealth'],
                                                wealth_stats[i][
                                                    'wealth_at_end'],
                                                wealth_stats[i]['wealth_at_retirement']) for i in [75, 50, 25, 5]]
        depleted_df = pd.DataFrame({
            'Scenario': ['Optimistic (75th percentile)',
                         'Expected (Avg Outcome)',
                         'Possible (25th pct)',
                         'Pessimistic (5th pct)'],
            'Stock Market Avg Return': [fn.percent_as_text(wealth_stats[i]['rate_of_return_at_end']) for i in [75, 'mean', 25, 5]],
            'Bond Return': ['1%', '1%', '1%', '1%'],
            'Your Assets will': asset_depleted_text,
            'At the Age of 101, You will Have': [fn.dollar_as_text(wealth_stats[i]['wealth_at_end']) for i in [75, 'mean', 25, 5]],

        })

        # make a chart with wealth over time

        # the bars that represent wealth during the savings phase should be green
        # and the bars during the retirement phase are blue
        bar_colors = ['#26BE81'] * (params['years_to_retire'])
        bar_colors = bar_colors + ['green']
        bar_colors = bar_colors + ['#26BE81'] * \
            (params['years_in_retirement'] + 1)

        # make chart that shows median wealth over time
        data1 = [
            {'x': df['age'],
             'y': df['Expected (Average Outcome)'],
             'type': 'bar',
             'marker': {'color': bar_colors}},
        ]

        chart_lines = [

            # veritcal line when user starts to take social security
            {
                'x0': params['user_social_security_age'],
                'y0': 0,
                'x1': params['user_social_security_age'],
                'y1': 1,
                'yref': 'paper',
                'type': 'line',
                'line': {'color': 'purple', 'width': 5, 'dash': 'dot'}
            },


            # vertical line at expected age at death (50% survival probability)
            {
                'x0': params['user_mortality']['expected_age_at_death'],
                'y0': 0,
                'x1': params['user_mortality']['expected_age_at_death'],
                'y1': 1,
                'yref': 'paper',
                'type': 'line',
                'line': {'color': 'orange', 'width': 5, 'dash': 'dot'}
            },

            {
                'x0': params['user_mortality']['25%'],
                'y0': 0,
                'x1': params['user_mortality']['25%'],
                'y1': 1,
                'yref': 'paper',
                'type': 'line',
                'line': {'color': 'orange', 'width': 4, 'dash': 'dot'}
            },

            {
                'x0': params['user_mortality']['5%'],
                'y0': 0,
                'x1': params['user_mortality']['5%'],
                'y1': 1,
                'yref': 'paper',
                'type': 'line',
                'line': {'color': 'orange', 'width': 3, 'dash': 'dot'}
            },

            {
                'x0': params['user_mortality']['1%'],
                'y0': 0,
                'x1': params['user_mortality']['1%'],
                'y1': 1,
                'yref': 'paper',
                'type': 'line',
                'line': {'color': 'orange', 'width': 2, 'dash': 'dot'}
            },

        ]

        chart_annotations = [
            {'x': params['user_retirement_age'],
             'y': -0.3,
             'yref': 'paper',
             'text': 'Retirement',
             'showarrow': False,
             'font': {'color': 'green', 'family': 'avenir', 'size': 12}},

            {'x': params['user_social_security_age'],
             'y': -0.2,
             'yref': 'paper',
             'text': 'Social Security',
             'showarrow': False,
             'font': {'color': 'purple', 'family': 'avenir', 'size': 12}},

            {'x': params['user_mortality']['expected_age_at_death'],
             'y': -0.2,
             'yref': 'paper',
             'text': '50%',
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 12}},

            {'x': params['user_mortality']['10%'],
             'y': -0.3,
             'yref': 'paper',
             'text': 'Probabilities of Living To These Ages',
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 12}},


            {'x': params['user_mortality']['25%'],
             'y': -0.2,
             'yref': 'paper',
             'text': '25%',
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 12}},

            {'x': params['user_mortality']['5%'],
             'y': -0.2,
             'yref': 'paper',
             'text': '5%',
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 12}},

            {'x': params['user_mortality']['1%'],
             'y': -0.2,
             'yref': 'paper',
             'text': '1%',
             'showarrow': False,
             'font': {'color': 'orange', 'family': 'avenir', 'size': 12}}

        ]

        layout1 = {'title': '<b>Your Expected Wealth Over Time</b>',
                   'annotations': chart_annotations,
                   'height': 350,
                   'margin': {'t': 40, 'r': 10},
                   'shapes': chart_lines,
                   }

        figure1 = {'data': data1,
                   'layout': layout1}

        # make multiple charts that shows wealth paths over time
        data75 = [
            {'x': df['age'],
             'y': df['Optimistic (75th pct)'],
             'type': 'bar',
             'name': 'Pessimistic',
             'marker': {'color': '#D3F2E5'}},
        ]

        data50 = [
            {'x': df['age'],
             'y': df['Expected (Average Outcome)'],
             'type': 'bar',
             'name': 'Expected',
             'marker': {'color': '#26BE81'}},
        ]

        data25 = [
            {'x': df['age'],
             'y': df['Possible (25th pct)'],
             'type': 'bar',
             'name': 'Possible',
             'marker': {'color': '#D3F2E5'}},
        ]

        data5 = [
            {'x': df['age'],
             'y': df['Pessimistic (5th pct)'],
             'type': 'bar',
             'name': 'Pessimistic',
             'marker': {'color': '#D3F2E5'}},
        ]

        layout75 = {'title': '<b>Optimistic Scenario ({} Avg Stock Market Return) </b>'.format(fn.percent_as_text(wealth_stats[75]['rate_of_return_at_end'])),
                    'titlefont': {'color': '#267B83'},
                    'annotations': chart_annotations,
                    'height': 300,
                    'margin': {'t': 30, 'r': 10},
                    'shapes': chart_lines,
                    }

        layout50 = {'title': '<b>Expected Scenario ({} Avg Stock Market Return) </b>'.format(fn.percent_as_text(wealth_stats['mean']['rate_of_return_at_end'])),
                    'titlefont': {'color': '#26BE81'},
                    'annotations': chart_annotations,
                    'height': 300,
                    'margin': {'t': 30, 'r': 10},
                    'shapes': chart_lines,
                    }

        layout25 = {'title': '<b>Possible Scenario ({} Avg Stock Market Return) </b>'.format(fn.percent_as_text(wealth_stats[25]['rate_of_return_at_end'])),
                    'titlefont': {'color': '#267B83'},
                    'annotations': chart_annotations,
                    'height': 300,
                    'margin': {'t': 30, 'r': 10},
                    'shapes': chart_lines,
                    }

        layout5 = {'title': '<b>Pessimistic Scenario ({} Avg Stock Market Return) </b>'.format(fn.percent_as_text(wealth_stats[5]['rate_of_return_at_end'])),
                   'titlefont': {'color': '#267B83'},
                   'annotations': chart_annotations,
                   'height': 300,
                   'margin': {'t': 30, 'r': 10},
                   'shapes': chart_lines,
                   }

        figure75 = {'data': data75,
                    'layout': layout75}

        figure50 = {'data': data50,
                    'layout': layout50}

        figure25 = {'data': data25,
                    'layout': layout25}

        figure5 = {'data': data5,
                   'layout': layout5}

        # build scenario analysis tables

        # run scenario analysis that simulate different saving, spending and time-to-retirement assumptions
        # (this is performed by controlling the 'contribution' array. Either increase the contriution amounts
        # during the savings phase, or extend the length of the savings phase, or decrease the spend during retirement)
        # each final element of the 'scenario_analysis' dictionary is an array that represents additions/subtractions
        # from assets

        scenario_analysis = {'save_more': {i: {'age_at_negative_wealth': {},
                                               'wealth_at_retirement': {},
                                               'wealth_at_end': {},
                                               'forever_income': {}
                                               } for i in range(4)},
                             'work_longer': {i: {'age_at_negative_wealth': {},
                                                 'wealth_at_retirement': {},
                                                 'wealth_at_end': {},
                                                 'forever_income': {}} for i in range(4)},
                             'spend_less': {i: {'age_at_negative_wealth': {},
                                                'wealth_at_retirement': {},
                                                'wealth_at_end': {},
                                                'forever_income': {}} for i in range(4)}}

        for i in range(4):

            scenario_analysis['save_more'][i]['save_amount'] = fn.dollar_as_text(
                params['user_save'] + (0.05 * params['user_save'] * i))

            _contributions = fn.calc_contributions(user_age=params['user_age'],
                                                   retirement_age=params[
                                                       'user_retirement_age'],
                                                   final_age=params[
                                                       'user_mortality']['1%'],
                                                   user_save=params[
                                                       'user_save'] + (0.05 * params['user_save'] * i),
                                                   user_spend=params[
                                                       'user_spend'],
                                                   user_social_security_age=params[
                                                       'user_social_security_age'],
                                                   user_social_security_benefit=params['user_social_security_benefit'])

            _, _, _, _, _, _, _wealth_stats = fn.financial_plan(
                params, _contributions, equity_returns, bond_returns)

            for pct in [75, 'mean', 25, 5]:
                scenario_analysis['save_more'][i]['age_at_negative_wealth'][
                    pct] = _wealth_stats[pct]['age_at_negative_wealth']
                scenario_analysis['save_more'][i]['wealth_at_retirement'][
                    pct] = _wealth_stats[pct]['wealth_at_retirement']
                scenario_analysis['save_more'][i]['wealth_at_end'][
                    pct] = _wealth_stats[pct]['wealth_at_end']
                scenario_analysis['save_more'][i]['forever_income'][
                    pct] = _wealth_stats[pct]['wealth_at_retirement'] * 0.04

            scenario_analysis['work_longer'][i][
                'retire_age'] = params['user_retirement_age'] + (1 + i)
            _contributions = fn.calc_contributions(user_age=params['user_age'],
                                                   retirement_age=params[
                                                       'user_retirement_age'] + (1 + i),
                                                   final_age=params[
                                                       'user_mortality']['1%'],
                                                   user_save=params[
                                                       'user_save'],
                                                   user_spend=params[
                                                       'user_spend'],
                                                   user_social_security_age=params[
                                                       'user_social_security_age'],
                                                   user_social_security_benefit=params['user_social_security_benefit'])

            new_params = params.copy()
            new_params['idx_at_retirement'] = new_params[
                'user_retirement_age'] + (1 + i) - params['user_age']
            _, _, _, _, _, _, _wealth_stats = fn.financial_plan(
                new_params, _contributions, equity_returns, bond_returns)
            for pct in [75, 'mean', 25, 5]:
                scenario_analysis['work_longer'][i]['age_at_negative_wealth'][
                    pct] = _wealth_stats[pct]['age_at_negative_wealth']
                scenario_analysis['work_longer'][i]['wealth_at_retirement'][
                    pct] = _wealth_stats[pct]['wealth_at_retirement']
                scenario_analysis['work_longer'][i]['wealth_at_end'][
                    pct] = _wealth_stats[pct]['wealth_at_end']
                scenario_analysis['work_longer'][i]['forever_income'][
                    pct] = _wealth_stats[pct]['wealth_at_retirement'] * 0.04

            scenario_analysis['spend_less'][i]['spend_amount'] = fn.dollar_as_text(
                params['user_spend'] - ((0.05 * params['user_spend']) * i))

            _contributions = fn.calc_contributions(user_age=params['user_age'],
                                                   retirement_age=params[
                                                       'user_retirement_age'],
                                                   final_age=params[
                                                       'user_mortality']['1%'],
                                                   user_save=params[
                                                       'user_save'],
                                                   user_spend=params[
                                                       'user_spend'] - ((0.05 * params['user_spend']) * i),
                                                   user_social_security_age=params[
                                                       'user_social_security_age'],
                                                   user_social_security_benefit=params['user_social_security_benefit'])

            _, _, _, _, _, _, _wealth_stats = fn.financial_plan(
                params, _contributions, equity_returns, bond_returns)
            for pct in [75, 'mean', 25, 5]:
                scenario_analysis['spend_less'][i]['age_at_negative_wealth'][
                    pct] = _wealth_stats[pct]['age_at_negative_wealth']
                scenario_analysis['spend_less'][i]['wealth_at_retirement'][
                    pct] = _wealth_stats[pct]['wealth_at_retirement']
                scenario_analysis['spend_less'][i]['wealth_at_end'][
                    pct] = _wealth_stats[pct]['wealth_at_end']
                scenario_analysis['spend_less'][i]['forever_income'][
                    pct] = _wealth_stats[pct]['wealth_at_retirement'] * 0.04

        df_save_more = pd.DataFrame({'Savings Per Year': [scenario_analysis['save_more'][i]['save_amount'] for i in range(4)],
                                     'Wealth at Retirement': [fn.dollar_as_text(scenario_analysis['save_more'][i]['wealth_at_retirement'][5]) for i in range(4)],
                                     'Forever Income': [fn.dollar_as_text(scenario_analysis['save_more'][i]['forever_income'][5]) for i in range(4)],
                                     'Run out of Money at': [scenario_analysis['save_more'][i]['age_at_negative_wealth'][5] for i in range(4)],
                                     })

        df_work_longer = pd.DataFrame({'Retirement Age': [scenario_analysis['work_longer'][i]['retire_age'] for i in range(4)],
                                       'Wealth at Retirement': [fn.dollar_as_text(scenario_analysis['work_longer'][i]['wealth_at_retirement'][5]) for i in range(4)],
                                       'Forever Income': [fn.dollar_as_text(scenario_analysis['work_longer'][i]['forever_income'][5]) for i in range(4)],
                                       'Run out of Money at': [scenario_analysis['work_longer'][i]['age_at_negative_wealth'][5] for i in range(4)]
                                       })

        df_spend_less = pd.DataFrame({'Spending per year': [scenario_analysis['spend_less'][i]['spend_amount'] for i in range(4)],
                                      'Wealth at Retirement': [fn.dollar_as_text(scenario_analysis['spend_less'][i]['wealth_at_retirement'][5]) for i in range(4)],
                                      'Forever Income': [fn.dollar_as_text(scenario_analysis['spend_less'][i]['forever_income'][5]) for i in range(4)],
                                      'Run out of Money at': [scenario_analysis['spend_less'][i]['age_at_negative_wealth'][5] for i in range(4)]
                                      })

        outlook_header = "You're in Excellent Shape!"
        outlook_note = "You are on track for financial security for the rest of your life"
        expected_terminal_wealth = wealth_stats['mean']['wealth_at_end']
        pessimistic_terminal_wealth = wealth_stats[5]['wealth_at_end']
        if (expected_terminal_wealth > 0) & (pessimistic_terminal_wealth < 0):
            outlook_header = "Your Finances Look Good"
            outlook_note = "You are on a successful path to financial security but adverse market returns could derail your plans"
        if (expected_terminal_wealth < 0) & (pessimistic_terminal_wealth < 0):
            outlook_header = "Warning: You are Likely to Exhaust Your Savings"
            outlook_note = "Your long-term financial plan may not be feasible"

        num1 = int(float(user_wealth.replace(',', '').replace('$', '')))
        num1 = '${:,}'.format(num1)

        num2 = int(float(user_save.replace(',', '').replace('$', '')))
        num2 = '${:,}'.format(num2)

        num3 = int(float(user_spend.replace(',', '').replace('$', '')))
        num3 = '${:,}'.format(num3)

        js = '''
        var wealth = document.getElementById("my_wealth_input");
        wealth.value='{}'

        var save = document.getElementById("my_save_input");
        save.value='{}'

        var spend = document.getElementById("my_spend_input");
        spend.value='{}'
        '''.format(num1, num2, num3)

        js = ''

        return html.Div([

            html.Hr(),

            # first result section
            html.Div([
                dbc.Row(
                    [
                        dbc.Col(

                            html.Div([

                                html.H1(outlook_header,
                                        style={'text-align': 'center', 'color': '#26BE81', 'font-weight': 'bold'}),

                                html.H4(outlook_note, className='display-6 text-note',
                                        style={'text-align': 'center', 'color': '#grey', })

                            ]), width=5),

                        dbc.Col(
                            dcc.Graph(id='chart', figure=figure1), width=7),


                    ], align="center", no_gutters=True,
                ),
            ], style={'margin-left': '10%', 'margin-right': '10%'}),

            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),

            # second result section
            html.Div([

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                dbc.Row([
                    dbc.Col(

                        html.Div([

                            html.H1("In {}, at your target retirement age of {}:".format(params['current_year'] + params['years_to_retire'],
                                                                                         params['user_retirement_age']),
                                    style={'text-align': 'center', 'color': 'white', }),

                        ]), width=12),


                ], align="center", no_gutters=True),

                html.Br(),

                dbc.Row([

                    dbc.Col(
                        html.Div([
                            html.Img(src='money.png', style={
                                     'height': '150px'}),
                            html.Br(),
                            html.Br(),
                            html.H4('''You'll have contributed an additional {} to savings over the next {} years'''.format(total_user_save,
                                                                                                                            params['user_retirement_age'] - params['user_age'] - 1))
                        ]), width=6, style={'padding-left': '10%', 'padding-right': '10%'}),

                    dbc.Col(
                        html.Div([
                            html.Img(src='stock-market.png',
                                     style={'height': '150px'}),
                            html.Br(),
                            html.Br(),
                            html.H4('''And we assumed your investments glide into a 60/40 split between stocks 
                                and bonds by the time you retire''')
                        ]), width=6, style={'padding-left': '10%', 'padding-right': '10%'})
                ], style={'padding-top': '50px'}),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                dbc.Row([

                    dbc.Col(
                        '', width=2),

                    dbc.Col(html.Img(src='spreadsheet.png',
                                     style={'height': '150px'}), width=2),


                    dbc.Col(
                        html.Div([

                            html.H4("We don't actually know what the market will do, so we've mapped out a few scenarios for \
                     how your savings might grow until retirement", style={'margin-left': '0%', 'margin-right': '15%', 'display': 'inline-block'})
                        ]), width=8),
                ]),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                dbc.Table.from_dataframe(retirement_df, style={'color': 'white', 'font-size': '1.5rem'}, borderless=True,
                                         hover=True,
                                         striped=True),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                html.H1(
                    '''The money you save will be used to generate income for you in retirement when you are not working'''),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

            ], className='green-background', style={'padding-left': '10%', 'padding-right': '10%'}),

            # third result section

            html.Div([

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                html.H1("During retirement, your nest egg will have to last up to {} years".format(params['user_mortality']['1%'] - params['user_retirement_age']),
                        className='display-6',
                        style={'text-align': 'center', 'color': '#26BE81', 'margin-left': '10%', 'margin-right': '10%'}),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                dbc.Row([

                    dbc.Col(
                        html.Div([

                            html.Img(src='profit.png', style={
                                     'height': '150px'}),

                            html.H4('''We assume your nest egg will generate income based on a 60/40 split between
                            stocks and bonds''', style={'color': '#267B83'})

                        ]), width=4),
                    dbc.Col(
                        html.Div([

                            html.Img(src='pension.png', style={
                                     'height': '150px'}),

                            html.H4('''And we assume you'll receive $1,500 each month in social security benefits starting
                            at age 67''', style={'color': '#267B83'})

                        ]), width=4),
                    dbc.Col(
                        html.Div([

                            html.Img(src='invoice.png', style={
                                     'height': '150px'}),

                            html.H4('''And you'll spend {} each year on expenses'''.format(fn.dollar_as_text(params['user_spend'])), style={
                                    'color': '#267B83'})

                        ]), width=4),

                ], no_gutters=False),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),


                html.H4('''Based on your savings and your anticipated spending, your financial security is measured by how likely 
                    your wealth can last you for the rest of your life:''', style={
                        'color': '#267B83', 'margin-left': '10%', 'margin-right': '10%'}),


                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                dbc.Table.from_dataframe(depleted_df,
                                         style={'color': '#267B83', 'font-size': '1.5rem'}, borderless=True,
                                         hover=True,
                                         striped=True),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                html.Details([

                    html.Summary('View Wealth Scenario Charts'),

                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),


                    dbc.Row([

                        dbc.Col(
                            html.Div(dcc.Graph(id='chart75', figure=figure75, style={'height': 300})), width=6),

                        dbc.Col(
                            html.Div(dcc.Graph(id='chart50', figure=figure50, style={'height': 300})), width=6)
                    ]),

                    dbc.Row([

                        dbc.Col(
                            html.Div(dcc.Graph(id='chart25', figure=figure25, style={'height': 300})), width=6),

                        dbc.Col(
                            html.Div(dcc.Graph(id='chart5', figure=figure5, style={'height': 300})), width=6)
                    ])

                ]),



            ], style={'margin-left': '8%', 'margin-right': '8%'}),

            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),


            # 4th Results Section
            html.Div([

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                html.H1("Suggestions to improve your financial outlook",
                        className='display-6',
                        style={'margin-left': '10%', 'margin-right': '10%'}),

                html.Div('''You can't control the market, but you do have three main avenues for reducing the chance you'd 
                    run out of money during retirement, even in the pessimistic scenario''', className='white-text text-note'),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),



                dbc.Row([

                    dbc.Col(
                        html.Div([

                            html.Img(src='save-money.png',
                                     style={'height': '150px'}),

                            html.Br(),
                            html.Br(),

                            html.H4(
                                '''Save more in the years leading up to retirement''')

                        ]), width=4),


                    dbc.Col(
                        html.Div([

                            dbc.Table.from_dataframe(df_save_more, style={'color': 'white', 'font-size': '1.5rem'}, borderless=True,
                                                     hover=True,
                                                     striped=True),



                        ]), width=8),

                ], no_gutters=False),

                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                dbc.Row([

                    dbc.Col(
                        html.Div([

                            html.Img(src='briefcase.png', style={
                                     'height': '150px'}),

                            html.Br(),
                            html.Br(),

                            html.H4('''Work longer while delaying retirement''')

                        ]), width=4),


                    dbc.Col(
                        html.Div([

                            dbc.Table.from_dataframe(df_work_longer, style={'color': 'white', 'font-size': '1.5rem'}, borderless=True,
                                                     hover=True,
                                                     striped=True),


                        ]), width=8),

                ], no_gutters=False),


                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),

                dbc.Row([

                    dbc.Col(
                        html.Div([

                            html.Img(src='fishing.png', style={
                                     'height': '150px'}),

                            html.Br(),
                            html.Br(),

                            html.H4('''Spend less during retirement''')

                        ]), width=4),


                    dbc.Col(
                        html.Div([

                            dbc.Table.from_dataframe(df_spend_less, style={'color': 'white', 'font-size': '1.5rem'}, borderless=True,
                                                     hover=True,
                                                     striped=True),



                        ]), width=8),

                ], no_gutters=False),


                html.Br(),
                html.Br(),
                html.Br(),
                html.Br(),




            ], className='green-background', style={'padding-left': '10%', 'padding-right': '10%'}),

            html.Script('hello', type="text/javascript",
                        src="//counter.websiteout.net/js/17/6/0/0"),
            html.A('Icons made by Freepik',
                   href='https://www.flaticon.com/authors/freepik'),



        ])


@app.callback(dash.dependencies.Output("collapse", "is_open"),
              [dash.dependencies.Input("collapse-button", "n_clicks")],
              [dash.dependencies.State("collapse", "is_open")],
              )
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
