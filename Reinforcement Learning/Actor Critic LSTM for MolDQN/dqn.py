import torch
import torch.nn as nn
import torch.nn.functional as F


class Actor(nn.Module):
    def __init__(self, input_length, output_length):
        super(Actor, self).__init__()

        self.linear_1 = nn.Linear(input_length, 1024)
        self.linear_2 = nn.Linear(1024, 512)
        self.linear_3 = nn.Linear(512, 128)
        self.lstm = nn.LSTM(128, 32)
        self.linear_4 = nn.Linear(32, output_length)

        self.activation = nn.ReLU()

    def forward(self, x, hidden):
        x = self.activation(self.linear_1(x))
        x = self.activation(self.linear_2(x))
        x = self.activation(self.linear_3(x))
        x = x.view(-1, 1, 128)
        x, lstm_hidden = self.lstm(x, hidden)
        x = self.linear_4(x)
        x = F.softmax(x, dim=2)

        return x, lstm_hidden

class Critic(nn.Module):
    def __init__(self, input_length, output_length):
        super(Critic, self).__init__()

        self.linear_1 = nn.Linear(input_length, 1024)
        self.linear_2 = nn.Linear(1024, 512)
        self.linear_3 = nn.Linear(512, 128)
        self.lstm = nn.LSTM(128, 32)
        self.linear_4 = nn.Linear(32, output_length)

        self.activation = nn.ReLU()

    def forward(self, x, hidden):
        x = self.activation(self.linear_1(x))
        x = self.activation(self.linear_2(x))
        x = self.activation(self.linear_3(x))
        x = x.view(-1, 1, 128)
        x, lstm_hidden = self.lstm(x, hidden)
        x = self.linear_4(x)

        return x

# class ActorCriticMolDQN(nn.Module):
#     def __init__(self, actor, critic):
#         super().__init__()
        
#         self.actor = actor
#         self.critic = critic
        
#     def forward(self, state, hidden):
        
#         action_pred, lstm_hidden = self.actor(state, hidden)
#         action_prob = F.softmax(action_pred, dim=2).squeeze(1)

#         value_pred, _ = self.critic(state, hidden)
#         value_pred = value_pred.squeeze(1)
        
#         return action_prob, value_pred, lstm_hidden

