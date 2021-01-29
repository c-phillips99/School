# This file impliments the idea of cross entropy 
# Based on the psudo-code from https://en.wikipedia.org/wiki/Cross-entropy_method

import math
import numpy as np

def evaluate(x):
    return np.exp(-(x - 2)**2) + 0.8 * np.exp(-(x + 2)**2)

def xs_sort(x, s):
    # Creating the new list is not the most efficient way to do this, but I did it for simplicity
    new_x = []
    zipped = list(zip (x, s))
    sorted_zipped = sorted(zipped, key = lambda x: x[1], reverse = True)
    for elem in sorted_zipped:
        new_x.append(elem[0])
    return new_x

def run():
    mu = -6 # Mean
    epsilon = 0.01 # Learning rate
    var = 100 # Variance
    iter = 0
    maxiters = 100
    N = 100
    Ne = 10 # Only using the best 10 to update
    while t < maxiters and var > epsilon:
        x = np.random.normal(mu, var, N) # Obtain N samples from current sampling distribution
        s = evaluate(x) # Evaluate objective function at sampled points
        x = xs_sort(x, s) # Sort x by objective function values in descending order
        # Update parameters of sampling distribution                  
        mu = np.mean(x[0:Ne])
        var = np.var(x[0:Ne])
        iter += 1
        
    # Return mean of final sampling distribution as solution
    return mu

if __name__ == "__main__":
    mu = run()
    print ("True mu: 2")
    print (f"Exstimated mu: {mu}")
