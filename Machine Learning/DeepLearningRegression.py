import torch 
import torch.nn as nn
import pandas as pd
from sklearn.model_selection import train_test_split

## Data Prep
data = pd.read_csv("data/YearPredictionMSD.txt", header=None, nrows = 10000) # Using a subset
data.iloc[0,:]
missing_data = data.isnull().sum().sum() # Checks for missing data
outliers = {} # Catches outlier more than 3 standard deviations away from the mean
for i in range(data.shape[1]):
        min_t = data[data.columns[i]].mean() - (3 * data[data.columns[i]].std())
        max_t = data[data.columns[i]].mean() + (3 * data[data.columns[i]].std())
        count = 0
        for j in data[data.columns[i]]:
            if j < min_t or j > max_t:
                count += 1
        percentage = count / data.shape[0]
        outliers[data.columns[i]] = "%.3f" % percentage
X = data.iloc[:, 1:]
Y = data.iloc[:, 0]
X = (X - X.min()) / (X.max() - X.min()) # Normalizing the data
X_shuffle = X.sample(frac=1)
Y_shuffle = Y.sample(frac=1)
x_new, x_test, y_new, y_test = train_test_split(X_shuffle, Y_shuffle, test_size=0.2, random_state=0)
dev_per = x_test.shape[0]/x_new.shape[0]
x_train, x_dev, y_train, y_dev = train_test_split(x_new, y_new, test_size=dev_per, random_state=0)

# Training data
x_train = torch.tensor(x_train.values).float()
y_train = torch.tensor(y_train.values).float()
# Validation data
x_dev = torch.tensor(x_dev.values).float()
y_dev = torch.tensor(y_dev.values).float()
# Test data
x_test = torch.tensor(x_test.values).float()
y_test = torch.tensor(y_test.values).float()

## Building the Net
model = nn.Sequential(nn.Linear(x_train.shape[1], 100), nn.ReLU(), nn.Linear(100, 50), nn.ReLU(), nn.Linear(50, 25), nn.ReLU(), nn.Linear(25, 1))

loss_function = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

## Training the Net
for i in range(100):
    y_pred = model(x_train)
    loss = loss_function(y_pred, y_train)
    print (f"{i}, loss = {loss.item()}")
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

pred = model(x_test[0])
print ("True value:")
print (y_test[0])
print("Predicted value:")
print(pred)
