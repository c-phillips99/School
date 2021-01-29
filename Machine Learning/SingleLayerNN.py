# This file impliments a single layer neural network in Pytorch

import torch
import torch.nn as nn
import matplotlib.pyplot as pyplot

x = torch.randn(100, 5) # Random input values
y = torch.randint(2, (100,)).type(torch.FloatTensor) # Random target values

input_units = 5
output_units = 1

model = nn.Sequential(nn.Linear(input_units, output_units), nn.Sigmoid())
loss_func = torch.nn.MSELoss() # Using Mean-Squared Error for regression
optimizer = torch.optim.Adam(model.parameters(), lr = 0.01)

losses = []

for t in range(0, 100):
    y_pred = model(x)
    loss = loss_func(y_pred, y)
    optimizer.zero_grad()
    loss.backward()
    losses.append(loss.item())
    optimizer.step()
    print('loss ', loss.item())
    

print ("Final weights and bias:")
print(model.state_dict())

pyplot.plot(range(0, 100), losses)
pyplot.show()
