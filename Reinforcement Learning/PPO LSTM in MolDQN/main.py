import torch
from agent import Agent
from agent import QEDRewardMolecule, Agent
import hyp
import math
import utils
import numpy as np
from torch.distributions import Categorical
from torch.utils.tensorboard import SummaryWriter

TENSORBOARD_LOG = True
TB_LOG_PATH = "./runs/dqn/run2"
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
batch_losses = []
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
    prob, h_out = agent.dqn.pi(observations_tensor, h_in)
    prob = prob.flatten()
    m = Categorical(prob)
    a = m.sample().item()
    action = valid_actions[a]

    action_fingerprint = np.append(
        utils.get_fingerprint(action, hyp.fingerprint_length, hyp.fingerprint_radius),
        steps_left,
    )

    s_prime, r, done = environment.step(action)

    # Update replay buffer (state: (fingerprint_length + 1), action: _, reward: (), next_state: (num_actions, fingerprint_length + 1),
    # done: ()
    # Compute number of steps left
    steps_left = hyp.max_steps_per_episode - environment.num_steps_taken

    # Append steps_left to the new state and store in next_state
    s_prime = utils.get_fingerprint(
        s_prime, hyp.fingerprint_length, hyp.fingerprint_radius
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

    agent.put_data((
        observations_tensor,  # (fingerprint_length + 1)
        a,
        r,
        action_fingerprints,  # (num_actions, fingerprint_length + 1)
        prob[a].item(),
        h_in,
        h_out,
        float(done),
    ))

    if done:
        final_reward = r
        if episodes != 0 and TENSORBOARD_LOG and len(batch_losses) != 0:
            writer.add_scalar("episode_reward", final_reward, episodes)
            writer.add_scalar("episode_loss", np.array(batch_losses).mean(), episodes)
        if episodes != 0 and episodes % 2 == 0 and len(batch_losses) != 0:
            print(
                "reward of final molecule at episode {} is {}".format(
                    episodes, final_reward
                )
            )
            print(
                "mean loss in episode {} is {}".format(
                    episodes, np.array(batch_losses).mean()
                )
            )
        episodes += 1
        eps_threshold *= 0.99907
        batch_losses = []
        environment.initialize()

    if it % update_interval == 0 and len(agent.data) >= batch_size:
        for update in range(num_updates_per_it):
            loss = agent.update_params()
            batch_losses.append(loss)
