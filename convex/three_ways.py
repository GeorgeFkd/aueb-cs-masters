import cvxpy as cp
import numpy as np
from scipy.io import loadmat
import matplotlib.pyplot as plt

# Load data from sep3way_data.mat
data = loadmat("sep3way_data.mat")
X = data["X"]  # shape (n, N)
Y = data["Y"]  # shape (n, M)
Z = data["Z"]  # shape (n, P)

n, N = X.shape
_, M = Y.shape
_, P = Z.shape

# Define variables
a1 = cp.Variable(n)
a2 = cp.Variable(n)
a3 = cp.Variable(n)
b1 = cp.Variable()
b2 = cp.Variable()
b3 = cp.Variable()

# Define constraints
constraints = []

for j in range(N):
    xj = X[:, j]
    constraints += [
        a1 @ xj - b1 >= a2 @ xj - b2 + 1,
        a1 @ xj - b1 >= a3 @ xj - b3 + 1,
    ]

for j in range(M):
    yj = Y[:, j]
    constraints += [
        a2 @ yj - b2 >= a1 @ yj - b1 + 1,
        a2 @ yj - b2 >= a3 @ yj - b3 + 1,
    ]

for j in range(P):
    zj = Z[:, j]
    constraints += [
        a3 @ zj - b3 >= a1 @ zj - b1 + 1,
        a3 @ zj - b3 >= a2 @ zj - b2 + 1,
    ]

# Objective: minimize the sum of squared norms
objective = cp.Minimize(cp.sum_squares(a1) + cp.sum_squares(a2) + cp.sum_squares(a3))

# Solve the problem
problem = cp.Problem(objective, constraints)
problem.solve()

# Output results
print("Optimal objective value:", problem.value)
print("a1:", a1.value)
print("a2:", a2.value)
print("a3:", a3.value)
print("b1:", b1.value)
print("b2:", b2.value)
print("b3:", b3.value)

# Optional: plot (requires sep3way_data.m plotting code to be replicated)

a1, a2, a3 = a1.value, a2.value, a3.value
b1, b2, b3 = b1.value, b2.value, b3.value

# Compute decision boundaries
t = np.linspace(-7, 7, 1000)

def line_from_normals(a_i, a_j, b_i, b_j, t):
    u = a_i - a_j
    v = b_i - b_j
    line = (-t * u[0] + v) / u[1]
    return line, u, v

line1, u1, v1 = line_from_normals(a1, a2, b1, b2, t)
line2, u2, v2 = line_from_normals(a2, a3, b2, b3, t)
line3, u3, v3 = line_from_normals(a3, a1, b3, b1, t)

# Masks for correct halfspaces
def region_mask(u, v, t, line):
    return u @ np.vstack([t, line]) - v > 0

idx1 = region_mask(u2, v2, t, line1)
idx2 = region_mask(u3, v3, t, line2)
idx3 = region_mask(u1, v1, t, line3)

# Plotting
plt.figure(figsize=(8, 8))
plt.plot(X[0], X[1], '*', label="Class 1 (X)")
plt.plot(Y[0], Y[1], 'ro', label="Class 2 (Y)")
plt.plot(Z[0], Z[1], 'g+', label="Class 3 (Z)")
plt.plot(t[idx1], line1[idx1], 'k')
plt.plot(t[idx2], line2[idx2], 'k')
plt.plot(t[idx3], line3[idx3], 'k')
plt.axis([-7, 7, -7, 7])
plt.legend()
plt.title("3-Way Linear Classification")
plt.grid(True)
plt.show()
