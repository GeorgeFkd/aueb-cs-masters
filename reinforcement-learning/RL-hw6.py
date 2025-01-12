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
    grid_width = 5
    grid_height = 5
    wind_up_offset = np.zeros((grid_width,1))
    wind_right_offset = np.zeros((grid_height,1))
    target = GridPoint(7,3)
    tiles_rewards = []
    reward = -1
    # for when it gets outside the grid-world
    punishment = -1
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
        else:
            return -1
    def next_state_from_with_step(self, state:GridPoint, action:str):
        # this logic might be incorrect
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
        return point + GridPoint(0,self._params.wind_up_offset[point.x])



class PolicyParams:
    epsilon = 0.2
    alpha = 0.5
    gamma = 0.9

class SimulationParams:
    starting_tile = GridPoint(0,3)
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

def get_action_from_q(policy_settings:PolicyParams,state:GridPoint,Q_s_a):
    # for greedy, just take the argmin from the Q_s_a in the 3rd axis
    # for ε-greedy with probability ε pick a random one
    if np.random.uniform(0,1) <= policy_settings.epsilon:
        return np.random.choice([0,1,2,3])
    actions_from_state = Q_s_a[state.x,state.y]
    return np.argmax(actions_from_state)

def direction(action):
    if action == 0:
        return Direction.WEST
    elif action == 1:
        return Direction.EAST
    elif action == 2:
        return Direction.NORTH
    elif action == 3:
        return Direction.SOUTH

class EpisodeDurationOverTimeMetric:
    episode = []
    timesteps = []
    def observe(self,timesteps,episode_no):
        self.episode.append(episode_no)
        self.timesteps.append(timesteps)
    def plot(self):
        max_duration = max(self.timesteps)
        min_duration = min(self.timesteps)
        plt.figure(figsize=(10, 6))
        plt.plot(self.episode, self.timesteps, label="Episode Duration", color="blue", linewidth=0.8)

        # Add max and min lines
        plt.axhline(y=max_duration, color='red', linestyle='--', label="Max Duration")
        plt.axhline(y=min_duration, color='green', linestyle='--', label="Min Duration")

        # Labels and title
        plt.xlabel("Episodes")
        plt.ylabel("Episode Duration")
        plt.title("Episode Durations Over Time")
        plt.legend()

        # Show plot
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("Windy Grid World with SARSA.pdf",format="pdf")
        plt.show()
        pass

def print_grid_values(Q):
    for x in range(Q.shape[0]):
        for y in range(Q.shape[1]):
            print(f"{x},{y} LEFT: {Q[x,y,0]}, RIGHT: {Q[x,y,1]}, UP {Q[x,y,2]}, DOWN {Q[x,y,3]}")



def run_simulation(env:EnvParams,policy:PolicyParams,simulation:SimulationParams):
    grid = GridWorld(env)
    Q = np.zeros((grid._params.grid_width,grid._params.grid_height,4))
    alpha = policy.alpha
    gamma = policy.gamma
    stats = EpisodeDurationOverTimeMetric()
    for episode in range(simulation.simulated_episodes):
        S = simulation.starting_tile
        A = get_action_from_q(policy,S,Q)
        is_terminal = False
        timesteps = 0
        while not is_terminal:
            S_prime, is_terminal = grid.next_state_from_with_step(S, direction(A))
            R = grid.reward_of_position(S_prime)
            A_prime = get_action_from_q(policy,S_prime,Q)
            print_action(A_prime)
            Q[S.x,S.y,A] = Q[S.x,S.y,A] + alpha * (R + gamma*Q[S_prime.x,S_prime.y,A_prime] - Q[S.x,S.y,A])
            S = S_prime
            A = A_prime
            timesteps += 1
            if timesteps > simulation.max_episode_length:
                is_terminal = True
        print("Reached destination in ",timesteps,"steps")
        stats.observe(timesteps,episode)

    stats.plot()

env = EnvParams(GridPoint(7,3),[0,0,0,1,1,1,2,2,1,0],(10,7))
p = PolicyParams()
sim = SimulationParams(GridPoint(0,3),250,250,5)
run_simulation(env,p,sim)

