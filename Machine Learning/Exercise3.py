from random import randint

def f(x):
    return x * x + 1

def df (x):
    return 2 * x

if __name__ == "__main__":
    cur_x = randint(0, 10) # Random starting value
    rate = 0.01 # Learning rate
    precision = 0.000001 # Exit condition
    previous_step_size = 1
    max_iters = 10000 # Maximum number of iterations
    iters = 0 # Iteration counter
    while previous_step_size > precision and iters < max_iters:
        prev_x = cur_x # Store current x value in prev_x
        cur_x = cur_x - rate * df(prev_x) # Grad descent
        previous_step_size = abs(cur_x - prev_x) # Change in x
        iters = iters + 1 # Iteration counter
        print (f"Iteration: {iters} \nX value is {cur_x}")
    print (f"The local minimum is x = {cur_x} and y = {f(cur_x)}") 