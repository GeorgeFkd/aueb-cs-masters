from math import sqrt,log,pow,e
from collections.abc import Callable

import numpy as np
import matplotlib.pyplot as plt
print("Hello world from python3")

class EnvParams:
    seed=0
    amount_of_avail_actions = 10 # 10-armed bandit problem
    initial_action_values=np.zeros((1,1))
    type="" #stationary or non-stationary
    random_walk_step=""
    reward_std=1
    steps=1000
class AllStrategiesParams:
    strategy="" #epsilon-greedy, upper-confidence-bound, soft-max-preference
    value_estimate_update_rule="" # "mean","exponential_decay"
    epsilon=0 # epsilon param for the epsilon greedy strategies
    c=0 #for upper confidence bound strategy
    alpha=0 # params used in updating the reward estimate

def create_default_env() -> EnvParams:
    env_params = EnvParams()
    env_params.seed = 123
    env_params.initial_action_values = np.zeros((1,1))
    env_params.type = "non-stationary"
    env_params.reward_std = 1
    env_params.steps = 1000
    return env_params


def calc_softmax_for(preferences):
    # print("Ht=",preferences)
    z_exp = np.exp(preferences - np.max(preferences))
    return z_exp / np.sum(z_exp)


def run_n_armed_bandit(exec_params:EnvParams,strategy_params:AllStrategiesParams,n=10):
    #if optimistic initial values, this should probably change
    Qt = np.zeros(exec_params.amount_of_avail_actions)
    Nt = np.zeros(exec_params.amount_of_avail_actions)
    preferences = np.zeros(exec_params.amount_of_avail_actions)
    average_reward = 0
    avg_reward_per_step = []
    optimal_action_per_step = []
    # if the problem is stationary this only happens once
    random_vals = np.random.normal(0,1,size=exec_params.amount_of_avail_actions)

    for step in range(exec_params.steps):
        # if exec_params.type == "non-stationary":
        #     random_vals = random_vals + np.random.normal(0,1,size=exec_params.amount_of_avail_actions)
        action_chosen = -1
        p_t_a = np.zeros(exec_params.amount_of_avail_actions)
        if strategy_params.strategy == "epsilon-greedy":
            val = np.random.uniform(0,1)
            if strategy_params.epsilon !=- 1 and val < strategy_params.epsilon:
                #choose randomly
                action_chosen = np.random.randint(0,exec_params.amount_of_avail_actions)
            else:
                #choose greedily
                action_chosen = np.argmax(Qt)
        elif strategy_params.strategy.lower() == "ucb" or strategy_params.strategy.lower() == "upper-confidence-bound":
            # confidence_vals = [strategy_params.c * sqrt(log(step+1) / (action_usage_times + 0.0000001)) for action_usage_times in Nt]
            confidence_vals = [
                strategy_params.c * np.sqrt(np.log(step + 1) / Nt[a]) if Nt[a] > 0 else float('inf')
                for a in range(exec_params.amount_of_avail_actions)
            ]
            action_chosen = np.argmax(Qt + confidence_vals)
        elif strategy_params.strategy == "soft-max-preference" or "softmax" in strategy_params.strategy or "gradient" in strategy_params.strategy:
            p_t_a = calc_softmax_for(preferences)
            # this here might not be correct
            action_chosen = np.random.choice(np.arange(exec_params.amount_of_avail_actions), p=p_t_a)
            pass
        # a valid action has been chosen
        assert(action_chosen != -1 and action_chosen < exec_params.amount_of_avail_actions)


        Nt[action_chosen] = Nt[action_chosen] + 1
        reward = random_vals[action_chosen]
        noisy_reward = reward + np.random.normal(0,1)
        if strategy_params.strategy == "epsilon-greedy":
            Qt[action_chosen] = Qt[action_chosen] + (1/Nt[action_chosen]) * (noisy_reward - Qt[action_chosen])
        if strategy_params.strategy == "soft-max-preference" or "softmax" in strategy_params.strategy or "gradient" in strategy_params.strategy:
            preferences = preferences - strategy_params.alpha * (noisy_reward - average_reward) * p_t_a
            preferences[action_chosen] = preferences[action_chosen] + strategy_params.alpha * (noisy_reward - average_reward) * (1-p_t_a[action_chosen])
        # Gradient Bandit ( i did not get it right most likely )
        #preferences = preferences - [strategy_params.alpha * (noisy_reward - average_reward) * prob for prob in p_t_a ]
        # changed p_t_a to 1-p_t_a let's see
        #preferences[action_chosen] = preferences[action_chosen] + strategy_params.alpha * (noisy_reward - average_reward) * (1-p_t_a[action_chosen])
        # calculate statistics
        # this might be wrong, instead of noisy reward it might be the reward
        average_reward = average_reward + (1/(step+1)) * (noisy_reward - average_reward)
        avg_reward_per_step.append(average_reward)
        # not sure about this
        optimal_action_per_step.append((reward,np.argmax(random_vals)))
    return avg_reward_per_step,optimal_action_per_step


def eval_strategy_in_bandit_task(exec_params:EnvParams,strategy_params:AllStrategiesParams,tasks=2000):
    test_results = []
    for i in range(tasks):
        exec_params.seed = exec_params.seed + 1
        avg_rewards_per_step,optimal_action_per_step = run_n_armed_bandit(exec_params, strategy_params)
        test_results.append({"avg_rewards":avg_rewards_per_step,"seed":exec_params.seed,"optimal_actions":optimal_action_per_step})
    aggregate_results = []
    optimal_percentage_of_action = []
    for step in range(exec_params.steps):
        #it threw an error here
        aggregate_results.append(0)
        optimal_percentage_of_action.append(0)
        for task_results in test_results:
            aggregate_results[step] = task_results["avg_rewards"][step] + aggregate_results[step]
            opt_percentage = task_results["optimal_actions"][step][0]+ 0.000001 / (task_results["optimal_actions"][step][1] + 0.00001)
            optimal_percentage_of_action[step] = optimal_percentage_of_action[step] + opt_percentage
        aggregate_results[step] = aggregate_results[step] / tasks
        optimal_percentage_of_action[step] = optimal_percentage_of_action[step] / tasks

    x_vals_avg = range(len(aggregate_results))
    y_vals_avg = aggregate_results
    x_vals_optimal = range(len(optimal_percentage_of_action))
    y_vals_optimal = optimal_percentage_of_action
    return x_vals_avg,y_vals_avg,x_vals_optimal,y_vals_optimal

def eval_epsilon_greedy(epsilon):
    #todo find the optimal value for ε
    strategy_params = AllStrategiesParams()
    strategy_params.strategy = "epsilon-greedy"
    strategy_params.epsilon = epsilon
    exec_params = create_default_env()
    np.random.seed(exec_params.seed)
    x_vals_avg,y_vals_avg,x_vals_optimal,y_vals_optimal = eval_strategy_in_bandit_task(exec_params, strategy_params)
    print(f"After a thousand steps epsilon-greedy, with ε={epsilon} it converges to: {y_vals_avg[len(y_vals_avg)-1]}")
    # plt.figure(figsize=(8, 6))
    # plt.plot(x_vals_avg, y_vals_avg, linestyle='-', color='b')
    # plt.plot(x_vals_optimal, y_vals_optimal, linestyle='-', color='r')
    # plt.title(f"10-armed bandits-epsilon-greedy(ε={epsilon})")
    # plt.yticks([0,0.5,1,1.5] + [y_vals_avg[len(y_vals_avg)-1]])
    # plt.xlabel("Steps")
    # plt.ylabel("Average Reward")
    # plt.show()
    return y_vals_avg

def eval_ucb_strategy(c):
    # it does go higher than e-greedy so we doing ok
    #TODO find the optimal value for c
    strategy_params = AllStrategiesParams()
    strategy_params.strategy = "ucb"
    strategy_params.c = c
    exec_params = create_default_env()
    np.random.seed(exec_params.seed)
    x_vals_avg,y_vals_avg,x_vals_optimal,y_vals_optimal = eval_strategy_in_bandit_task(exec_params, strategy_params)
    print(f"After a thousand steps of ucb, with c={c} it converges to: {y_vals_avg[len(y_vals_avg)-1]}")
    # # plt.figure(figsize=(8, 6))
    # fig,(ax1,ax2) = plt.subplots(2,figsize=(8,6))
    # fig.suptitle("Multi Armed Bandits Strategies UCB")
    # ax1.plot(x_vals_avg, y_vals_avg, linestyle='-', color='b')
    # # ax1.set_title(f"10-armed bandits UCB(c={c})")
    # ax1.set_yticks([0,0.5,1,1.5] + [y_vals_avg[len(y_vals_avg)-1]])
    # ax1.set_xlabel("Steps")
    # ax1.set_ylabel("Average Reward")
    #
    # ax2.plot(x_vals_optimal, y_vals_optimal, linestyle='-', color='r')
    # # ax2.set_title(f"10-armed bandits UCB(c={c})")
    # ax2.set_xlabel("Steps")
    # ax2.set_ylabel("Optimal %")
    # plt.show()
    return y_vals_avg

def eval_gradient_strategy(alpha):
    # it is wrong
    strategy_params = AllStrategiesParams()
    strategy_params.strategy = "softmax"
    strategy_params.alpha = alpha
    exec_params = create_default_env()
    np.random.seed(exec_params.seed)
    x_vals_avg,y_vals_avg,x_vals_optimal,y_vals_optimal = eval_strategy_in_bandit_task(exec_params, strategy_params)
    print(f"After a thousand steps of Gradient Bandit, with α={alpha} it converges to: {y_vals_avg[len(y_vals_avg)-1]}")
    # plt.figure(figsize=(8, 6))
    # plt.subplot(nrows=4,ncols=3)
    # plt.title(f"10-armed bandits Gradient(α={alpha})")
    # plt.yticks([0,0.5,1,1.5] + [y_vals_avg[len(y_vals_avg)-1]])
    # plt.xlabel("Steps")
    # plt.ylabel("Average Reward")
    # plt.plot(x_vals_avg, y_vals_avg, linestyle='-', color='b')
    # plt.subplot(nrows=4,ncols=3)
    # plt.plot(x_vals_optimal, y_vals_optimal, linestyle='-', color='b')
    # plt.title(f"10-armed bandits Gradient(α={alpha})")
    # plt.yticks([0,0.5,1,1.5] + [y_vals_avg[len(y_vals_avg)-1]])
    # plt.xlabel("Steps")
    # plt.ylabel("Optimal %")
    # plt.show()
    return y_vals_avg




# to do figure 2.5, we need for x->log(tuned parameter vals)
# y-> average reward.
def eval_ucb_for_vals(vals_arr):
    x_axis = []
    y_axis = []
    for c in vals_arr:
        result = eval_ucb_strategy(c)
        #just grab the value it converged to
        result = result[-1]
        x_axis.append(c)
        y_axis.append(result)
    return x_axis,y_axis
def eval_gradient_for_vals(vals_arr):
    x_axis = []
    y_axis = []
    for alpha in vals_arr:
        result = eval_gradient_strategy(alpha)
        #just grab the value it converged to
        result = result[-1]
        x_axis.append(alpha)
        y_axis.append(result)
    return x_axis,y_axis

    pass
def eval_greedy_for_vals(vals_arr):
    x_axis = []
    y_axis = []
    for epsilon in vals_arr:
        result = eval_epsilon_greedy(epsilon)
        #just grab the value it converged to
        result = result[-1]
        x_axis.append(epsilon)
        y_axis.append(result)
    return x_axis,y_axis

def display_stats_of_all_strategies(args):
    """Gets as input tuples of x,y and plots them as in the figure 2.5 of the book"""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Loop through the strategies and plot each one
    for results in args:
        ax.plot(results[0], results[1], label=results[2], color=results[3])

    # Set titles and labels
    ax.set_title('Average reward over first 1000 steps', fontsize=12, loc='left', pad=20)
    ax.set_xlabel('$\\alpha \\ / \\ c \\ / \\ Q_0$', fontsize=14)
    ax.set_ylabel('Average reward', fontsize=12)

    # Customize ticks
    ax.set_xscale('log')  # Set the x-axis to a logarithmic scale
    ax.set_xticks([1/128, 1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2, 4])
    ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())  # Use standard formatting for log scale

    # Add legend
    ax.legend(loc='upper left', fontsize=10)

    # Display the plot
    # plt.tight_layout()
    plt.show()



#with these vals i should get sth similar
# x_ucb,y_ucb = eval_ucb_for_vals([0.1,0.25,0.5,1,1.25,1.5,2.0,2.5,3])
# x_gradient,y_gradient = eval_gradient_for_vals([0.01,0.05,0.1,0.2,0.5,1,2])
# x_greedy,y_greedy = eval_greedy_for_vals([0,0.01,0.05,0.1,0.2,0.3])
#todo impl optimistic initial values for greedy
#display_stats_of_all_strategies([(x_ucb,y_ucb,"UCB","blue"),(x_gradient,y_gradient,"gradient bandit","green"),(x_greedy,y_greedy,"epsilon-greedy","red")])

