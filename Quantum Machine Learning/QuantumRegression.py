# This program is based on the variational classifier used in https://pennylane.ai/qml/demos/tutorial_variational_classifier.html
# This code is modified to be able to predict a sin function

import pennylane as qml
from pennylane import numpy as np
from pennylane.optimize import NesterovMomentumOptimizer
import matplotlib.pyplot as plt
from math import sin

dev = qml.device("default.qubit", wires=1)

def square_loss(labels, predictions):
    loss = 0
    for l, p in zip(labels, predictions):
        loss = loss + (l - p) ** 2     
    loss = loss / len(labels)
    return loss

def accuracy(labels, predictions):
    loss = 0
    for l, p in zip(labels, predictions):
        if abs(l - p) < 1e-5:
            loss = loss + 1
    loss = loss / len(labels)
    return loss

def statepreparation(a):
    qml.RY(a, wires=0)

def layer(W):
    qml.Rot(W[0, 0], W[0, 1], W[0, 2], wires=0)

@qml.qnode(dev)
def circuit(weights, angles=None):
    statepreparation(angles)
    for W in weights:
        layer(W)
    return qml.expval(qml.PauliZ(0))

def regressor(reg, angles=None):
    weights = reg[0]
    bias = reg[1]
    return circuit(weights, angles=angles) + bias

def cost(weights, features, labels):
    predictions = [circuit(weights[0], angles=f) for f in features]
    return square_loss(labels, predictions)

# data
data = np.loadtxt("sin_data.txt")
X = data[:, -2]
features = np.array([x for x in X]) # Redundant
Y = data[:, -1]

np.random.seed(0)
num_data = len(Y)
num_train = int(0.75 * num_data)
index = np.random.permutation(range(num_data))
feats_train = features[index[:num_train]]
Y_train = Y[index[:num_train]]

num_qubits = 1
num_layers = 6
reg_init = (0.01 * np.random.randn(num_layers, num_qubits, 3), 0.0)

opt = NesterovMomentumOptimizer(0.01)
batch_size = 5

# train the regressor
reg = reg_init
for it in range(100):

    # Update the weights by one optimizer step
    batch_index = np.random.randint(0, num_train, (batch_size,))
    feats_train_batch = feats_train[batch_index]
    Y_train_batch = Y_train[batch_index]
    reg = opt.step(lambda v: cost(v, feats_train_batch, Y_train_batch), reg)

    print(
        "Iter: {:5d} | Cost: {:0.7f}"
        "".format(it + 1, cost(reg, features, Y))
    )

plot_predictions = [regressor(reg, angles= (f / 10)) for f in range(0, 63, 1)]
plot_actual = [sin(x / 10) for x in range(0, 63, 1)]
plt.plot(plot_actual, "r")
plt.plot(plot_predictions, "b")
plt.show()
