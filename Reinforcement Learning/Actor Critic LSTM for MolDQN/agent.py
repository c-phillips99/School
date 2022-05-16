import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import torch.optim as opt
import utils
import hyp
from dqn import Actor, Critic
from rdkit import Chem
from rdkit.Chem import QED
from environment import Molecule
from baselines.deepq import replay_buffer

REPLAY_BUFFER_CAPACITY = hyp.replay_buffer_size


class QEDRewardMolecule(Molecule):
    """The molecule whose reward is the QED."""

    def __init__(self, discount_factor, **kwargs):
        """Initializes the class.

    Args:
      discount_factor: Float. The discount factor. We only
        care about the molecule at the end of modification.
        In order to prevent a myopic decision, we discount
        the reward at each step by a factor of
        discount_factor ** num_steps_left,
        this encourages exploration with emphasis on long term rewards.
      **kwargs: The keyword arguments passed to the base class.
    """
        super(QEDRewardMolecule, self).__init__(**kwargs)
        self.discount_factor = discount_factor

    def _reward(self):
        """Reward of a state.

    Returns:
      Float. QED of the current state.
    """
        molecule = Chem.MolFromSmiles(self._state)
        if molecule is None:
            return 0.0
        qed = QED.qed(molecule)
        return qed * self.discount_factor ** (self.max_steps - self.num_steps_taken)


class Agent(object):
    def __init__(self, input_length, output_length, device):
        self.device = device
        self.actor = Actor(input_length, output_length).to(self.device)
        self.critic = Critic(input_length, 1).to(self.device)
        # self.dqn = ActorCriticMolDQN(self.actor, self.critic)
        # self.dqn = MolDQN(input_length, output_length).to(self.device)
        # self.replay_buffer = replay_buffer.ReplayBuffer(REPLAY_BUFFER_CAPACITY)
        self.a_optimizer = getattr(opt, hyp.optimizer)(
            self.actor.parameters(), lr=hyp.learning_rate
        )
        self.c_optimizer = getattr(opt, hyp.optimizer)(
            self.critic.parameters(), lr=hyp.learning_rate
        )

    def get_action(self, observations, hidden):
        action_prob, lstm_hidden = self.actor.forward(observations.to(self.device), hidden)
        value_pred = self.critic.forward(observations.to(self.device), lstm_hidden)
        return action_prob.squeeze(1).flatten(), value_pred.squeeze(1), lstm_hidden

    def train(self, rewards, log_prob_actions, values):
        returns = calculate_returns(rewards, .99).detach()#.unsqueeze(1)
        probs = torch.stack(log_prob_actions)
        vals = torch.stack(values).squeeze(1)

        policy_loss = - (returns * probs).sum()
        self.a_optimizer.zero_grad()
        policy_loss.backward(retain_graph=True)
        self.a_optimizer.step()

        value_loss = F.smooth_l1_loss(returns, vals).sum()
        self.c_optimizer.zero_grad()
        value_loss.backward(retain_graph=True)
        self.c_optimizer.step()

        return policy_loss.item(), value_loss.item()

def calculate_returns(rewards, discount_factor, normalize = True):
    returns = []
    R = 0
    
    for r in reversed(rewards):
        R = r + R * discount_factor
        returns.insert(0, R)
    
    returns = torch.tensor(returns)
    if normalize and len(returns) > 1:
        returns = (returns - returns.mean()) / returns.std()
        
    return returns