import torch
import torch.nn.functional as F
from agent import QEDRewardMolecule, Agent
from torch.distributions import Categorical
import hyp
import math
import utils
import numpy as np
from torch.utils.tensorboard import SummaryWriter


torch.autograd.set_detect_anomaly(True)
TENSORBOARD_LOG = True
TB_LOG_PATH = "./runs/ac"
episodes = 0
iterations = 200000
update_interval = 20
batch_size = 128
num_updates_per_it = 1

if torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

environment = QEDRewardMolecule(
    discount_factor=hyp.discount_factor,
    atom_types=set(hyp.atom_types),
    init_mol=hyp.start_molecule,
    allow_removal=hyp.allow_removal,
    allow_no_modification=hyp.allow_no_modification,
    allow_bonds_between_rings=hyp.allow_bonds_between_rings,
    allowed_ring_sizes=set(hyp.allowed_ring_sizes),
    max_steps=hyp.max_steps_per_episode,
)

# DQN Inputs and Outputs:
# input: appended action (fingerprint_length + 1) .
# Output size is (1).

agent = Agent(hyp.fingerprint_length + 1, 1, device)

if TENSORBOARD_LOG:
    writer = SummaryWriter(TB_LOG_PATH)

environment.initialize()

eps_threshold = 1.0
p_batch_losses = []
v_batch_losses = []
log_prob_actions = []
rewards = []
values = []
episode_reward = 0

h_out = (torch.zeros([1, 1, 32], dtype=torch.float), torch.zeros([1, 1, 32], dtype=torch.float))

for it in range(iterations):

    h_in = h_out

    steps_left = hyp.max_steps_per_episode - environment.num_steps_taken

    # Compute a list of all possible valid actions. (Here valid_actions stores the states after taking the possible actions)
    valid_actions = list(environment.get_valid_actions())

    # Append each valid action to steps_left and store in observations.
    observations = np.vstack(
        [
            np.append(
                utils.get_fingerprint(
                    act, hyp.fingerprint_length, hyp.fingerprint_radius
                ),
                steps_left,
            )
            for act in valid_actions
        ]
    )  # (num_actions, fingerprint_length)

    observations_tensor = torch.Tensor(observations)
    # Get action through epsilon-greedy policy with the following scheduler.
    # eps_threshold = hyp.epsilon_end + (hyp.epsilon_start - hyp.epsilon_end) * \
    #     math.exp(-1. * it / hyp.epsilon_decay)

    # a, log_prob_action = agent.get_action(observations_tensor) #agent.get_action(observations_tensor, eps_threshold)
    # act = a.detach().data.numpy().astype(int)
    action_prob, value_pred, h_out = agent.get_action(observations_tensor, h_in)
    action_prob = action_prob.flatten()
    m = Categorical(action_prob)
    a = m.sample()
    act = a.item()
    # print('act xxxxxxxxxxx', act[0])
    # Find out the new state (we store the new state in "action" here. Bit confusing but taken from original implementation)
    action = valid_actions[act]
    # Take a step based on the action
    result = environment.step(action)

    action_fingerprint = np.append(
        utils.get_fingerprint(action, hyp.fingerprint_length, hyp.fingerprint_radius),
        steps_left,
    )

    next_state, reward, done = result

    # Compute number of steps left
    steps_left = hyp.max_steps_per_episode - environment.num_steps_taken

    # Append steps_left to the new state and store in next_state
    next_state = utils.get_fingerprint(
        next_state, hyp.fingerprint_length, hyp.fingerprint_radius
    )  # (fingerprint_length)

    action_fingerprints = np.vstack(
        [
            np.append(
                utils.get_fingerprint(
                    act, hyp.fingerprint_length, hyp.fingerprint_radius
                ),
                steps_left,
            )
            for act in environment.get_valid_actions()
        ]
    )  # (num_actions, fingerprint_length + 1)

    # Update replay buffer (state: (fingerprint_length + 1), action: _, reward: (), next_state: (num_actions, fingerprint_length + 1),
    # done: ()

    # agent.replay_buffer.add(
        # obs_t=action_fingerprint,  # (fingerprint_length + 1)
        # action=0,  # No use
        # reward=reward,
        # obs_tp1=action_fingerprints,  # (num_actions, fingerprint_length + 1)
        # done=float(result.terminated),
    # )
    
    # log_prob_actions.append(log_prob_action)
    # rewards.append(reward)
    # print('action_prob, act xxxxxxxxxxx', action_prob, act)
    # agent.add_episodic_data((reward, action_prob[0][act], value[act]))
    rewards.append(reward)
    log_prob_actions.append(torch.log(action_prob[act]))
    values.append(value_pred[act])
    #Notice: I did not take log on prob, so you need to take log in your loss definition

    # episode_reward += reward

    # log_prob_actions = torch.cat(log_prob_actions)

    # returns = agent.calculate_returns(rewards)

    if done:
        final_reward = reward
        if episodes != 0 and TENSORBOARD_LOG and len(p_batch_losses) != 0:
            writer.add_scalar("episode_reward", final_reward, episodes)
            writer.add_scalar("episode_loss", np.array(p_batch_losses).mean(), episodes)
        if episodes != 0 and episodes % 2 == 0 and len(p_batch_losses) != 0:
            print(
                "reward of final molecule at episode {} is {}".format(
                    episodes, final_reward
                )
            )
            print(
                "mean policy loss in episode {} is {}".format(
                    episodes, np.array(p_batch_losses).mean()
                )
            )
            print(
                "mean value loss in episode {} is {}".format(
                    episodes, np.array(v_batch_losses).mean()
                )
            )
        episodes += 1
        eps_threshold *= 0.99907
        batch_losses = []
        log_prob_actions = []
        rewards = []
        values = []
        environment.initialize()

    if it % update_interval == 0: # and agent.replay_buffer.__len__() >= batch_size:
        for update in range(num_updates_per_it):
            p_loss, v_loss = agent.train(rewards, log_prob_actions, values) #It takes no training data, otherwise, I got NaN
            log_prob_actions = []
            rewards = []
            values = []
            # loss = agent.update_policy(returns, log_prob_actions)#agent.update_params(batch_size, hyp.gamma, hyp.polyak)
            # loss = loss.item()
            p_batch_losses.append(p_loss)
            v_batch_losses.append(v_loss)
    
