import numpy as np
import logging
import matplotlib.pyplot as plt
class Direction:
    WEST = "west"
    NORTH = "north"
    EAST = "east"
    SOUTH = "south"

class GridPoint:
    x = -1
    y = -1

    # (0,0)            (m-1,0)
    #         (k,l-1)
    #  (k-1,l) (k,l) (k+1,l)
    #         (k,l+1)
    # (0,n-1)           (m-1,n-1)
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # to be able to calculate when it gets out of the grid
    def __add__(self, other):
        return GridPoint(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"x{self.x}{self.y}"

    def south(self):
        return GridPoint(self.x, self.y + 1)

    def north(self):
        return GridPoint(self.x, self.y - 1)

    def east(self):
        return GridPoint(self.x + 1, self.y)

    def west(self):
        return GridPoint(self.x - 1, self.y)

    def to_direction(self, direct: str):
        if direct == Direction.NORTH:
            return self.north()
        if direct == Direction.SOUTH:
            return self.south()
        if direct == Direction.EAST:
            return self.east()
        if direct == Direction.WEST:
            return self.west()
class EnvParams:
    gamma = 0.9
    starting_tile = GridPoint(0, 0)
    grid_width = 12
    grid_height = 4
    wind_up_offset = np.zeros((grid_width,1))
    wind_right_offset = np.zeros((grid_height,1))
    target = GridPoint(7,3)
    tiles_rewards = []
    cliff = [GridPoint(1,0),GridPoint(2,0),GridPoint(3,0),GridPoint(4,0)
            ,GridPoint(5,0),GridPoint(6,0),GridPoint(7,0),GridPoint(8,0)
            ,GridPoint(9,0),GridPoint(10,0)]
    reward = -1
    # for when it gets outside the grid-world
    punishment = -100
    def __init__(self,target:GridPoint,wind_up:list[int],grid_shape:tuple[int,int]):
        self.target = target
        self.wind_up_offset = np.array(wind_up)
        self.wind_right_offset = np.zeros((grid_shape[1],1))
        self.tiles_rewards = np.zeros(grid_shape)
        self.tiles_rewards[::] = -1
        self.tiles_rewards[target.x,target.y] = 0
        self.grid_width,self.grid_height = grid_shape

class GridWorld:
    _params:EnvParams = None
    def __init__(self,env_params):
        self._params = env_params
    def position_is_out_of_limit(self,point:GridPoint):
        return (point.x >= self._params.grid_width or
                point.y >= self._params.grid_height or
                point.x < 0 or point.y < 0)
    def reward_of_position(self,point:GridPoint):
        # constant rewards
        # of -1 until the goal state is reached.
        if point == self._params.target:
            return 0
        elif point in self._params.cliff:
            return -100
        else:
            return -1
    def next_state_from_with_step(self, state:GridPoint, action:str):

        next_point = state.to_direction(action)
        if self.position_is_out_of_limit(next_point):
            return state,False
        prev_point = next_point
        next_point = self.apply_wind(next_point)
        if self.position_is_out_of_limit(next_point):
            return prev_point,False

        if next_point == self._params.target:
            # if it is the target, return true to signal the episode is over.
            return self._params.target,True
        return next_point,False
    def apply_wind(self,point:GridPoint):
        return point



class PolicyParams:
    epsilon = 0.1
    type = "sarsa" # or expected-sarsa, or Q-Learning
    alpha = 0.5
    gamma = 0.9

class SimulationParams:
    starting_tile = GridPoint(0,0)
    # width,height,3 -> 0-> Left,1->Right,2->Up,3->Down
    simulated_episodes = 50
    max_episode_length = 30
    seed = 5
    debug = True

    def __init__(self,start:GridPoint,simulated_eps, max_ep_length,seed):
        self.starting_tile = start
        self.simulated_episodes = simulated_eps
        self.max_episode_length = max_ep_length
        self.seed = seed

def print_action(a):
    if a == 0:
        print("Left")
    elif a == 1:
        print("Right")
    elif a == 2:
        print("Up")
    elif a == 3:
        print("Down")

def get_action_eps_greedy(policy_settings:PolicyParams, state:GridPoint, Q_s_a):
    # for greedy, just take the argmin from the Q_s_a in the 3rd axis
    # for ε-greedy with probability ε pick a random one
    if np.random.uniform(0,1) <= policy_settings.epsilon:
        return np.random.choice([0,1,2,3])
    actions_from_state = Q_s_a[state.x,state.y]
    return np.argmax(actions_from_state)

def calc_update_using_policy_probs_and_Q(policy_settings:PolicyParams, s_prime:GridPoint, Q_s_a):
    greedy_option = np.argmax(Q_s_a[s_prime.x,s_prime.y])
    non_greedy_options = [i for i in range(4)]
    non_greedy_options.remove(greedy_option)
    greedy_option_prob = 1 - policy_settings.epsilon + policy_settings.epsilon * 0.25
    non_greedy_option_prob = policy_settings.epsilon * 0.25
    total = 0
    for i in range(4):
        if i == greedy_option:
            total = total + greedy_option_prob * Q_s_a[s_prime.x,s_prime.y,greedy_option]
        else:
            total = total + non_greedy_option_prob * Q_s_a[s_prime.x,s_prime.y,i]
    return total

def direction(action):
    if action == 0:
        return Direction.WEST
    elif action == 1:
        return Direction.EAST
    elif action == 2:
        return Direction.NORTH
    elif action == 3:
        return Direction.SOUTH

class AverageRewardAndAlphaMetric:
    alphas = []
    average_rewards = []
    methods_used = []
    def observe(self,avg_reward,al,from_method):
        self.alphas.append(al)
        self.average_rewards.append(avg_reward)
        self.methods_used.append(from_method)
    def plot(self):
        # plt.plot(self.alphas, self.average_rewards, color="blue", linewidth=0.8)
        unique_categories = ["sarsa","expected-sarsa","Q-learning"]
        # Labels and title
        plt.figure(figsize=(8,6))
        colors = ['b', 'r', 'g', 'c', 'm', 'y']  # Define colors (extend as needed)
        category_color_map = {cat: colors[i % len(colors)] for i, cat in enumerate(unique_categories)}
        for algo in unique_categories:
            x_algo = [self.alphas[i] for i in range(len(self.alphas)) if self.methods_used[i] == algo]
            y_algo = [self.average_rewards[i] for i in range(len(self.average_rewards)) if self.methods_used[i] == algo]
            plt.plot(x_algo, y_algo, marker='o', label=algo, color=category_color_map[algo])
        plt.xlabel("alpha")
        plt.ylabel("Average sum of rewards per episode")
        plt.title("Performance")
        plt.legend()

        # Show plot
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("Cliff World with all methods-avg-reward-alpha.pdf",format="pdf")
        plt.show()


def print_grid_values(Q):
    for x in range(Q.shape[0]):
        for y in range(Q.shape[1]):
            print(f"{x},{y} LEFT: {Q[x,y,0]}, RIGHT: {Q[x,y,1]}, UP {Q[x,y,2]}, DOWN {Q[x,y,3]}")



class RewardsPerEpisodeMetric:
    episodes = []
    rewards = []
    methods_used = []
    def observe(self,r,episode,from_method):

        self.episodes.append(episode)
        self.rewards.append(r)
        self.methods_used.append(from_method)
    def plot(self):
        # plt.plot(self.episodes, self.average_rewards, color="blue", linewidth=0.8)
        unique_categories = ["sarsa","expected-sarsa","Q-learning"]
        # Labels and title
        plt.figure(figsize=(8,6))
        colors = ['b', 'r', 'g', 'c', 'm', 'y']  # Define colors (extend as needed)
        category_color_map = {cat: colors[i % len(colors)] for i, cat in enumerate(unique_categories)}
        for algo in unique_categories:
            x_algo = [self.episodes[i] for i in range(len(self.episodes)) if self.methods_used[i] == algo]
            y_algo = [self.rewards[i] for i in range(len(self.rewards)) if self.methods_used[i] == algo]
            plt.plot(x_algo, y_algo, marker='o', label=algo, color=category_color_map[algo])
        plt.xlabel("Episodes")
        plt.ylabel("Sum of rewards during episode")
        plt.title("Performance")
        plt.legend()

        # Show plot
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("Cliff World with all methods-rewards-per-episode.pdf",format="pdf")
        plt.show()

def run_simulation(env:EnvParams,policy:PolicyParams,simulation:SimulationParams,stats:AverageRewardAndAlphaMetric,chart2:RewardsPerEpisodeMetric):
    grid = GridWorld(env)
    Q = np.zeros((grid._params.grid_width,grid._params.grid_height,4))
    alpha = policy.alpha
    gamma = policy.gamma
    for episode in range(simulation.simulated_episodes):
        S = simulation.starting_tile
        A = get_action_eps_greedy(policy,S,Q)
        is_terminal = False
        timesteps = 0
        rewards = 0
        while not is_terminal:
            S_prime, is_terminal = grid.next_state_from_with_step(S, direction(A))
            R = grid.reward_of_position(S_prime)
            A_prime = get_action_eps_greedy(policy,S_prime,Q)
            # Q-Learning
            if "q" in policy.type.lower():
                Q[S.x, S.y, A] = Q[S.x, S.y, A] + alpha * (
                            R + gamma * np.max(Q[S_prime.x, S_prime.y]) - Q[S.x, S.y, A])
            # Expected Sarsa
            elif "expected" in policy.type.lower():
                weighted_sum_of_actions_based_on_policy = calc_update_using_policy_probs_and_Q(policy,S_prime,Q)
                Q[S.x,S.y,A] = Q[S.x,S.y,A] + alpha * (R + gamma * weighted_sum_of_actions_based_on_policy - Q[S.x,S.y,A])
            # simple Sarsa
            else:
                Q[S.x, S.y, A] = Q[S.x, S.y, A] + alpha * (
                            R + gamma * Q[S_prime.x, S_prime.y, A_prime] - Q[S.x, S.y, A])
            S = S_prime
            A = A_prime
            timesteps += 1
            rewards += R
            if timesteps > simulation.max_episode_length or R == -100:
                is_terminal = True
        print(f"{policy.type} in episode {episode} has reached destination in ",timesteps,"steps ","with rewards: ",rewards)
        chart2.observe(rewards,episode,policy.type)
        stats.observe(float(rewards)/timesteps,alpha,policy.type)
    return stats,chart2

statistics = AverageRewardAndAlphaMetric()
perf_of_algos = RewardsPerEpisodeMetric()
for alph in [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1]:

    env = EnvParams(GridPoint(11, 0), [0, 0, 0, 1, 1, 1, 2, 2, 1, 0], (12, 4))
    p = PolicyParams()
    p.alpha = alph

    p.type = "sarsa"
    sim = SimulationParams(GridPoint(0, 3), 250, 250, 5)
    statistics,perf_of_algos = run_simulation(env, p, sim,statistics,perf_of_algos)

    p.type = "expected-sarsa"
    sim = SimulationParams(GridPoint(0, 3), 250, 250, 5)
    statistics,perf_of_algos = run_simulation(env, p, sim,statistics,perf_of_algos)

    p.type = "Q-learning"
    sim = SimulationParams(GridPoint(0, 3), 250, 250, 5)
    statistics,perf_of_algos = run_simulation(env, p, sim,statistics,perf_of_algos)

statistics.plot()
perf_of_algos.plot()
