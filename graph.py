import numpy as np
import matplotlib.pyplot as plt
 
# Define the symmetric matrix A
A = np.array([
    [4, 1, 0, 2],
    [1, 3, 1, 0],
    [0, 1, 2, 1],
    [2, 0, 1, 5]
])
 
# Exact eigenvalues (sorted)
exact_eigs = np.sort(np.linalg.eigvalsh(A))
 
def lanczos_eigen_history(A, max_iter):
    """Perform Lanczos iteration and track eigenvalue estimates at each step"""
    n = A.shape[0]
    V = np.zeros((n, max_iter+1))  # Orthonormal basis
    T = np.zeros((max_iter, max_iter))  # Tridiagonal matrix
    eig_history = []
    
    # Initialize with random vector
    v = np.random.rand(n)
    V[:, 0] = v / np.linalg.norm(v)
    
    for j in range(max_iter):
        # Lanczos iteration
        w = A @ V[:, j]
        alpha = V[:, j] @ w
        T[j, j] = alpha
        w = w - alpha * V[:, j]
        
        if j > 0:
            w = w - T[j-1, j] * V[:, j-1]
        
        if j < max_iter-1:
            beta = np.linalg.norm(w)
            T[j, j+1] = T[j+1, j] = beta
            V[:, j+1] = w / beta
        
        # Store eigenvalues of current T matrix
        if j >= 1:  # Only start storing after 2nd iteration
            current_eigs = np.linalg.eigvalsh(T[:j+1, :j+1])
            eig_history.append(np.sort(current_eigs))
    
    return eig_history
 
# Run Lanczos for 4 iterations (full convergence for 4x4 matrix)
max_iter = 4
eig_history = lanczos_eigen_history(A, max_iter)
 
# Prepare data for plotting
iterations = range(2, max_iter+1)  # Eigenvalue estimates start at iteration 2
colors = plt.cm.rainbow(np.linspace(0, 1, 4))  # Different color for each eigenvalue
 
plt.figure(figsize=(10, 6))
 
# Plot each eigenvalue's convergence
for i in range(4):
    # Extract ith eigenvalue across iterations
    eigs_i = [eigs[i] if len(eigs) > i else np.nan for eigs in eig_history]
    plt.plot(iterations, eigs_i, 'o-', color=colors[i],
             label=f'λ_{i+1} estimate', linewidth=2)
    
    # Plot exact eigenvalue as horizontal line
    plt.axhline(y=exact_eigs[i], color=colors[i], linestyle='--',
                alpha=0.7, label=f'Exact λ_{i+1} = {exact_eigs[i]:.4f}')
 
plt.xlabel('Lanczos Iteration', fontsize=12)
plt.ylabel('Eigenvalue Estimate', fontsize=12)
plt.title('Lanczos Eigenvalue Convergence (4×4 Matrix)', fontsize=14)
plt.xticks(iterations)
plt.grid(True, alpha=0.3)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()