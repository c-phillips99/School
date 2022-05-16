import gym

import argparse
import time
import numpy as np
import collections

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random

import dqn_extra

DEFAULT_ENV_NAME = "CartPole-v0"
MEAN_REWARD_BOUND = 199.5

GAMMA = 0.99
BATCH_SIZE = 32
REPLAY_SIZE = 10000
LEARNING_RATE = 1e-5
SYNC_TARGET_FRAMES = 1000
REPLAY_START_SIZE = 2000

EPSILON_DECAY_LAST_FRAME = 40000
EPSILON_START = 0.75
EPSILON_FINAL = 0.01

Experience = collections.namedtuple(
    'Experience', field_names=['state', 'action', 'reward',
                               'done', 'new_state'])

class ExperienceBuffer:
    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)

    def __len__(self):
        return len(self.buffer)

    def append(self, experience):
        self.buffer.append(experience)

    def sample(self, batch_size):
        indices = np.random.choice(len(self.buffer), batch_size,
                                   replace=False)
        states, actions, rewards, dones, next_states = \
            zip(*[self.buffer[idx] for idx in indices])
        return np.array(states), np.array(actions), \
               np.array(rewards, dtype=np.float32), \
               np.array(dones, dtype=np.bool), \
               np.array(next_states)


class Agent:
    def __init__(self, env, exp_buffer):
        self.env = env
        self.exp_buffer = exp_buffer
        self._reset()

    def _reset(self):
        self.state = env.reset()
        self.total_reward = 0.0

    @torch.no_grad()
    def play_step(self, net, epsilon=0.0, device="cpu"):
        done_reward = None

        if np.random.random() < epsilon:
            action = env.action_space.sample()
        else:
            state_a = np.array([self.state], copy=False)
            state_v = torch.tensor(state_a).type('torch.FloatTensor').to(device)
            q_vals_v = net.qvals(state_v)
            act_v = torch.argmax(q_vals_v, dim=1)
            action = int(act_v.item())

        # do step in the environment
        new_state, reward, is_done, _ = self.env.step(action)
        self.total_reward += reward

        exp = Experience(self.state, action, reward,
                         is_done, new_state)
        self.exp_buffer.append(exp)
        self.state = new_state
        if is_done:
            done_reward = self.total_reward
            self._reset()
        return done_reward

def calc_loss(batch, net, tgt_net, gamma=GAMMA, device="cpu"):
    states, actions, rewards, dones, next_states = batch
    batch_size = 32

    states_v = torch.FloatTensor(states).to(device)
    actions_v = torch.LongTensor(actions).to(device)
    next_states_v = torch.FloatTensor(next_states).to(device)

    # next state distribution
    next_distr_v, next_qvals_v = tgt_net.both(next_states_v)
    next_acts = next_qvals_v.max(1)[1].data.cpu().numpy()
    next_distr = tgt_net.apply_softmax(next_distr_v)
    next_distr = next_distr.data.cpu().numpy()

    next_best_distr = next_distr[range(batch_size), next_acts]
    dones = dones.astype(np.bool)

    proj_distr = dqn_extra.distr_projection(
        next_best_distr, rewards, dones, gamma)

    distr_v = net(states_v)
    sa_vals = distr_v[range(batch_size), actions_v.data]
    state_log_sm_v = F.log_softmax(sa_vals, dim=1)
    proj_distr_v = torch.tensor(proj_distr).to(device)

    loss_v = -state_log_sm_v * proj_distr_v
    return loss_v.sum(dim=1).mean()

if __name__ == "__main__":
    env = env = gym.make(DEFAULT_ENV_NAME)
    device = "cpu"
    net = dqn_extra.DistributionalDQN(env.observation_space.shape, 512, env.action_space.n).to(device)
    tgt_net = dqn_extra.DistributionalDQN(env.observation_space.shape, 512, env.action_space.n).to(device)
    print(net)

    buffer = ExperienceBuffer(REPLAY_SIZE)
    agent = Agent(env, buffer)
    epsilon = EPSILON_START

    optimizer = optim.Adam(net.parameters(), lr=LEARNING_RATE)
    total_rewards = []
    frame_idx = 0
    best_m_reward = None

    while True:
        frame_idx += 1
        epsilon = max(EPSILON_FINAL, EPSILON_START -
                      frame_idx / EPSILON_DECAY_LAST_FRAME)

        reward = agent.play_step(net, epsilon, device=device)
        if reward is not None:
            total_rewards.append(reward)
            m_reward = np.mean(total_rewards[-100:])
            print("%d: done %d games, reward %.3f, "
                  "eps %.2f" % (
                frame_idx, len(total_rewards), m_reward, epsilon
            ))
            if best_m_reward is None or best_m_reward < m_reward:
                best_m_reward = m_reward
            if m_reward >= MEAN_REWARD_BOUND:
                print("Solved in %d frames!" % frame_idx)
                break

        if len(buffer) < REPLAY_START_SIZE:
            continue

        if frame_idx % SYNC_TARGET_FRAMES == 0:
            tgt_net.load_state_dict(net.state_dict())

        optimizer.zero_grad()
        batch = buffer.sample(BATCH_SIZE)
        loss_v = calc_loss(batch, net, tgt_net, gamma=GAMMA, device=device)
        loss_v.backward()
        optimizer.step()
