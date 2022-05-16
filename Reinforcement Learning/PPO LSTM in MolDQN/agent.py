import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import torch.optim as opt
import utils
import hyp
from dqn import MolDQN
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
        self.dqn = MolDQN(input_length, output_length).to(self.device)
        self.data = []
        self.optimizer = getattr(opt, hyp.optimizer)(
            self.dqn.parameters(), lr=hyp.learning_rate
        )

    def put_data(self, transition):
        self.data.append(transition)

    def get_data(self):
        s, a, r, s_prime, prob_a, h_in, h_out, done_mask = [], [], [], [], [], [], [], []
        for i in range(len(self.data)):
            s.append(self.data[i][0])
            a.append(self.data[i][1])
            r.append(self.data[i][2])
            s_prime.append(self.data[i][3])
            prob_a.append(self.data[i][4])
            h_in.append(self.data[i][5])
            h_out.append(self.data[i][6])
            done_mask.append(self.data[i][7])
        return s, a, r, s_prime, prob_a, h_in[0], h_out[0], done_mask

    def network_outputs(self, s, s_prime, a, first_hidden, second_hidden):
        batch_size = len(self.data)
        pi_s = torch.zeros(batch_size, 1, requires_grad=False)
        v_s = torch.zeros(batch_size, 1, requires_grad=False)
        v_s_prime = torch.zeros(batch_size, 1, requires_grad=False)
        for i in range(batch_size):
            state = (
                torch.FloatTensor(s[i])
                .reshape(-1, hyp.fingerprint_length + 1)
                .to(self.device)
            )
            pi_out, _ = self.dqn.pi(state, first_hidden)
            pi_s[i] = torch.max(pi_out.squeeze(1))
            v_s[i] = torch.max(self.dqn.v(state, first_hidden).squeeze(1))

            next_state = (
                torch.FloatTensor(s_prime[i])
                .reshape(-1, hyp.fingerprint_length + 1)
                .to(self.device)
            )
            v_s_prime[i] = torch.max(self.dqn.v(next_state, second_hidden).squeeze(1))
        
        return pi_s, v_s, v_s_prime
    
    def update_params(self):
        s, a, r, s_prime, prob_a, (h1_in, h2_in), (h1_out, h2_out), done_mask = self.get_data()

        first_hidden  = (h1_in.detach(), h2_in.detach())
        second_hidden = (h1_out.detach(), h2_out.detach())
        
        pi_s, v_s, v_s_prime = self.network_outputs(s, s_prime, a, first_hidden, second_hidden)
        a = torch.tensor(a).reshape(pi_s.shape)
        prob_a = torch.tensor(prob_a).reshape(pi_s.shape)
        done_mask = torch.tensor(done_mask).reshape(v_s.shape).to(self.device)
        r = torch.FloatTensor(r).reshape(v_s.shape).to(self.device)
        td_target = r + hyp.gamma * v_s_prime * done_mask
        delta = td_target - v_s
        delta = delta.detach().numpy()
        
        advantage_lst = []
        advantage = 0.0
        for delta_t in delta[::-1]:
            advantage = hyp.gamma * hyp.lmbda * advantage + delta_t[0]
            advantage_lst.append([advantage])
        advantage_lst.reverse()
        advantage = torch.tensor(advantage_lst, dtype=torch.float)

        # print(pi_s.shape)
        # print(a.shape)
        pi_a = pi_s.gather(0,a)
        ratio = torch.exp(torch.log(pi_a) - torch.log(prob_a))  # a/b == exp(log(a)-log(b))

        surr1 = ratio * advantage
        surr2 = torch.clamp(ratio, 1-hyp.eps_clip, 1+hyp.eps_clip) * advantage
        loss = (-torch.min(surr1, surr2) + F.smooth_l1_loss(v_s, td_target.detach())).mean()
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()
