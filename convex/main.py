import cvxpy as cp
import numpy as np

# Define variables
x = cp.Variable(3)

# Define parameters for the problem
P = np.array([[-3, 0, 0],
              [0, 1, 0],
              [0, 0, 2]])
q = np.array([2, 2, 2])

# Define problem
objective = cp.Minimize(0.5 * cp.quad_form(x, P) + q.T @ x)
constraints = [cp.sum_squares(x) == 1]
problem = cp.Problem(objective, constraints)

# Solve the problem
problem.solve()

# Print solution
print("Optimal value:", problem.value)
print("Optimal x:", x.value)

# Check KKT conditions
if problem.status == 'optimal':
    # Stationarity condition: ∇f(x) + λ∇h(x) = 0
    # Where h(x) = x₁² + x₂² + x₃² - 1 = 0
    
    # Compute gradient of objective at solution
    grad_f = P @ x.value + q
    
    # Compute gradient of constraint at solution
    grad_h = 2 * x.value
    
    # Solve for Lagrange multiplier λ
    # From stationarity: grad_f + λ*grad_h = 0
    # We can solve this least-squares problem
    A = grad_h.reshape(-1, 1)  # reshape to column vector
    lambd = -np.linalg.lstsq(A, grad_f, rcond=None)[0][0]
    
    print("\nKKT conditions check:")
    print(f"Lagrange multiplier (λ): {lambd}")
    
    # Check stationarity
    stationarity_residual = np.linalg.norm(grad_f + lambd * grad_h)
    print(f"Stationarity residual (should be near 0): {stationarity_residual:.4e}")
    
    # Primal feasibility (constraint satisfaction)
    primal_feasibility = np.abs(np.sum(x.value**2) - 1)
    print(f"Primal feasibility (should be near 0): {primal_feasibility:.4e}")
    
    # Dual feasibility (no inequality constraints in this problem)
    print("Dual feasibility: N/A (no inequality constraints)")
    
    # Complementary slackness (no inequality constraints in this problem)
    print("Complementary slackness: N/A (no inequality constraints)")
else:
    print("Problem could not be solved to optimality.")



