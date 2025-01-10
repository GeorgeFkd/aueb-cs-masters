import numpy as np
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
    #(0,n-1)           (m-1,n-1)
    def __init__(self, x, y):
        self.x = x
        self.y = y
    # to be able to calculate when it gets out of the grid
    def __add__(self,other):
        return GridPoint(self.x + other.x, self.y + other.y)
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __str__(self):
        return f"x{self.x}{self.y}"
    def south(self):
        return GridPoint(self.x,self.y+1)
    def north(self):
        return GridPoint(self.x,self.y-1)
    def east(self):
        return GridPoint(self.x+1,self.y)
    def west(self):
        return GridPoint(self.x-1,self.y)
    def to_direction(self,direct:str):
        if direct == Direction.NORTH:
            return self.north()
        if direct == Direction.SOUTH:
            return self.south()
        if direct == Direction.EAST:
            return self.east()
        if direct == Direction.WEST:
            return self.west()
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
        return -1
    def next_state_from_with_step(self,point:GridPoint,direction:str):
        # this logic might be incorrect
        next_point = point.to_direction(direction)
        if self.position_is_out_of_limit(next_point):
            return point
        prev_point = next_point
        next_point = self.apply_wind(next_point)
        if self.position_is_out_of_limit(next_point):
            return prev_point


        if next_point == self._params.target:
            return self._params.target,True
        # if it is the target, return true to signal the episode is over.
        return point.to_direction(direction),False
    def apply_wind(self,point:GridPoint):
        return point + GridPoint(self._params.wind_right_offset[point.x],self._params.wind_up_offset[point.y])

class EnvParams:
    gamma = 0.9
    grid_width = 5
    grid_height = 5
    wind_up_offset = np.array((grid_width, 1))
    wind_right_offset = np.array((grid_height, 1))
    target = GridPoint(7,3)
    tiles_rewards = np.array((grid_width, grid_height))
    reward = -1
    # for when it gets outside the grid-world
    punishment = -1
    # [(point,reward)]
    special_points = [
        (GridPoint(1,0),10), # A gives 10 points
        (GridPoint(3,0),5) # B gives 5 points
    ]
    # an array of probabilities for north east south west
    random_walk_distribution = [0.25,0.25,0.25,0.25]

class PolicyParams:
    epsilon = 0.1
    alpha = 0.5
    gamma = 0.9

class SimulationParams:
    starting_tile = GridPoint(1,1)
    # width,height,3 -> 0-> Left,1->Right,2->Up,3->Down
    initial_q = np.array()
    initial_q.fill(0)
    simulated_episodes = 50
    max_episode_length = 30
    seed = 5
    debug = True
    def init_Q(self,width,height):
        self.initial_q = np.array((width,height,3))
        self.initial_q.fill(0)
        return self.initial_q.copy()


def get_action_from_q(policy_settings:PolicyParams,state,Q_s_a):
    # for greedy, just take the argmin from the Q_s_a in the 3rd axis
    # for ε-greedy with probability ε pick a random one
    pass
def run_simulation(env:EnvParams,policy:PolicyParams,simulation:SimulationParams):
    grid = GridWorld(env)
    Q = simulation.init_Q(env.grid_width,env.grid_height)
    # the only thing I don't have already is
    # S is a x,y -> not a grid point unfortunately
    for episode in range(simulation.simulated_episodes):
        # Initialise S -> S = simulation.starting_tile.x,simulation.starting_tile.y
        # Choose A from S using policy from Q, do not take the action yet so it is in the loop
        # For each step of episode:
        # Take action A, observe R_t+1, S'
        # Choose A' from S' using policy from Q
        # Q[S,A] = Q[S,A] + policy.alpha * (R_t+1 + env.gamma * Q[S',A'] - Q[S,A])
        # move the plot forward
        # S = S'
        # A = A'
        # until S is terminal
        pass


