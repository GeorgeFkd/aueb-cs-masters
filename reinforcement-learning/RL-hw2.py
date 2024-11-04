import numpy as np
from scipy.linalg import solve
import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

# Example 3.8: Gridworld Figure 3.5a uses a rectangular grid to illustrate
# value functions for a simple finite MDP. The cells of the grid correspond to
# the states of the environment. At each cell, four actions are possible: north,
# south, east, and west, which deterministically cause the agent to move one
# cell in the respective direction on the grid. Actions that would take the agent
# off the grid leave its location unchanged, but also result in a reward of −1.
# Other actions result in a reward of 0, except those that move the agent out
# of the special states A and B. From state A, all four actions yield a reward of
# +10 and take the agent to A0 . From state B, all actions yield a reward of +5
# and take the agent to B0.
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

class EnvParams:
    gamma = 0.9
    grid_width = 5
    grid_height = 5
    # [ (from,to)
    teleports = [
        (GridPoint(1,0),GridPoint(1,4)), # A->A`
        (GridPoint(3,0),GridPoint(3,2)) # B->B1
    ]
    reward = 0
    # for when it gets outside the grid-world
    punishment = -1
    # [(point,reward)]
    special_points = [
        (GridPoint(1,0),10), # A gives 10 points
        (GridPoint(3,0),5) # B gives 5 points
    ]
    # an array of probabilities for north east south west
    random_walk_distribution = [0.25,0.25,0.25,0.25]





class GridWorld:
    _params:EnvParams = None
    def __init__(self,env_params):
        self._params = env_params
    def position_is_out_of_limit(self,point:GridPoint):
        return (point.x >= self._params.grid_width or
                point.y >= self._params.grid_height or
                point.x < 0 or point.y < 0)
    def reward_of_position(self,point:GridPoint):
        if self.position_is_out_of_limit(point):
            return self._params.punishment
        for extra_reward_points in self._params.special_points:
            if extra_reward_points[0] == point:
                return extra_reward_points[1]
        return 0
    def next_state_from_with_step(self,point:GridPoint,direction:str):
        # All actions when you are in a teleport point get you to the same place
        # which is the destination of the teleport
        for teleport_point in self._params.teleports:
            if point == teleport_point[0]:
                return teleport_point[1],False
        if self.position_is_out_of_limit(point.to_direction(direction)):
            # stay in the same position and apply punishment
            return point,True
        return point.to_direction(direction),False



class GridWorldSolver:
    # basically calculates the rewards for each position on the board
    # by writing out the sets of equations required
    _grid = None
    _params:EnvParams = None
    def __init__(self,env_params):
        self._params = env_params
        self._grid = GridWorld(env_params)
    def get_equation_terms_of_direction(self, g:GridPoint, direction:str, pr_result):
        result_next, result_punish = self._grid.next_state_from_with_step(g, direction)
        current_reward =  self._params.punishment if result_punish else self._grid.reward_of_position(g)
        current_b = pr_result * current_reward #* self._params.gamma
        current_a = pr_result * self._params.gamma
        return current_b, current_a, (result_next.x, result_next.y)

    def get_current_equation_str(self,g:GridPoint, direction:str,pr_result):
        result_next, result_punish = self._grid.next_state_from_with_step(g, direction)
        result = f"{pr_result}*({self._params.gamma}*{result_next} + "
        if result_punish:
            result += f"{self._params.punishment + self._grid.reward_of_position(g)}))"
        else:
            result += f"{self._grid.reward_of_position(g)}))"
        return result
    def write_equations(self):
        pr_north = self._params.random_walk_distribution[0]
        pr_east = self._params.random_walk_distribution[1]
        pr_south = self._params.random_walk_distribution[2]
        pr_west = self._params.random_walk_distribution[3]
        nx,ny = self._params.grid_width,self._params.grid_height
        b = np.zeros(nx*ny,dtype=float)
        a = np.zeros((nx*ny,nx*ny),dtype=float)
        # print("\t\t\t\tNorth\t\t\t\tEast\t\t\t\tSouth\t\t\t\tWest")
        for x in range(nx):
            for y in range(ny):
                current_point = GridPoint(x,y)
                b_north,a_north,a_north_pos = self.get_equation_terms_of_direction(current_point,Direction.NORTH,pr_north)
                b_east,a_east,a_east_pos = self.get_equation_terms_of_direction(current_point,Direction.EAST,pr_east)
                b_west,a_west,a_west_pos = self.get_equation_terms_of_direction(current_point,Direction.WEST,pr_west)
                b_south,a_south,a_south_pos = self.get_equation_terms_of_direction(current_point,Direction.SOUTH,pr_south)
                equation_index = x + y * nx

                # x12 = x[1+2*5] = x[11] in a x[25] array
                b[equation_index] = b_north + b_east + b_west + b_south
                a[equation_index,a_north_pos[0] + a_north_pos[1] * nx] += a_north
                a[equation_index,a_east_pos[0] + a_east_pos[1] * nx] += a_east
                a[equation_index,a_south_pos[0] + a_south_pos[1] * nx] += a_south
                a[equation_index,a_west_pos[0] + a_west_pos[1] * nx] += a_west

                #for visuals
                # print(str(current_point) + f"={self.get_current_equation_str(current_point,Direction.NORTH,pr_north)} + "
                #                            f"{self.get_current_equation_str(current_point,Direction.EAST,pr_east)} + "
                #                            f"{self.get_current_equation_str(current_point,Direction.SOUTH,pr_south)} + "
                #                            f"{self.get_current_equation_str(current_point,Direction.WEST,pr_west)}"
                #       )

        return a,b
grid_solver = GridWorldSolver(EnvParams())
A,B = grid_solver.write_equations()
print("b=",B.reshape((5,5)))
I = np.eye(25)
# print("A=",A)
v = np.linalg.solve(I-A,B)
vreshaped = np.round(v.reshape(5,5),1)
print("Value function (v):")
print(vreshaped)

# correct_result = np.array([
#     [3.3, 8.8, 4.4, 5.3, 1.5],
#     [1.5, 3.0, 2.3, 1.9, 0.5],
#     [0.1, 0.7, 0.7, 0.4, -0.4],
#     [-1.0, -0.4, -0.4, -0.6, -1.2],
#     [-1.9, -1.3, -1.2, -1.4, -2.0]
# ])
#
# deviation = vreshaped - correct_result
# print("Per element Distance from textbook result",deviation)






