import gym
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Normal

# Hyperparameters
learning_rate  = 0.0002
gamma         = 0.98
lmbda         = 0.95
n_rollout     = 10
eps_clip        = 0.2

class ActorCritic(nn.Module):
    def __init__(self):
        super(ActorCritic, self).__init__()
        self.data = []
        
        self.fc1   = nn.Linear(3,128)
        self.fc_mu = nn.Linear(128,1)
        self.fc_std  = nn.Linear(128,1)
        self.fc_v = nn.Linear(128,1)
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)

    def pi(self, x, softmax_dim = 0):
        x = F.relu(self.fc1(x))
        mu = 2.0*torch.tanh(self.fc_mu(x))
        std = F.softplus(self.fc_std(x))
        return mu, std
    
    def v(self, x):
        x = F.relu(self.fc1(x))
        v = self.fc_v(x)
        return v
    
    def put_data(self, transition):
        self.data.append(transition)
        
    def make_batch(self):
        s_lst, a_lst, r_lst, s_prime_lst, prob_a_lst, done_lst = [], [], [], [], [], []
        for transition in self.data:
            s,a,r,s_prime,prob_a,done = transition
            s_lst.append(s)
            a_lst.append([a])
            r_lst.append([r/100.0])
            s_prime_lst.append(s_prime)
            prob_a_lst.append(prob_a)
            done_mask = 0.0 if done else 1.0
            done_lst.append([done_mask])
        
        s_batch, a_batch, r_batch, s_prime_batch, prob_a_batch, done_batch = torch.tensor(s_lst, dtype=torch.float), torch.tensor(a_lst), \
                                                               torch.tensor(r_lst, dtype=torch.float), torch.tensor(s_prime_lst, dtype=torch.float), \
                                                               torch.tensor(prob_a_lst, dtype=torch.float), torch.tensor(done_lst, dtype=torch.float)
        self.data = []
        return s_batch, a_batch, r_batch, s_prime_batch, prob_a_batch, done_batch

    def train_net(self):
        s, a, r, s_prime, old_log_prob, done = self.make_batch()
        td_target = r + gamma * self.v(s_prime) * done
        delta = td_target - self.v(s)

        mu, std = self.pi(s, softmax_dim=1)
        dist = Normal(mu, std)
        log_prob = dist.log_prob(a)
        ratio = torch.exp(log_prob - old_log_prob)  # a/b == exp(log(a)-log(b))

        surr1 = ratio * delta.detach()
        surr2 = torch.clamp(ratio, 1-eps_clip, 1+eps_clip) * delta.detach()
        loss = -torch.min(surr1, surr2) + F.smooth_l1_loss(self.v(s) , td_target)

        self.optimizer.zero_grad()
        loss.mean().backward()
        nn.utils.clip_grad_norm_(self.parameters(), 1.0)
        self.optimizer.step()

def main():  
    env = gym.make('Pendulum-v0')
    model = ActorCritic()    
    print_interval = 20
    score = 0.0

    for n_epi in range(10000):
        done = False
        s = env.reset()
        while not done:
            for t in range(n_rollout):
                mu, std = model.pi(torch.from_numpy(s).float())
                m = Normal(mu, std)
                a = m.sample()
                log_prob = m.log_prob(a)
                s_prime, r, done, info = env.step([a.item()])
                model.put_data((s, a, r/10.0, s_prime, log_prob.item(), done))
                
                s = s_prime
                score += r
                
                if done:
                    break                     
            
            model.train_net()
            
        if n_epi%print_interval==0 and n_epi!=0:
            print("# of episode :{}, avg score : {:.1f}".format(n_epi, score/print_interval))
            score = 0.0
    env.close()

if __name__ == '__main__':
    main()
