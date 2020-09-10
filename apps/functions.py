
import numpy as np
import pandas as pd


def calc_age_for_survival_prob(target_survival_prob, age_list, cum_survival_prob_list):
    for i in range(len(age_list)):
        if cum_survival_prob_list[i] <= target_survival_prob:
            return age_list[i]
    return 999


def calc_wealth_trajectory(starting_wealth, equity_returns, bond_returns, allocations, contributions):

    assert equity_returns.shape == allocations.shape, 'error: equity returns and allocations are not the same shape'
    assert equity_returns.shape == bond_returns.shape, 'error: equity returns and bond returns are not the same shape'
    assert equity_returns.shape == contributions.shape, 'error: equity returns and contributions are not the same shape'

    # get the number of periods to simulate, based on the length of the
    # returns simulation
    num_simulations = equity_returns.shape[0]
    num_periods = equity_returns.shape[1]

    # init an array that is the same shape as the inputted return
    # (this will be a [num_simulations x num_periods]-sized array)
    wealths = np.zeros_like(equity_returns)
    wealths[:, 0] = starting_wealth

    # for every simulation, iterate through each period and update the wealth based on the prior period
    # wealth, the return in the given period and the contribution/spend in
    # that period
    current_wealths = np.copy(starting_wealth)

    for i in range(num_periods):

        # update the wealth in period i as the wealth in period (i-1) times the investment return plus
        # the savings/spending

        # calculate returns in period i across all the simulations
        # the returns are calculated as asset return times allocation to that
        # asset
        equity_return_i = (
            1 + equity_returns[:, i]).flatten() * allocations[:, i].flatten()
        bond_return_i = (
            1 + bond_returns[:, i]).flatten() * (1.0 - allocations[:, i].flatten())
        contribution_i = contributions[:, i].flatten()

        current_wealths = ((current_wealths.flatten() * equity_return_i) +
                           (current_wealths.flatten() * bond_return_i) +
                           contribution_i)

        wealths[:, i] = current_wealths

    return wealths

def get_age_at_negative_wealth(trajectory, age_list):

    # find the index of the first instance when wealth for a given year
    # is negative
    i = next((x for x in iter(range(len(trajectory))) if trajectory[x] <= 0), 999)

    if i == 999:
        return 999
    else:
        return age_list[i]

def calc_wealth_milestones(trajectories, rates_of_return, age_list, idx_at_retirement, idx_at_final_age, years_to_retire_minus_one):

    wealth_stats ={}

    for i in ['mean', 75, 50, 25, 5, 1]:

        wealth_stats[i] = {}

        # get the $ value of weath at retirement for the given percentile
        # (eg 1200000)
        wealth_stats[i]['wealth_at_retirement'] = trajectories[i][idx_at_retirement]

         # get the average annualized rate of return of the stock market through the 
         # savings phase for the given percentile
        wealth_stats[i]['rate_of_return_at_retirement'] = calc_geometric_rate_of_return(start_value=1,
            end_value=rates_of_return[i][idx_at_retirement - 1],
            num_periods=years_to_retire_minus_one)

        # get the $ value of wealth at the max user age
        wealth_stats[i]['wealth_at_end'] = trajectories[i][idx_at_final_age]

        # get the average rate of return of the stock market until the max
        # user age
        wealth_stats[i]['rate_of_return_at_end'] = calc_geometric_rate_of_return(start_value=1,
                                                                          end_value=rates_of_return[i][
                                                                              idx_at_final_age - 1],
                                                                          num_periods=idx_at_final_age - 1)
        # find the index of the first instance when wealth for a given year
        # is negative
        temp = next((x for x in iter(range(len(trajectories[i]))) if trajectories[i][x] <= 0), 999)

        if temp == 999:
            wealth_stats[i]['age_at_negative_wealth'] = 999
        else:
            wealth_stats[i]['age_at_negative_wealth'] = age_list[temp]

    return wealth_stats

def financial_plan(params, contributions, equity_returns, bond_returns):

    rates_of_return = equity_returns[:, 1:]
    rates_of_return = rates_of_return + 1
    rates_of_return = np.cumprod(rates_of_return, axis=1)
    rates_of_return = wealth_distributions(rates_of_return)
            
    allocations = calc_asset_allocations(user_age=params['user_age'],
                                            retirement_age=params['user_retirement_age'],
                                            final_age=params['user_mortality']['1%'],
                                            percent_at_retirement=0.6,
                                            glide_length=10)

    # make an array of allocations for every simulation (previously 'allocations' was a single array of size
    # [1 x num_periods]. Now let's make it [num_simulations x num_periods] so that it is consistent with other arrays)
    allocations = np.array([allocations for i in range(params['num_simulations'])])

    # 5b. calculate the contributions and spending in each year

    # under the base case scenario, pull out the total amount saved by the
    # user during the savings phase
    total_user_save = contributions[:params['user_retirement_age'] - params['user_age']].sum()
    total_user_save = dollar_as_text(total_user_save)

    # convert contributions from [num_periods] array to [num_simulations x num_periods]
    contributions = np.array([contributions for i in range(params['num_simulations'])])

    # 5c. calc wealth over time
    # init an [num_simulations x 1]-sized array with the starting wealth
    # value for each element
    starting_wealth_array = np.full(
        shape=params['num_simulations'], fill_value=params['user_wealth'])

    # calculate the growth of wealth which incorporates market returns,
    # contributions and spending in each period
    wealths = calc_wealth_trajectory(starting_wealth=starting_wealth_array,
                                        equity_returns=equity_returns,
                                        bond_returns=bond_returns,
                                        allocations=allocations,
                                        contributions=contributions)

    # calculate the different wealth trajectories
    # (eg the median path, 25th percentile path, etc)
    trajectories = wealth_distributions(wealths)

    # 6. calculate stats about wealth trajectory

    # get the final wealth values (as array) at the start of retiremente)
    wealth_stats = calc_wealth_milestones(trajectories,
                                             rates_of_return,
                                             params['age_list'],
                                             params['idx_at_retirement'],
                                             params['idx_at_final_age'],
                                             params['years_to_retire_minus_one'])

    return total_user_save, starting_wealth_array, allocations, contributions, wealths, trajectories, wealth_stats



def depleted_text(depleted_age, final_wealth, wealth_at_retirement):
    if (depleted_age == 999) & (final_wealth > (1.2 * wealth_at_retirement)):
        return "👍 Grow Forever"
    elif (depleted_age == 999) & (final_wealth <= (1.2 * wealth_at_retirement)) & (final_wealth > (0.8 * wealth_at_retirement)):
        return "👍 Remain Roughly Stable Over Your Life"
    elif (depleted_age == 999) & (final_wealth <= (0.8 * wealth_at_retirement)):
        return "Decline But Last the Rest of Your Life"
    else:
        return "Run out at Age {}".format(depleted_age)


def calc_geometric_rate_of_return(start_value, end_value, num_periods):
    return ((end_value / start_value) ** (1 / num_periods)) - 1.0


def calc_contributions(user_age, retirement_age, final_age, user_save, user_spend, user_social_security_age, user_social_security_benefit):
    ''' 
    make an array that contains the contribution (or spend) for every period. 
    '''

    num_periods = final_age - user_age + 1
    age_list = list(range(user_age, final_age + 1))
    contributions = np.array([0] * num_periods)

    for i in range(num_periods):

        if age_list[i] < retirement_age:
            contributions[i] = user_save
        else:
            contributions[i] = -user_spend

        if age_list[i] >= user_social_security_age:
            contributions[i] += user_social_security_benefit


    # set first period (current user age) to zero
    contributions[0] = 0

    return contributions


def calc_asset_allocations(user_age, retirement_age, final_age, percent_at_retirement, glide_length):
    '''
    for every age, calculate the allocation "p" to stocks (with the assumption that 1-p is allocated to bonds)

    :return: an array with percent allocation to stocks for every year
    '''

    # init a set of parameters
    # (num of periods that we need to simualte, a list with the ages for each period and
    # an array that holds the allocation to stocks in each period)
    num_periods = final_age - user_age + 1
    age_list = list(range(user_age, final_age + 1))
    allocations = np.array([1.0] * num_periods)

    # iterate through all periods of the simulation
    for i in range(num_periods):

        # get the user's age in the current period
        current_age = age_list[i]

        # if user is at or in retirement, then set to target allocation
        if current_age >= retirement_age:
            allocations[i] = percent_at_retirement

        # else if user is still in savings phase, calculate a trajectory
        # where the user's allocation is graduatlly reduced from 100% to the
        # target allocation
        else:

            # get the age at which to start 'gliding' into the retirement
            # allocation
            glide_start_age = retirement_age - glide_length

            if current_age < glide_start_age:
                allocations[i] = 1.0
            else:
                decrement = (1.0 - percent_at_retirement) / \
                    (retirement_age - glide_start_age)
                allocations[i] = 1.0 - decrement * \
                    (current_age - glide_start_age)

    return allocations


def random_walk_simulations(mean, stdev, periods, num_simulations, set_first_obs_as_zero=True):
    '''
    simulate market returns by sampling from a normal distribution. Create a set of
    simulations, each composed of a series of returns.


    return a numpy array of size [num_simulations x periods] that represents several sequences
    of returns. 
    '''

    # draw random numbers from a normal distribution with specified mean and standard deviation
    # the result is an [num_simulations x periods] array of simulated returns
    random_returns = np.random.normal(
        mean, stdev, size=[num_simulations, periods])

    if set_first_obs_as_zero:
        random_returns[:, 0] = 0

    return random_returns


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
    p75 = np.percentile(x, 75, axis=0)
    p50 = np.percentile(x, 50, axis=0)
    p25 = np.percentile(x, 25, axis=0)
    p10 = np.percentile(x, 10, axis=0)
    p5 = np.percentile(x, 5, axis=0)
    p1 = np.percentile(x, 1, axis=0)

    return {'mean': means,
            'median': medians,
            75: p75,
            50: p50,
            25: p25,
            10: p10,
            5: p5,
            1: p1
            }


def dollar_as_text(x):
    if x >= 1000000:
        text = round((x / 1000000), 2)
        if text.is_integer():
            text = int(text)
        text = '${}M'.format(text)
    else:
        text = round((x / 1000), 2)
        if text.is_integer():
            text = int(text)
        text = '${}K'.format(text)

    return text

def percent_as_text(x):
    return str(round(x*100,2)) + '%'

def get_user_mortality_stats(user_age, mortality_table):

    user_mortality = {}

    # 1. get the expected age at death (average between male and female statistics)
    expected_age_at_death = mortality_table.loc[user_age, 'expected_years_till_death_male']
    expected_age_at_death += mortality_table.loc[user_age, 'expected_years_till_death_female']
    expected_age_at_death /= 2
    expected_age_at_death = int(expected_age_at_death) + user_age

    user_mortality['expected_age_at_death'] = expected_age_at_death

    # 2. calculate the cumulative survival probabilities
    # (what age is the user expected to live to with 25%, 5%, 1% probability conditional
    # on their current age)

    # first, subset the dataset to drop ages that are less than the users expected age at death
    # (this is going to be the 50% survivial probability)
    this_mortality_df = mortality_table[user_age:]
    this_mortality_df['cum_survival_prob'] = this_mortality_df['forward_survival_prob_1y'].cumprod()

    age_list = this_mortality_df.index.tolist()
    cum_survival_prob_list = this_mortality_df['cum_survival_prob'].tolist()

    user_mortality['25%'] = calc_age_for_survival_prob(0.25, age_list, cum_survival_prob_list)
    user_mortality['10%'] = calc_age_for_survival_prob(0.10, age_list, cum_survival_prob_list)
    user_mortality['5%'] = calc_age_for_survival_prob(0.05, age_list, cum_survival_prob_list)
    user_mortality['1%'] = calc_age_for_survival_prob(0.01, age_list, cum_survival_prob_list)

    return user_mortality, age_list


def get_historical_annual_returns():

    df = pd.read_csv('data/lt_annual_asset_returns.csv')
    df = df[['year', 'sp500_including_dividends_real_return',
             'ust_3m_real_return', 'ust_real_return', 'bbb_corporate_real_return']]

    # return columns are given as strings like '-2.56%'. Convert these to
    # floats
    for col in ['sp500_including_dividends_real_return', 'ust_3m_real_return', 'ust_real_return', 'bbb_corporate_real_return']:
        df[col] = df[col].map(lambda x: float(x.strip('%'))) / 100

    years = df['year'].tolist()
    sp500 = df['sp500_including_dividends_real_return'].tolist()
    ust_3m = df['ust_3m_real_return'].tolist()
    ust = df['ust_real_return'].tolist()
    bbb = df['bbb_corporate_real_return'].tolist()

    return years, sp500, ust_3m, ust, bbb


def build_single_continuous_sample_series(start_i, max_i, num_periods):
    index_list = list(range(start_i, start_i + num_periods))

    def _wrap(x, ceiling):

        if x < ceiling:
            return x
        else:
            return x - ceiling

    index_list = [_wrap(i, max_i) for i in index_list]

    return index_list


def build_continuous_sampled_returns(num_periods_per_simulation,
                                     num_simulations,
                                     year_list,
                                     sp500_list,
                                     ust_list,
                                     set_first_obs_as_zero=True):
    '''
    build simulated returns based on sampling continuous historical return series

    let's randomly sample from the observed annual returns history back to 1928 and construct
    continuous histories. As of 2020, we have 92 annual samples (1928-2019). We will pick a random number
    between 0 and 91, for example 5. The 5th observation corresponds to the year 1932 so that will be the start of
    our 'sampled history'. Let's say we want to simulate 40 years of market returns, which represents 40 years
    that we'll want to use to model savings and retirement periods. We will count 40 periods starting from 1932 which
    will give us the interval from 1932 to 1971. We will therefore use the SP500 returns from 1932 to 1971 and that
    will be our sampled return series. We then repeat 10,000 times to simulate returns based on historical data. 

    If the random number we pick is high, say 90, then we will wrap the series and start back at the first observation
    of 1928. For example, the 90th observation is 2017 and will use a return history based on [2017, 2018 ,2019 , 1928, 
    1929, 1930, ...]

    :num_periods: number of periods to simulate
    :num simulations: number of simulations to run


    '''
    num_of_samples = len(year_list)

    # pick N random numbers (uniform) over all sample periods
    # (for example, if we have 150 samples, we are going to pick a number between 0 and 149)
    randoms = np.random.randint(0, num_of_samples, size=num_simulations)

    all_sampled_sp500_returns = []
    all_sampled_ust_returns = []
    all_sampled_years = []

    for i in randoms:
        index_list = build_single_continuous_sample_series(start_i=i,
                                                           max_i=num_of_samples,
                                                           num_periods=num_periods_per_simulation)

        sampled_years = [year_list[i] for i in index_list]
        all_sampled_years.append(sampled_years)

        sampled_ust = [ust_list[i] for i in index_list]
        all_sampled_ust_returns.append(sampled_ust)

        sampled_sp500 = [sp500_list[i] for i in index_list]
        all_sampled_sp500_returns.append(sampled_sp500)

    # convert list of lists to numpy array
    all_sampled_years = np.array(all_sampled_years)
    all_sampled_sp500_returns = np.array(all_sampled_sp500_returns)
    all_sampled_ust_returns = np.array(all_sampled_ust_returns)

    if set_first_obs_as_zero:
        all_sampled_years[:, 0] = 0
        all_sampled_sp500_returns[:, 0] = 0
        all_sampled_ust_returns[:, 0] = 0

    return all_sampled_years, all_sampled_sp500_returns, all_sampled_ust_returns


def build_discontinuous_sampled_returns(num_periods_per_simulation,
                                        sub_sample_length,
                                        num_simulations,
                                        year_list,
                                        sp500_list,
                                        ust_list,
                                        set_first_obs_as_zero=True):
    '''
    construct simulated return series by sampling small windows from historical data. For example, we may want
    to construct a simualted 42 year return history. We want to sample random 5-year windows in history. We can 
    sample 8 of these 5-year windows which gives us 40 years of returns. We then need to sample a two year window 
    to get our full 42 year simulated history. 

    this is similar to build_continuous_return_series() but instead we sample small periods and string them 
    together to build a longer simulated history. By sampling several small windows, we gain more diversity
    of simulated trajectories but maintain some degree of serial correlation between continuous years. 
    '''

    # calculate the number of windows we'll need to contruct (if we want a 42 year history, and the
    # windows are of length 5, then num_sub_periods is 9 (which will give us a little extra at
    # 45 years rather than 42 but that's ok, we'll trim the excess later)
    num_sub_periods = int(num_periods_per_simulation / sub_sample_length)
    num_sub_periods += 1

    # pick num_sub_periods + 1 random numbers (uniform) over all sample periods
    num_of_samples = len(year_list)
    randoms = np.random.randint(0, num_of_samples, size=[
                                num_simulations, num_sub_periods])

    all_sampled_sp500_returns = []
    all_sampled_ust_returns = []
    all_sampled_years = []

    for i in randoms:

        # build a single simulation that consists of num_periods_per_simulation
        index_list = []
        for random_num in i:

            # based on the random num, get the next sub_sample_length numbers
            # (if the random num is 14 and sub_sample_length=6, then make a list
            # of [14,15,16])
            one_window = build_single_continuous_sample_series(start_i=random_num,
                                                               max_i=num_of_samples,
                                                               num_periods=sub_sample_length)

            index_list = index_list + one_window

        # trim any extra samples from the simulation
        index_list = index_list[:num_periods_per_simulation]

        # record this one simulation

        sampled_years = [year_list[i] for i in index_list]
        all_sampled_years.append(sampled_years)

        sampled_ust = [ust_list[i] for i in index_list]
        all_sampled_ust_returns.append(sampled_ust)

        sampled_sp500 = [sp500_list[i] for i in index_list]
        all_sampled_sp500_returns.append(sampled_sp500)

    all_sampled_years = np.array(all_sampled_years)
    all_sampled_sp500_returns = np.array(all_sampled_sp500_returns)
    all_sampled_ust_returns = np.array(all_sampled_ust_returns)

    if set_first_obs_as_zero:
        all_sampled_years[:, 0] = 0
        all_sampled_sp500_returns[:, 0] = 0
        all_sampled_ust_returns[:, 0] = 0

    return all_sampled_years, all_sampled_sp500_returns, all_sampled_ust_returns
