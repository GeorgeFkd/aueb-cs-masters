print("RL homework 3")
# This routine executes policy iteration for the car rental problem of Exercise 4.2. The state (m,n) is the number
# of cars in the two locations, and the policy is the number of cars moved from the first location to the second one
#
# Input Parameters
# ================
# environment_parameters={
#     location_sizes[2]: a vector containing the sizes of the two locations
#     location_return_rates[2]: a vector containing the Poisson car return rates at the two locations
#     location_request_rates[2]: a vector containing the Poisson car request rates at the two locations
#     transfer_cost: the cost of transferring a car from one location to the other
#     transfer_limit: the maximum number of cars that can be transferred from one location to the other
#     rental_reward: the reward of a single rental
#     }
#
# policy_parameters={
#     gamma: the discount factor
#     evaluations_number: the number of policy evaluations in each policy iteration
#     iterations_number: the number of policy iterations that will be executed
#     initial_policy: the initial policy applied to all states.
#     }
#
# verbosity: specifies how much will be printed
#     verbosity=0: nothing is printed
#     verbosity=1: results are printed at the end
#     verbosity=2: results are printed also at end of each policy iteration

import numpy as np
import scipy

np.set_printoptions(precision=2, suppress=True)

class EnvParams:
    location_sizes = [12,8]
    # Both are random Poisson Variables that have the λ indicated below
    location_return_rates =  np.array((1,2))
    location_return_rates[0] = 3
    location_return_rates[1] = 2
    location_request_rates = np.array((1,2))
    location_request_rates[0] = 3
    location_request_rates[1] = 4
    transfer_cost = 2
    transfer_limit = 5
    rental_reward = 10
class PolicyParams:
    gamma = 0.9
    evaluations_number = 3
    iterations_number = 100
    initial_policy = 0.25



# TODO,use gamma, multiple evaluations and iterations ,
# also take into consideration the transfer_cost and the transfer_limit
def policy_iteration_car_rental(environment_parameters:EnvParams, policy_parameters:PolicyParams, verbosity:int):

    # Initialization
    location_sizes=environment_parameters.location_sizes
    location_return_rates = environment_parameters.location_return_rates
    location_request_rates = environment_parameters.location_request_rates
    transfer_cost=environment_parameters.transfer_cost
    transfer_limit=environment_parameters.transfer_limit
    rental_reward = environment_parameters.rental_reward

    gamma = policy_parameters.gamma
    evaluations_number=policy_parameters.evaluations_number
    iterations_number=policy_parameters.iterations_number
    initial_policy = policy_parameters.initial_policy

    policy = initial_policy * np.ones([location_sizes[0]+1,location_sizes[1]+1],dtype='int')
    old_values = np.zeros([location_sizes[0]+1,location_sizes[1]+1])

    # FIRST PARKING LOT
    # =================
    # we compute probability that we go from m cars to n cars, measured at ENDS of days, in first parking lot,
    # if there is no transfer. This is related to Skellam's distribution.
    transition_probs1=np.zeros([location_sizes[0]+1,location_sizes[0]+1])
    expected_rewards_terms1=np.zeros([location_sizes[0]+1,location_sizes[0]+1])
    for m in range(location_sizes[0]+1):
        for n in range(location_sizes[0]+1):
            # we calculate probability we go from m cars to n cars
            for returns in range(location_sizes[0]-m+1):
                # prob1 is probability we go from m cars to m+returns in the morning
                if returns==location_sizes[0]-m:
                    prob1=1-scipy.stats.poisson.cdf(returns-1, location_return_rates[0])
                else:
                    prob1=scipy.stats.poisson.pmf(returns, location_return_rates[0])
                if n >0:
                    prob2=scipy.stats.poisson.pmf(m+returns-n,location_request_rates[0])
                else:
                    prob2=1-scipy.stats.poisson.cdf(m+returns-1,location_request_rates[0])

                pr=prob1*prob2
                # print(m,n,returns,prob1,prob2)
                # time.sleep(1)
                transition_probs1[m,n]+=pr
                expected_rewards_terms1[m,n]+=pr*rental_reward*(m+returns-n)
    # we calculate expected rewards from state m
    expected_rewards1=np.sum(expected_rewards_terms1,axis=1)

    if verbosity==2:
        print('Transition probabilities for first location:')
        print(transition_probs1)
        print('Check:')
        print(np.sum(transition_probs1,1))
        print('Expected rewards terms for first location:')
        print(expected_rewards_terms1)
        print('Expected rewards for each state for first location')
        print(expected_rewards1)

    # SECOND PARKING LOT
    # we compute probability that we go from m cars to n cars, measured at ENDS of days, in second parking lot,
    # if there is no transfer. This is related to Skellam's distribution
    transition_probs2=np.zeros([location_sizes[1]+1,location_sizes[1]+1])
    expected_reward_terms2=np.zeros([location_sizes[1]+1,location_sizes[1]+1])
    for m in range(location_sizes[1]+1):
        for n in range(location_sizes[1]+1):
            # we calculate probability we go from m cars to n cars
            for returns in range(location_sizes[1]-m+1):
                # prob1 is probability we go from m cars to m+returns to returns in the morning
                if returns==location_sizes[1]-m:
                    prob1=1-scipy.stats.poisson.cdf(returns-1, location_return_rates[1])
                else:
                    prob1=scipy.stats.poisson.pmf(returns, location_return_rates[1])
                if n >0:
                    prob2=scipy.stats.poisson.pmf(m+returns-n,location_request_rates[1])
                else:
                    prob2=1-scipy.stats.poisson.cdf(m+returns-1,location_request_rates[1])

                pr=prob1*prob2
                transition_probs2[m,n]+=pr
                expected_reward_terms2[m,n]+=pr*rental_reward*(m+returns-n)
                #print(m,n,returns,prob1,prob2,pr,pr*rental_reward*(m+returns-n))
                #time.sleep(1)
    # we calculate expected rewards from state m
    expected_rewards2 = np.sum(expected_reward_terms2, axis=1)

    if verbosity==2:
        print('Transition probabilities for second location:')
        print(transition_probs2)
        print('Check:')
        print(np.sum(transition_probs2,1))
        print('Expected rewards for second location:')
        print(expected_reward_terms2)
        print('Expected rewards for each state for second location')
        print(expected_rewards2)
    return transition_probs1,expected_rewards1,transition_probs2,expected_rewards2

policy = PolicyParams()
env = EnvParams()
verbosity = 3
policy_iteration_car_rental(env,policy,2)

## We gotta implement the Policy Iteration Algorithm
