import torch
import torch.nn as nn
import torch.nn.functional as F


class MolDQN(nn.Module):
    def __init__(self, input_length, output_length):
        super(MolDQN, self).__init__()     
        self.fc1   = nn.Linear(input_length,64)
        self.lstm  = nn.LSTM(64,32)
        self.fc_pi = nn.Linear(32,output_length)
        self.fc_v  = nn.Linear(32,1)

    def pi(self, x, hidden, softmax_dim=2):
        x = F.relu(self.fc1(x))
        x = x.view(-1, 1, 64)
        x, lstm_hidden = self.lstm(x, hidden)
        x = self.fc_pi(x)
        prob = F.softmax(x, dim=softmax_dim)
        return prob, lstm_hidden
    
    def v(self, x, hidden):
        x = F.relu(self.fc1(x))
        x = x.view(-1, 1, 64)
        x, lstm_hidden = self.lstm(x, hidden)
        v = self.fc_v(x)
        return v