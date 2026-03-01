# Chapter 12: Reinforcement Learning

## Table of Contents

1. [What is Reinforcement Learning?](#1-what-is-reinforcement-learning)
2. [Core Concepts and Terminology](#2-core-concepts-and-terminology)
3. [Markov Decision Processes (MDPs)](#3-markov-decision-processes-mdps)
4. [Dynamic Programming](#4-dynamic-programming)
5. [Monte Carlo Methods](#5-monte-carlo-methods)
6. [Temporal Difference Learning](#6-temporal-difference-learning)
7. [Q-Learning (Off-Policy TD)](#7-q-learning-off-policy-td)
8. [Deep Q-Networks (DQN)](#8-deep-q-networks-dqn)
9. [Policy Gradient Methods](#9-policy-gradient-methods)
10. [Actor-Critic Methods](#10-actor-critic-methods)
11. [Proximal Policy Optimization (PPO)](#11-proximal-policy-optimization-ppo)
12. [Soft Actor-Critic (SAC)](#12-soft-actor-critic-sac)
13. [Model-Based Reinforcement Learning](#13-model-based-reinforcement-learning)
14. [Multi-Agent Reinforcement Learning](#14-multi-agent-reinforcement-learning)
15. [Reward Shaping and Curriculum Learning](#15-reward-shaping-and-curriculum-learning)
16. [RLHF (RL from Human Feedback)](#16-rlhf-rl-from-human-feedback)
17. [Practical RL with Gymnasium and Stable-Baselines3](#17-practical-rl-with-gymnasium-and-stable-baselines3)
18. [Summary and Key Takeaways](#18-summary-and-key-takeaways)

---

## 1. What is Reinforcement Learning?

Reinforcement Learning (RL) is the third major paradigm of machine learning, alongside supervised and unsupervised learning. In RL, an **agent** learns to make decisions by interacting with an **environment**. The agent takes **actions**, receives **rewards** (or penalties), and learns a **policy** -- a strategy for choosing actions that maximize cumulative reward over time.

### How RL Differs from Other ML

| Aspect | Supervised Learning | Unsupervised Learning | Reinforcement Learning |
|--------|--------------------|-----------------------|------------------------|
| Data | Labeled pairs (x, y) | Unlabeled data x | State, action, reward sequences |
| Feedback | Correct answer given | No feedback | Scalar reward signal |
| Goal | Predict labels | Find structure/patterns | Maximize cumulative reward |
| Timing | One-shot prediction | One-shot | Sequential decisions |
| Exploration | Not needed | Not needed | Critical |

### Real-World Applications

- **Game playing**: AlphaGo, AlphaZero, OpenAI Five (Dota 2), AlphaStar (StarCraft II)
- **Robotics**: Locomotion, grasping, manipulation
- **Autonomous driving**: Lane following, obstacle avoidance, parking
- **Natural language**: RLHF for aligning large language models (ChatGPT, Claude)
- **Resource management**: Data center cooling, network routing, inventory management
- **Drug discovery**: Molecular design, clinical trial optimization
- **Finance**: Portfolio optimization, algorithmic trading
- **Recommendation systems**: Content recommendation with long-term user engagement

### The RL Loop

```
     +----------+     action a_t     +-----------+
     |          |-------------------->|           |
     |  Agent   |                     |Environment|
     |          |<--------------------|           |
     +----------+   state s_{t+1},    +-----------+
                     reward r_{t+1}
```

At each time step t:
1. Agent observes the current state s_t
2. Agent selects an action a_t based on its policy
3. Environment transitions to a new state s_{t+1}
4. Environment provides a reward r_{t+1} to the agent
5. Agent updates its policy based on this experience
6. Repeat

---

## 2. Core Concepts and Terminology

### 2.1 Agent and Environment

The **agent** is the learner and decision maker. The **environment** is everything the agent interacts with. The boundary between agent and environment is defined by what the agent can control (actions) versus what it cannot (environment dynamics).

### 2.2 State (s)

A state captures all relevant information about the current situation. Examples:
- Chess: The positions of all pieces on the board
- Robotics: Joint angles, velocities, object positions
- Game: Player position, health, inventory, enemy positions

```python
# Example: A simple grid world state
# The state is the (row, col) position of the agent
state = (2, 3)  # Agent is at row 2, column 3

# Example: Cart-Pole state
# [cart_position, cart_velocity, pole_angle, pole_angular_velocity]
state = [0.01, -0.02, 0.03, 0.01]

# Example: Atari game state -- raw pixels
# state is a (210, 160, 3) RGB image
import numpy as np
state = np.random.randint(0, 255, (210, 160, 3), dtype=np.uint8)
```

### 2.3 Action (a)

An action is a decision the agent makes. Actions can be:

- **Discrete**: A finite set of choices (move left, right, up, down; buy, sell, hold)
- **Continuous**: A real-valued vector (joint torques, steering angle, throttle)

```python
# Discrete action space
# e.g., in a game: 0=left, 1=right, 2=up, 3=down, 4=fire
action = 2  # "up"

# Continuous action space
# e.g., in robotics: [torque_joint1, torque_joint2, torque_joint3]
import numpy as np
action = np.array([0.5, -0.3, 0.7])
```

### 2.4 Reward (r)

The reward is a scalar signal that tells the agent how well it is doing. The entire goal of RL is to maximize the **cumulative** reward, not just the immediate reward.

```python
# Sparse reward: only at the end
# - Win the game: +1
# - Lose the game: -1
# - Every other step: 0

# Dense reward: at every step
# - Move closer to the goal: +0.1
# - Move further from goal: -0.1
# - Reach the goal: +10
# - Fall off the edge: -10

# Shaped reward example for a robot reaching a target
def compute_reward(robot_pos, target_pos, reached, fell):
    distance = np.linalg.norm(robot_pos - target_pos)
    
    if reached:
        return 100.0   # Large bonus for success
    elif fell:
        return -100.0  # Large penalty for failure
    else:
        return -distance * 0.1  # Small penalty proportional to distance
```

### 2.5 Policy (pi)

The policy is the agent's strategy -- a mapping from states to actions. It tells the agent what to do in any given state.

- **Deterministic policy**: pi(s) = a (always the same action for a given state)
- **Stochastic policy**: pi(a|s) = P(a|s) (probability distribution over actions)

```python
# Deterministic policy example
def deterministic_policy(state):
    if state[0] < 0:
        return 0  # Move right
    else:
        return 1  # Move left

# Stochastic policy example
import torch
import torch.nn as nn

class StochasticPolicy(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
            nn.Softmax(dim=-1)  # Output probabilities
        )
    
    def forward(self, state):
        """Returns action probabilities."""
        return self.network(state)
    
    def sample_action(self, state):
        """Sample an action from the policy."""
        probs = self.forward(state)
        dist = torch.distributions.Categorical(probs)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob
```

### 2.6 Value Function V(s)

The value function estimates how good it is to be in a particular state. Formally, V(s) is the expected cumulative reward starting from state s and following policy pi:

$$V^{\pi}(s) = E_{\pi}\left[\sum_{t=0}^{\infty} \gamma^t r_{t+1} \mid s_0 = s\right]$$

Where gamma (discount factor, 0 < gamma <= 1) determines how much future rewards are worth relative to immediate rewards:
- gamma = 0: Only care about immediate reward (greedy/myopic)
- gamma = 0.99: Future rewards almost as valuable as immediate
- gamma = 1: All rewards equally important (only for finite episodes)

### 2.7 Action-Value Function Q(s, a)

Q(s, a) estimates the value of taking action a in state s, then following policy pi:

$$Q^{\pi}(s, a) = E_{\pi}\left[\sum_{t=0}^{\infty} \gamma^t r_{t+1} \mid s_0 = s, a_0 = a\right]$$

The relationship between V and Q:

$$V^{\pi}(s) = \sum_a \pi(a|s) \cdot Q^{\pi}(s, a)$$

### 2.8 Advantage Function A(s, a)

The advantage tells you how much better action a is compared to the average action in state s:

$$A^{\pi}(s, a) = Q^{\pi}(s, a) - V^{\pi}(s)$$

If A(s, a) > 0, action a is better than average. If A(s, a) < 0, it is worse than average.

---

## 3. Markov Decision Processes (MDPs)

An MDP is the mathematical framework underlying RL. It consists of:

- **S**: Set of states
- **A**: Set of actions
- **P(s'|s, a)**: Transition probability -- probability of moving to state s' when taking action a in state s
- **R(s, a, s')**: Reward function -- reward received for transitioning from s to s' via action a
- **gamma**: Discount factor

The **Markov property** states that the future depends only on the current state, not the history:

$$P(s_{t+1} | s_t, a_t, s_{t-1}, a_{t-1}, \ldots) = P(s_{t+1} | s_t, a_t)$$

```python
class GridWorldMDP:
    """
    A simple grid world MDP.
    
    The agent moves in a 2D grid. It can move up, down, left, right.
    The goal is to reach the goal state while avoiding obstacles.
    """
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
        self.n_states = rows * cols
        self.n_actions = 4  # up, down, left, right
        
        # State: (row, col) encoded as row * cols + col
        self.start_state = 0             # Top-left
        self.goal_state = rows * cols - 1  # Bottom-right
        self.obstacles = {6, 7, 11, 12}  # Blocked cells
        
        # Action mapping
        self.action_deltas = {
            0: (-1, 0),  # up
            1: (1, 0),   # down
            2: (0, -1),  # left
            3: (0, 1),   # right
        }
        
        self.gamma = 0.99  # Discount factor
    
    def state_to_rc(self, state):
        """Convert state index to (row, col)."""
        return state // self.cols, state % self.cols
    
    def rc_to_state(self, row, col):
        """Convert (row, col) to state index."""
        return row * self.cols + col
    
    def get_transitions(self, state, action):
        """
        Returns list of (probability, next_state, reward, done) tuples.
        
        This MDP is deterministic (probability = 1.0), but the framework
        supports stochastic transitions.
        """
        if state == self.goal_state:
            return [(1.0, state, 0.0, True)]  # Terminal state
        
        row, col = self.state_to_rc(state)
        dr, dc = self.action_deltas[action]
        new_row, new_col = row + dr, col + dc
        
        # Check boundaries
        if (new_row < 0 or new_row >= self.rows or 
            new_col < 0 or new_col >= self.cols):
            new_row, new_col = row, col  # Stay in place
        
        new_state = self.rc_to_state(new_row, new_col)
        
        # Check obstacles
        if new_state in self.obstacles:
            new_state = state  # Bounce back
        
        # Reward
        if new_state == self.goal_state:
            reward = 1.0
        else:
            reward = -0.01  # Small step penalty to encourage efficiency
        
        done = (new_state == self.goal_state)
        
        return [(1.0, new_state, reward, done)]
    
    def step(self, state, action):
        """Take an action, return (next_state, reward, done)."""
        transitions = self.get_transitions(state, action)
        probs = [t[0] for t in transitions]
        idx = np.random.choice(len(transitions), p=probs)
        _, next_state, reward, done = transitions[idx]
        return next_state, reward, done
    
    def reset(self):
        """Reset to start state."""
        return self.start_state
```

### The Bellman Equation

The value function satisfies a recursive relationship called the Bellman equation:

$$V^{\pi}(s) = \sum_a \pi(a|s) \sum_{s'} P(s'|s, a) \left[R(s, a, s') + \gamma V^{\pi}(s')\right]$$

For the optimal policy:

$$V^*(s) = \max_a \sum_{s'} P(s'|s, a) \left[R(s, a, s') + \gamma V^*(s')\right]$$

$$Q^*(s, a) = \sum_{s'} P(s'|s, a) \left[R(s, a, s') + \gamma \max_{a'} Q^*(s', a')\right]$$

---

## 4. Dynamic Programming

Dynamic Programming (DP) methods solve MDPs when the model is fully known (transition probabilities and rewards). They are not practical for large or unknown environments, but they provide the theoretical foundation for all RL algorithms.

### 4.1 Policy Evaluation (Prediction)

Given a policy pi, compute V^pi(s) for all states:

```python
import numpy as np

def policy_evaluation(mdp, policy, theta=1e-6):
    """
    Iteratively compute the value function for a given policy.
    
    mdp: the MDP environment
    policy: (n_states, n_actions) array of action probabilities
    theta: convergence threshold
    
    Returns: V (n_states,) -- value of each state under this policy
    """
    V = np.zeros(mdp.n_states)
    
    iteration = 0
    while True:
        delta = 0  # Maximum change in V
        
        for s in range(mdp.n_states):
            v_old = V[s]
            
            # Bellman equation for policy pi
            v_new = 0
            for a in range(mdp.n_actions):
                if policy[s, a] == 0:
                    continue
                
                for prob, next_state, reward, done in mdp.get_transitions(s, a):
                    if done:
                        v_new += policy[s, a] * prob * reward
                    else:
                        v_new += policy[s, a] * prob * (reward + mdp.gamma * V[next_state])
            
            V[s] = v_new
            delta = max(delta, abs(v_old - v_new))
        
        iteration += 1
        
        if delta < theta:
            print(f"Policy evaluation converged in {iteration} iterations")
            break
    
    return V
```

### 4.2 Policy Improvement

Given V^pi, construct a better policy by acting greedily with respect to V:

```python
def policy_improvement(mdp, V):
    """
    Compute the greedy policy with respect to value function V.
    
    For each state, the greedy action is the one that maximizes
    the expected value of the next state.
    """
    policy = np.zeros((mdp.n_states, mdp.n_actions))
    
    for s in range(mdp.n_states):
        action_values = np.zeros(mdp.n_actions)
        
        for a in range(mdp.n_actions):
            for prob, next_state, reward, done in mdp.get_transitions(s, a):
                if done:
                    action_values[a] += prob * reward
                else:
                    action_values[a] += prob * (reward + mdp.gamma * V[next_state])
        
        # Greedy: put all probability on the best action
        best_action = np.argmax(action_values)
        policy[s, best_action] = 1.0
    
    return policy
```

### 4.3 Policy Iteration

Alternate between evaluation and improvement until the policy converges:

```python
def policy_iteration(mdp):
    """
    Find the optimal policy using policy iteration.
    
    1. Start with a random policy
    2. Evaluate the policy (compute V)
    3. Improve the policy (act greedily w.r.t. V)
    4. If the policy did not change, we have the optimal policy
    5. Otherwise, go to step 2
    """
    # Initialize random policy (uniform)
    policy = np.ones((mdp.n_states, mdp.n_actions)) / mdp.n_actions
    
    iteration = 0
    while True:
        # Step 2: Evaluate
        V = policy_evaluation(mdp, policy)
        
        # Step 3: Improve
        new_policy = policy_improvement(mdp, V)
        
        # Step 4: Check convergence
        if np.array_equal(policy, new_policy):
            print(f"Policy iteration converged in {iteration} iterations")
            break
        
        policy = new_policy
        iteration += 1
    
    return policy, V
```

### 4.4 Value Iteration

Combine evaluation and improvement into a single update:

```python
def value_iteration(mdp, theta=1e-6):
    """
    Find the optimal value function directly.
    
    Uses the Bellman optimality equation:
    V*(s) = max_a sum_{s'} P(s'|s,a) * [R(s,a,s') + gamma * V*(s')]
    
    This is more efficient than policy iteration for large state spaces
    because it does not need full policy evaluation at each step.
    """
    V = np.zeros(mdp.n_states)
    
    iteration = 0
    while True:
        delta = 0
        
        for s in range(mdp.n_states):
            v_old = V[s]
            
            # Bellman optimality: take the max over all actions
            action_values = np.zeros(mdp.n_actions)
            for a in range(mdp.n_actions):
                for prob, next_state, reward, done in mdp.get_transitions(s, a):
                    if done:
                        action_values[a] += prob * reward
                    else:
                        action_values[a] += prob * (reward + mdp.gamma * V[next_state])
            
            V[s] = np.max(action_values)
            delta = max(delta, abs(v_old - V[s]))
        
        iteration += 1
        
        if delta < theta:
            print(f"Value iteration converged in {iteration} iterations")
            break
    
    # Extract optimal policy
    policy = policy_improvement(mdp, V)
    
    return policy, V
```

---

## 5. Monte Carlo Methods

Monte Carlo (MC) methods learn from complete episodes of experience. They do not require knowledge of the environment dynamics (model-free).

### 5.1 First-Visit Monte Carlo Prediction

```python
def monte_carlo_prediction(env, policy, n_episodes=10000, gamma=0.99):
    """
    Estimate V^pi using Monte Carlo first-visit method.
    
    For each state, average the returns observed after the first visit
    to that state across all episodes.
    """
    V = {}          # Value estimates
    returns = {}    # List of returns for each state
    
    for episode_num in range(n_episodes):
        # Generate an episode
        episode = []
        state = env.reset()
        done = False
        
        while not done:
            action = np.random.choice(env.n_actions, p=policy[state])
            next_state, reward, done = env.step(state, action)
            episode.append((state, action, reward))
            state = next_state
        
        # Calculate returns for each state (first visit)
        G = 0  # Return (cumulative discounted reward)
        visited_states = set()
        
        # Walk backward through the episode
        for t in range(len(episode) - 1, -1, -1):
            state_t, action_t, reward_t = episode[t]
            G = gamma * G + reward_t
            
            # First-visit: only count the first time we visit this state
            if state_t not in visited_states:
                visited_states.add(state_t)
                
                if state_t not in returns:
                    returns[state_t] = []
                returns[state_t].append(G)
                
                # Value = average of all observed returns
                V[state_t] = np.mean(returns[state_t])
    
    return V
```

### 5.2 Monte Carlo Control (Finding Optimal Policy)

```python
def monte_carlo_control(env, n_episodes=100000, gamma=0.99, epsilon=0.1):
    """
    Find the optimal policy using Monte Carlo with epsilon-greedy exploration.
    
    Epsilon-greedy: with probability epsilon, take a random action.
    With probability (1 - epsilon), take the best action.
    This ensures continued exploration.
    """
    Q = {}  # Action-value function: Q[(state, action)] = value
    returns = {}
    
    # Initialize Q for all (state, action) pairs
    for s in range(env.n_states):
        for a in range(env.n_actions):
            Q[(s, a)] = 0.0
            returns[(s, a)] = []
    
    for episode_num in range(n_episodes):
        # Generate episode using epsilon-greedy policy derived from Q
        episode = []
        state = env.reset()
        done = False
        
        while not done:
            # Epsilon-greedy action selection
            if np.random.random() < epsilon:
                action = np.random.randint(env.n_actions)
            else:
                # Greedy: pick action with highest Q
                q_values = [Q[(state, a)] for a in range(env.n_actions)]
                action = np.argmax(q_values)
            
            next_state, reward, done = env.step(state, action)
            episode.append((state, action, reward))
            state = next_state
        
        # Update Q values
        G = 0
        visited = set()
        
        for t in range(len(episode) - 1, -1, -1):
            state_t, action_t, reward_t = episode[t]
            G = gamma * G + reward_t
            
            sa_pair = (state_t, action_t)
            if sa_pair not in visited:
                visited.add(sa_pair)
                returns[sa_pair].append(G)
                Q[sa_pair] = np.mean(returns[sa_pair])
        
        # Decay epsilon over time
        if episode_num % 10000 == 0:
            epsilon = max(0.01, epsilon * 0.99)
            print(f"Episode {episode_num}, Epsilon: {epsilon:.3f}")
    
    # Extract final policy
    policy = np.zeros((env.n_states, env.n_actions))
    for s in range(env.n_states):
        q_values = [Q[(s, a)] for a in range(env.n_actions)]
        best_action = np.argmax(q_values)
        policy[s, best_action] = 1.0
    
    return policy, Q
```

---

## 6. Temporal Difference Learning

TD methods bridge Monte Carlo and Dynamic Programming. They learn from incomplete episodes by bootstrapping -- using current estimates to update other estimates.

### 6.1 TD(0) Prediction

```python
def td_zero_prediction(env, policy, n_episodes=10000, alpha=0.1, gamma=0.99):
    """
    TD(0) prediction: estimate V^pi.
    
    Update rule:
    V(s) <- V(s) + alpha * [r + gamma * V(s') - V(s)]
    
    The term [r + gamma * V(s') - V(s)] is the TD error (delta).
    It measures the difference between the estimated value and
    the bootstrapped target (r + gamma * V(s')).
    
    Unlike Monte Carlo, TD(0) updates after EVERY step, not just at
    the end of the episode. This means:
    - Lower variance (does not need full episode return)
    - Some bias (bootstrapping from estimated V)
    - Can learn online, from incomplete episodes
    """
    V = np.zeros(env.n_states)
    
    for episode in range(n_episodes):
        state = env.reset()
        done = False
        
        while not done:
            action = np.random.choice(env.n_actions, p=policy[state])
            next_state, reward, done = env.step(state, action)
            
            # TD update
            if done:
                td_target = reward
            else:
                td_target = reward + gamma * V[next_state]
            
            td_error = td_target - V[state]
            V[state] += alpha * td_error
            
            state = next_state
    
    return V
```

### 6.2 SARSA (On-Policy TD Control)

```python
def sarsa(env, n_episodes=10000, alpha=0.1, gamma=0.99, epsilon=0.1):
    """
    SARSA: State-Action-Reward-State-Action.
    
    On-policy TD control: learns Q^pi while following pi.
    
    Update rule:
    Q(s, a) <- Q(s, a) + alpha * [r + gamma * Q(s', a') - Q(s, a)]
    
    The name "SARSA" comes from the quintuplet (s, a, r, s', a')
    used in the update. The key difference from Q-learning is that
    SARSA uses the ACTUAL next action a' (chosen by the policy),
    not the BEST next action.
    """
    Q = np.zeros((env.n_states, env.n_actions))
    
    def epsilon_greedy(state):
        if np.random.random() < epsilon:
            return np.random.randint(env.n_actions)
        return np.argmax(Q[state])
    
    for episode in range(n_episodes):
        state = env.reset()
        action = epsilon_greedy(state)
        done = False
        
        while not done:
            next_state, reward, done = env.step(state, action)
            
            if done:
                Q[state, action] += alpha * (reward - Q[state, action])
            else:
                next_action = epsilon_greedy(next_state)
                td_target = reward + gamma * Q[next_state, next_action]
                Q[state, action] += alpha * (td_target - Q[state, action])
                state = next_state
                action = next_action
    
    return Q
```

---

## 7. Q-Learning (Off-Policy TD)

Q-Learning is the most famous RL algorithm. It directly learns the optimal Q-function regardless of the policy being followed (off-policy).

```python
def q_learning(env, n_episodes=10000, alpha=0.1, gamma=0.99, epsilon=0.1):
    """
    Q-Learning: Off-policy TD control.
    
    Update rule:
    Q(s, a) <- Q(s, a) + alpha * [r + gamma * max_a' Q(s', a') - Q(s, a)]
    
    Key difference from SARSA: uses max_a' Q(s', a') instead of Q(s', a').
    This means it learns the OPTIMAL policy even while following an
    exploratory (epsilon-greedy) policy.
    
    This is "off-policy" because the policy being learned (greedy/optimal)
    is different from the policy being followed (epsilon-greedy).
    """
    Q = np.zeros((env.n_states, env.n_actions))
    
    # Track rewards per episode for monitoring
    episode_rewards = []
    
    for episode in range(n_episodes):
        state = env.reset()
        done = False
        total_reward = 0
        
        while not done:
            # Epsilon-greedy action selection (behavior policy)
            if np.random.random() < epsilon:
                action = np.random.randint(env.n_actions)
            else:
                action = np.argmax(Q[state])
            
            next_state, reward, done = env.step(state, action)
            total_reward += reward
            
            # Q-Learning update (uses max over next actions)
            if done:
                td_target = reward
            else:
                td_target = reward + gamma * np.max(Q[next_state])
            
            td_error = td_target - Q[state, action]
            Q[state, action] += alpha * td_error
            
            state = next_state
        
        episode_rewards.append(total_reward)
        
        # Decay epsilon
        epsilon = max(0.01, epsilon * 0.999)
        
        if episode % 1000 == 0:
            avg_reward = np.mean(episode_rewards[-100:])
            print(f"Episode {episode}, Avg Reward: {avg_reward:.2f}, Epsilon: {epsilon:.3f}")
    
    return Q, episode_rewards
```

### On-Policy vs Off-Policy

| Aspect | On-Policy (SARSA) | Off-Policy (Q-Learning) |
|--------|------------------|------------------------|
| Update uses | Actual next action a' from policy | Best next action max Q(s', a') |
| Learns | Q for the current policy | Optimal Q directly |
| Safer | Yes (accounts for exploration) | No (can overestimate) |
| Data efficiency | Lower | Higher (can use any data) |

---

## 8. Deep Q-Networks (DQN)

Tabular Q-learning does not scale to large or continuous state spaces (you cannot have a table entry for every possible state). Deep Q-Networks (Mnih et al., 2015) replace the Q-table with a neural network that approximates Q(s, a).

### 8.1 Core DQN Architecture

```python
import torch
import torch.nn as nn
import numpy as np
from collections import deque
import random

class DQN(nn.Module):
    """
    Deep Q-Network: neural network that approximates Q(s, a).
    
    Input: state (e.g., 84x84x4 stacked frames for Atari)
    Output: Q-value for each action
    """
    def __init__(self, input_shape, n_actions):
        super().__init__()
        
        # For image-based observations (e.g., Atari)
        if len(input_shape) == 3:
            self.features = nn.Sequential(
                nn.Conv2d(input_shape[0], 32, kernel_size=8, stride=4),
                nn.ReLU(),
                nn.Conv2d(32, 64, kernel_size=4, stride=2),
                nn.ReLU(),
                nn.Conv2d(64, 64, kernel_size=3, stride=1),
                nn.ReLU(),
            )
            # Calculate flattened feature size
            dummy = torch.zeros(1, *input_shape)
            flat_size = self.features(dummy).view(1, -1).shape[1]
            
            self.q_values = nn.Sequential(
                nn.Linear(flat_size, 512),
                nn.ReLU(),
                nn.Linear(512, n_actions)
            )
        else:
            # For vector observations (e.g., CartPole)
            self.features = nn.Identity()
            self.q_values = nn.Sequential(
                nn.Linear(input_shape[0], 128),
                nn.ReLU(),
                nn.Linear(128, 128),
                nn.ReLU(),
                nn.Linear(128, n_actions)
            )
    
    def forward(self, x):
        """
        x: state tensor
        Returns: (batch, n_actions) Q-values for each action
        """
        if isinstance(self.features, nn.Identity):
            return self.q_values(x)
        else:
            features = self.features(x)
            features = features.view(features.size(0), -1)
            return self.q_values(features)
```

### 8.2 Experience Replay

One of the key innovations in DQN. Instead of learning from consecutive experiences (which are correlated), store experiences in a buffer and sample random mini-batches:

```python
class ReplayBuffer:
    """
    Experience replay buffer.
    
    Why it is necessary:
    1. Breaks correlations between consecutive samples
    2. Each experience can be reused multiple times
    3. Stabilizes training dramatically
    """
    def __init__(self, capacity=100000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Store a transition."""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """Sample a random batch of transitions."""
        batch = random.sample(self.buffer, batch_size)
        
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32)
        )
    
    def __len__(self):
        return len(self.buffer)


class PrioritizedReplayBuffer:
    """
    Prioritized Experience Replay: sample more important experiences 
    more frequently. Priority is based on TD error magnitude.
    
    Experiences with larger TD error are more "surprising" and thus
    more useful for learning.
    """
    def __init__(self, capacity=100000, alpha=0.6, beta=0.4):
        self.capacity = capacity
        self.alpha = alpha    # Priority exponent (0 = uniform, 1 = full priority)
        self.beta = beta      # Importance sampling exponent
        self.buffer = []
        self.priorities = np.zeros(capacity, dtype=np.float32)
        self.position = 0
    
    def push(self, state, action, reward, next_state, done):
        max_priority = self.priorities[:len(self.buffer)].max() if self.buffer else 1.0
        
        if len(self.buffer) < self.capacity:
            self.buffer.append((state, action, reward, next_state, done))
        else:
            self.buffer[self.position] = (state, action, reward, next_state, done)
        
        self.priorities[self.position] = max_priority
        self.position = (self.position + 1) % self.capacity
    
    def sample(self, batch_size):
        n = len(self.buffer)
        
        # Calculate sampling probabilities
        priorities = self.priorities[:n] ** self.alpha
        probs = priorities / priorities.sum()
        
        # Sample indices based on priority
        indices = np.random.choice(n, batch_size, p=probs, replace=False)
        
        # Importance sampling weights (to correct for biased sampling)
        weights = (n * probs[indices]) ** (-self.beta)
        weights = weights / weights.max()  # Normalize
        
        batch = [self.buffer[i] for i in indices]
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32),
            indices,
            weights.astype(np.float32)
        )
    
    def update_priorities(self, indices, td_errors):
        """Update priorities based on new TD errors."""
        for idx, td_error in zip(indices, td_errors):
            self.priorities[idx] = abs(td_error) + 1e-6  # Small epsilon to avoid zero
```

### 8.3 Complete DQN Training Loop

```python
class DQNAgent:
    """
    Complete DQN agent with:
    - Experience replay
    - Target network (for stable targets)
    - Epsilon-greedy exploration with decay
    """
    def __init__(
        self,
        state_shape,
        n_actions,
        lr=1e-4,
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_end=0.01,
        epsilon_decay=10000,
        buffer_size=100000,
        batch_size=32,
        target_update_freq=1000,
        device="cuda"
    ):
        self.device = torch.device(device)
        self.n_actions = n_actions
        self.gamma = gamma
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        
        # Epsilon schedule
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.steps_done = 0
        
        # Online network (the one we train)
        self.online_net = DQN(state_shape, n_actions).to(self.device)
        
        # Target network (provides stable targets)
        # Periodically copy weights from online network
        self.target_net = DQN(state_shape, n_actions).to(self.device)
        self.target_net.load_state_dict(self.online_net.state_dict())
        self.target_net.eval()  # Target network is never in training mode
        
        self.optimizer = torch.optim.Adam(self.online_net.parameters(), lr=lr)
        self.replay_buffer = ReplayBuffer(capacity=buffer_size)
    
    def get_epsilon(self):
        """Exponential epsilon decay schedule."""
        epsilon = self.epsilon_end + (self.epsilon_start - self.epsilon_end) * \
            np.exp(-self.steps_done / self.epsilon_decay)
        return epsilon
    
    def select_action(self, state):
        """Epsilon-greedy action selection."""
        epsilon = self.get_epsilon()
        self.steps_done += 1
        
        if np.random.random() < epsilon:
            return np.random.randint(self.n_actions)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.online_net(state_tensor)
            return q_values.argmax(dim=1).item()
    
    def train_step(self):
        """One training step: sample batch, compute loss, update."""
        if len(self.replay_buffer) < self.batch_size:
            return None
        
        # Sample mini-batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Current Q values: Q(s, a) for the actions we actually took
        current_q = self.online_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Target Q values: r + gamma * max_a Q_target(s', a)
        with torch.no_grad():
            next_q = self.target_net(next_states).max(dim=1)[0]
            target_q = rewards + (1 - dones) * self.gamma * next_q
        
        # Loss: Huber loss (smoother than MSE, more robust to outliers)
        loss = nn.functional.smooth_l1_loss(current_q, target_q)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(self.online_net.parameters(), max_norm=10.0)
        self.optimizer.step()
        
        # Update target network periodically
        if self.steps_done % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.online_net.state_dict())
        
        return loss.item()


def train_dqn(env_name="CartPole-v1", n_episodes=1000):
    """Complete DQN training loop."""
    import gymnasium as gym
    
    env = gym.make(env_name)
    state_shape = env.observation_space.shape
    n_actions = env.action_space.n
    
    agent = DQNAgent(state_shape, n_actions)
    
    episode_rewards = []
    
    for episode in range(n_episodes):
        state, _ = env.reset()
        total_reward = 0
        done = False
        
        while not done:
            action = agent.select_action(state)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            
            agent.replay_buffer.push(state, action, reward, next_state, done)
            loss = agent.train_step()
            
            state = next_state
            total_reward += reward
        
        episode_rewards.append(total_reward)
        
        if episode % 50 == 0:
            avg_reward = np.mean(episode_rewards[-50:])
            epsilon = agent.get_epsilon()
            print(f"Episode {episode}, Avg Reward: {avg_reward:.2f}, "
                  f"Epsilon: {epsilon:.3f}, Buffer: {len(agent.replay_buffer)}")
    
    return agent, episode_rewards
```

### 8.4 Double DQN

Standard DQN tends to overestimate Q-values because the max operation in the target is biased upward. Double DQN fixes this by using the online network to SELECT the best action, but the target network to EVALUATE it:

```python
# In the train_step method, replace the target calculation:

# Standard DQN target (overestimates):
# target_q = rewards + gamma * max_a Q_target(s', a)

# Double DQN target (more accurate):
with torch.no_grad():
    # Use ONLINE network to select the best next action
    best_next_actions = self.online_net(next_states).argmax(dim=1)
    
    # Use TARGET network to evaluate that action
    next_q = self.target_net(next_states).gather(1, best_next_actions.unsqueeze(1)).squeeze(1)
    
    target_q = rewards + (1 - dones) * self.gamma * next_q
```

### 8.5 Dueling DQN

Split Q(s, a) into two components:

$$Q(s, a) = V(s) + A(s, a) - \text{mean}_a A(s, a)$$

```python
class DuelingDQN(nn.Module):
    """
    Dueling DQN: separate value and advantage streams.
    
    This helps because in many states, the VALUE of the state
    matters more than the specific action taken. The dueling
    architecture can learn this.
    """
    def __init__(self, input_shape, n_actions):
        super().__init__()
        
        self.features = nn.Sequential(
            nn.Linear(input_shape[0], 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU()
        )
        
        # Value stream: V(s) -- how good is this state?
        self.value_stream = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)  # Single value
        )
        
        # Advantage stream: A(s, a) -- how much better is action a?
        self.advantage_stream = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, n_actions)  # One advantage per action
        )
    
    def forward(self, x):
        features = self.features(x)
        
        value = self.value_stream(features)           # (batch, 1)
        advantages = self.advantage_stream(features)  # (batch, n_actions)
        
        # Q = V + A - mean(A)
        # Subtracting mean ensures identifiability
        q_values = value + advantages - advantages.mean(dim=1, keepdim=True)
        
        return q_values
```

---

## 9. Policy Gradient Methods

Instead of learning Q-values and deriving a policy, policy gradient methods directly learn the policy parameters by gradient ascent on expected reward.

### 9.1 REINFORCE Algorithm

The simplest policy gradient method. Also called "Monte Carlo Policy Gradient."

```python
import torch
import torch.nn as nn
import torch.optim as optim
import gymnasium as gym
import numpy as np

class PolicyNetwork(nn.Module):
    """A simple policy network for discrete actions."""
    def __init__(self, state_dim, action_dim, hidden_dim=128):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
        )
    
    def forward(self, state):
        logits = self.network(state)
        return torch.distributions.Categorical(logits=logits)


def reinforce(env_name="CartPole-v1", n_episodes=2000, gamma=0.99, lr=1e-3):
    """
    REINFORCE algorithm (Monte Carlo Policy Gradient).
    
    The policy gradient theorem tells us:
    
    grad J(theta) = E[sum_t grad log pi(a_t|s_t) * G_t]
    
    where G_t is the return from time t onward.
    
    Intuition: increase the probability of actions that led to high returns,
    decrease the probability of actions that led to low returns.
    """
    env = gym.make(env_name)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    policy = PolicyNetwork(state_dim, action_dim)
    optimizer = optim.Adam(policy.parameters(), lr=lr)
    
    episode_rewards = []
    
    for episode in range(n_episodes):
        state, _ = env.reset()
        
        log_probs = []
        rewards = []
        
        done = False
        while not done:
            state_tensor = torch.FloatTensor(state)
            dist = policy(state_tensor)
            action = dist.sample()
            log_prob = dist.log_prob(action)
            
            next_state, reward, terminated, truncated, _ = env.step(action.item())
            done = terminated or truncated
            
            log_probs.append(log_prob)
            rewards.append(reward)
            
            state = next_state
        
        # Compute returns (discounted cumulative rewards from each timestep)
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + gamma * G
            returns.insert(0, G)
        
        returns = torch.tensor(returns, dtype=torch.float32)
        
        # Normalize returns (reduces variance significantly)
        if len(returns) > 1:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)
        
        # Policy gradient loss
        # We want to MAXIMIZE expected return, so we MINIMIZE -return
        loss = 0
        for log_prob, G in zip(log_probs, returns):
            loss -= log_prob * G
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_reward = sum(rewards)
        episode_rewards.append(total_reward)
        
        if episode % 100 == 0:
            avg = np.mean(episode_rewards[-100:])
            print(f"Episode {episode}, Avg Reward: {avg:.2f}")
    
    return policy, episode_rewards
```

### 9.2 REINFORCE with Baseline

The raw REINFORCE has high variance. Adding a baseline (an estimate of V(s)) reduces variance without introducing bias:

```python
class PolicyWithBaseline(nn.Module):
    """Policy network with a value head (baseline)."""
    def __init__(self, state_dim, action_dim, hidden_dim=128):
        super().__init__()
        
        # Shared backbone
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
        )
        
        # Policy head
        self.policy_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
        )
        
        # Value head (baseline)
        self.value_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
    
    def forward(self, state):
        shared_features = self.shared(state)
        
        logits = self.policy_head(shared_features)
        value = self.value_head(shared_features)
        
        dist = torch.distributions.Categorical(logits=logits)
        return dist, value


def reinforce_with_baseline(env_name="CartPole-v1", n_episodes=2000, gamma=0.99):
    env = gym.make(env_name)
    model = PolicyWithBaseline(env.observation_space.shape[0], env.action_space.n)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    for episode in range(n_episodes):
        state, _ = env.reset()
        
        log_probs = []
        values = []
        rewards = []
        
        done = False
        while not done:
            state_tensor = torch.FloatTensor(state)
            dist, value = model(state_tensor)
            action = dist.sample()
            
            next_state, reward, terminated, truncated, _ = env.step(action.item())
            done = terminated or truncated
            
            log_probs.append(dist.log_prob(action))
            values.append(value.squeeze())
            rewards.append(reward)
            
            state = next_state
        
        # Compute returns
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + gamma * G
            returns.insert(0, G)
        returns = torch.tensor(returns, dtype=torch.float32)
        
        # Advantage = Return - Baseline(V)
        values_tensor = torch.stack(values)
        advantages = returns - values_tensor.detach()  # detach baseline from policy loss
        
        # Normalize advantages
        if len(advantages) > 1:
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Policy loss: -log_prob * advantage
        policy_loss = -(torch.stack(log_probs) * advantages).mean()
        
        # Value loss: MSE between predicted values and actual returns
        value_loss = nn.functional.mse_loss(values_tensor, returns)
        
        # Total loss
        loss = policy_loss + 0.5 * value_loss
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    return model
```

---

## 10. Actor-Critic Methods

Actor-Critic methods combine the best of policy gradient (the Actor) and value-based methods (the Critic):

- **Actor**: The policy network that selects actions
- **Critic**: The value network that evaluates how good the actions are

### 10.1 Advantage Actor-Critic (A2C)

```python
class ActorCritic(nn.Module):
    """
    Actor-Critic network with shared feature extraction.
    
    Actor: outputs action distribution (policy)
    Critic: outputs state value V(s)
    """
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super().__init__()
        
        # Shared feature extractor
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        
        # Actor head (policy)
        self.actor = nn.Linear(hidden_dim, action_dim)
        
        # Critic head (value)
        self.critic = nn.Linear(hidden_dim, 1)
    
    def forward(self, state):
        features = self.shared(state)
        
        action_logits = self.actor(features)
        value = self.critic(features)
        
        return action_logits, value
    
    def get_action(self, state):
        logits, value = self.forward(state)
        dist = torch.distributions.Categorical(logits=logits)
        action = dist.sample()
        return action, dist.log_prob(action), dist.entropy(), value


def train_a2c(env_name="CartPole-v1", n_steps_per_update=5, n_updates=10000, 
              gamma=0.99, lr=7e-4, entropy_coef=0.01, value_coef=0.5):
    """
    A2C (Advantage Actor-Critic) training.
    
    Unlike REINFORCE which waits for the entire episode,
    A2C updates every n_steps using TD bootstrapping.
    
    The advantage is estimated using TD residual:
    A(s, a) = r + gamma * V(s') - V(s)
    
    Or with n-step returns:
    A(s, a) = r_0 + gamma*r_1 + ... + gamma^n*V(s_n) - V(s)
    """
    env = gym.make(env_name)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    model = ActorCritic(state_dim, action_dim)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    state, _ = env.reset()
    episode_reward = 0
    episode_rewards = []
    
    for update in range(n_updates):
        # Collect n_steps of experience
        states = []
        actions = []
        rewards = []
        log_probs = []
        values = []
        dones = []
        entropies = []
        
        for step in range(n_steps_per_update):
            state_tensor = torch.FloatTensor(state)
            action, log_prob, entropy, value = model.get_action(state_tensor)
            
            next_state, reward, terminated, truncated, _ = env.step(action.item())
            done = terminated or truncated
            
            states.append(state_tensor)
            actions.append(action)
            rewards.append(reward)
            log_probs.append(log_prob)
            values.append(value.squeeze())
            dones.append(done)
            entropies.append(entropy)
            
            episode_reward += reward
            
            if done:
                episode_rewards.append(episode_reward)
                episode_reward = 0
                state, _ = env.reset()
            else:
                state = next_state
        
        # Bootstrap value for the last state
        with torch.no_grad():
            _, next_value = model(torch.FloatTensor(state))
            next_value = next_value.squeeze()
        
        # Compute returns and advantages using GAE (Generalized Advantage Estimation)
        returns = []
        advantages = []
        R = next_value
        
        for t in reversed(range(n_steps_per_update)):
            if dones[t]:
                R = 0
            R = rewards[t] + gamma * R
            advantage = R - values[t].detach()
            returns.append(R)
            advantages.append(advantage)
        
        returns.reverse()
        advantages.reverse()
        
        returns = torch.tensor(returns, dtype=torch.float32)
        advantages = torch.stack(advantages)
        
        # Normalize advantages
        if len(advantages) > 1:
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Compute losses
        log_probs_tensor = torch.stack(log_probs)
        values_tensor = torch.stack(values)
        entropies_tensor = torch.stack(entropies)
        
        # Policy loss (actor): maximize advantage-weighted log probability
        policy_loss = -(log_probs_tensor * advantages).mean()
        
        # Value loss (critic): minimize prediction error
        value_loss = nn.functional.mse_loss(values_tensor, returns)
        
        # Entropy bonus: encourage exploration
        entropy_loss = -entropies_tensor.mean()
        
        # Total loss
        loss = policy_loss + value_coef * value_loss + entropy_coef * entropy_loss
        
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        optimizer.step()
        
        if update % 500 == 0 and episode_rewards:
            avg = np.mean(episode_rewards[-50:])
            print(f"Update {update}, Avg Reward: {avg:.2f}")
    
    return model
```

---

## 11. Proximal Policy Optimization (PPO)

PPO (Schulman et al., 2017) is arguably the most popular RL algorithm today. It is used to train ChatGPT/Claude (via RLHF), robotic controllers, and game agents. PPO improves upon A2C by preventing too-large policy updates.

### 11.1 The Problem PPO Solves

In policy gradient methods, the gradient update can change the policy dramatically in a single step. This causes instability -- a good policy can be destroyed by a single bad update. PPO prevents this by clipping the policy update.

### 11.2 PPO-Clip Implementation

```python
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import gymnasium as gym

class PPONetwork(nn.Module):
    """
    PPO uses separate actor and critic networks.
    Can also use shared backbone with separate heads.
    """
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        super().__init__()
        
        # Actor (policy)
        self.actor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, action_dim),
        )
        
        # Critic (value function)
        self.critic = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
        )
        
        # Initialize weights
        self.apply(self._init_weights)
    
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.orthogonal_(module.weight, gain=np.sqrt(2))
            nn.init.constant_(module.bias, 0.0)
    
    def get_value(self, state):
        return self.critic(state)
    
    def get_action_and_value(self, state, action=None):
        logits = self.actor(state)
        dist = torch.distributions.Categorical(logits=logits)
        
        if action is None:
            action = dist.sample()
        
        return action, dist.log_prob(action), dist.entropy(), self.critic(state)


class PPOAgent:
    """
    Complete PPO-Clip implementation.
    """
    def __init__(
        self,
        state_dim,
        action_dim,
        lr=3e-4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_epsilon=0.2,
        value_coef=0.5,
        entropy_coef=0.01,
        max_grad_norm=0.5,
        n_epochs=4,           # Number of optimization epochs per batch
        batch_size=64,
        n_steps=2048,         # Steps of experience to collect before update
    ):
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.max_grad_norm = max_grad_norm
        self.n_epochs = n_epochs
        self.batch_size = batch_size
        self.n_steps = n_steps
        
        self.network = PPONetwork(state_dim, action_dim)
        self.optimizer = optim.Adam(self.network.parameters(), lr=lr, eps=1e-5)
    
    def compute_gae(self, rewards, values, dones, next_value):
        """
        Generalized Advantage Estimation (GAE).
        
        Computes advantages using a weighted combination of n-step TD errors:
        
        A_t = delta_t + (gamma * lambda) * delta_{t+1} + (gamma * lambda)^2 * delta_{t+2} + ...
        
        where delta_t = r_t + gamma * V(s_{t+1}) - V(s_t)
        
        lambda = 0: Just TD(0) advantage (low variance, high bias)
        lambda = 1: Monte Carlo advantage (high variance, low bias)
        lambda = 0.95: A good compromise (used in practice)
        """
        advantages = np.zeros_like(rewards)
        last_gae = 0
        
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_non_terminal = 1.0 - dones[t]
                next_val = next_value
            else:
                next_non_terminal = 1.0 - dones[t]
                next_val = values[t + 1]
            
            # TD error: r + gamma * V(s') - V(s)
            delta = rewards[t] + self.gamma * next_val * next_non_terminal - values[t]
            
            # GAE: accumulate discounted deltas
            advantages[t] = last_gae = delta + self.gamma * self.gae_lambda * next_non_terminal * last_gae
        
        returns = advantages + values
        return advantages, returns
    
    def update(self, states, actions, old_log_probs, returns, advantages):
        """
        PPO update: multiple epochs over the collected batch.
        
        The key insight of PPO-Clip:
        
        L_clip = min(ratio * A, clip(ratio, 1-eps, 1+eps) * A)
        
        where ratio = pi_new(a|s) / pi_old(a|s)
        
        This prevents the policy from changing too much:
        - If the ratio is within [1-eps, 1+eps], the gradient flows normally
        - If the ratio goes outside, the gradient is clipped
        
        Example with eps=0.2:
        - ratio = 1.5 and A > 0: clip to 1.2 (prevent too much increase)
        - ratio = 0.5 and A < 0: clip to 0.8 (prevent too much decrease)
        """
        dataset_size = len(states)
        
        total_policy_loss = 0
        total_value_loss = 0
        total_entropy = 0
        n_updates = 0
        
        for epoch in range(self.n_epochs):
            # Shuffle and create mini-batches
            indices = np.random.permutation(dataset_size)
            
            for start in range(0, dataset_size, self.batch_size):
                end = start + self.batch_size
                batch_indices = indices[start:end]
                
                batch_states = torch.FloatTensor(states[batch_indices])
                batch_actions = torch.LongTensor(actions[batch_indices])
                batch_old_log_probs = torch.FloatTensor(old_log_probs[batch_indices])
                batch_returns = torch.FloatTensor(returns[batch_indices])
                batch_advantages = torch.FloatTensor(advantages[batch_indices])
                
                # Normalize advantages (per mini-batch)
                batch_advantages = (batch_advantages - batch_advantages.mean()) / (batch_advantages.std() + 1e-8)
                
                # Get new action probabilities and values
                _, new_log_probs, entropy, new_values = self.network.get_action_and_value(
                    batch_states, batch_actions
                )
                
                # Policy ratio: pi_new / pi_old
                ratio = torch.exp(new_log_probs - batch_old_log_probs)
                
                # Clipped surrogate objective
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1.0 - self.clip_epsilon, 1.0 + self.clip_epsilon) * batch_advantages
                policy_loss = -torch.min(surr1, surr2).mean()
                
                # Value loss (also clipped for stability)
                value_loss = nn.functional.mse_loss(new_values.squeeze(), batch_returns)
                
                # Entropy bonus
                entropy_loss = -entropy.mean()
                
                # Total loss
                loss = policy_loss + self.value_coef * value_loss + self.entropy_coef * entropy_loss
                
                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.network.parameters(), self.max_grad_norm)
                self.optimizer.step()
                
                total_policy_loss += policy_loss.item()
                total_value_loss += value_loss.item()
                total_entropy += -entropy_loss.item()
                n_updates += 1
        
        return {
            'policy_loss': total_policy_loss / n_updates,
            'value_loss': total_value_loss / n_updates,
            'entropy': total_entropy / n_updates,
        }


def train_ppo(env_name="CartPole-v1", total_timesteps=100000):
    """Complete PPO training loop."""
    env = gym.make(env_name)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    
    agent = PPOAgent(state_dim, action_dim)
    
    state, _ = env.reset()
    episode_reward = 0
    episode_rewards = []
    timestep = 0
    
    while timestep < total_timesteps:
        # Collect experience
        states = []
        actions = []
        log_probs = []
        rewards = []
        dones = []
        values = []
        
        for step in range(agent.n_steps):
            state_tensor = torch.FloatTensor(state)
            
            with torch.no_grad():
                action, log_prob, _, value = agent.network.get_action_and_value(state_tensor)
            
            next_state, reward, terminated, truncated, _ = env.step(action.item())
            done = terminated or truncated
            
            states.append(state)
            actions.append(action.item())
            log_probs.append(log_prob.item())
            rewards.append(reward)
            dones.append(float(done))
            values.append(value.item())
            
            episode_reward += reward
            timestep += 1
            
            if done:
                episode_rewards.append(episode_reward)
                episode_reward = 0
                state, _ = env.reset()
            else:
                state = next_state
        
        # Compute advantages using GAE
        with torch.no_grad():
            next_value = agent.network.get_value(torch.FloatTensor(state)).item()
        
        advantages, returns = agent.compute_gae(
            np.array(rewards), np.array(values), np.array(dones), next_value
        )
        
        # PPO update
        metrics = agent.update(
            np.array(states), np.array(actions), np.array(log_probs),
            returns, advantages
        )
        
        if episode_rewards:
            avg = np.mean(episode_rewards[-20:])
            print(f"Timestep {timestep}, Avg Reward: {avg:.2f}, "
                  f"Policy Loss: {metrics['policy_loss']:.4f}")
    
    return agent
```

### 11.3 PPO for Continuous Actions

```python
class ContinuousPPONetwork(nn.Module):
    """PPO network for continuous action spaces (e.g., robotics)."""
    
    def __init__(self, state_dim, action_dim, hidden_dim=64):
        super().__init__()
        
        self.actor_backbone = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
        )
        
        # Output: mean of Gaussian distribution for each action dimension
        self.actor_mean = nn.Linear(hidden_dim, action_dim)
        
        # Log standard deviation (learnable parameter, not state-dependent)
        self.log_std = nn.Parameter(torch.zeros(action_dim))
        
        self.critic = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
        )
    
    def get_action_and_value(self, state, action=None):
        features = self.actor_backbone(state)
        mean = self.actor_mean(features)
        std = self.log_std.exp()
        
        # Gaussian distribution for continuous actions
        dist = torch.distributions.Normal(mean, std)
        
        if action is None:
            action = dist.sample()
        
        # Sum log probs across action dimensions (independent Gaussians)
        log_prob = dist.log_prob(action).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        value = self.critic(state)
        
        return action, log_prob, entropy, value
```

---

## 12. Soft Actor-Critic (SAC)

SAC (Haarnoja et al., 2018) is a state-of-the-art off-policy algorithm for continuous control. It maximizes both expected return AND entropy (encourages exploration):

$$J(\pi) = \sum_t E\left[r_t + \alpha \cdot H(\pi(\cdot|s_t))\right]$$

where H is entropy and alpha is the temperature parameter.

```python
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class SACActorNetwork(nn.Module):
    """
    SAC actor outputs a squashed Gaussian distribution.
    The action is sampled from Normal(mu, sigma) then passed through tanh
    to bound it to [-1, 1].
    """
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super().__init__()
        
        self.backbone = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        
        self.mean_head = nn.Linear(hidden_dim, action_dim)
        self.log_std_head = nn.Linear(hidden_dim, action_dim)
        
        self.LOG_STD_MIN = -20
        self.LOG_STD_MAX = 2
    
    def forward(self, state):
        features = self.backbone(state)
        mean = self.mean_head(features)
        log_std = self.log_std_head(features)
        log_std = torch.clamp(log_std, self.LOG_STD_MIN, self.LOG_STD_MAX)
        return mean, log_std
    
    def sample(self, state):
        """Sample an action using the reparameterization trick."""
        mean, log_std = self.forward(state)
        std = log_std.exp()
        
        # Reparameterization: action = tanh(mean + std * noise)
        normal_dist = torch.distributions.Normal(mean, std)
        x = normal_dist.rsample()  # rsample = differentiable sampling
        action = torch.tanh(x)
        
        # Log probability (with tanh correction)
        log_prob = normal_dist.log_prob(x) - torch.log(1 - action.pow(2) + 1e-6)
        log_prob = log_prob.sum(dim=-1, keepdim=True)
        
        return action, log_prob


class SACCriticNetwork(nn.Module):
    """
    SAC uses TWO critic networks (to reduce overestimation).
    Each takes (state, action) and outputs a Q-value.
    """
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super().__init__()
        
        # Q1
        self.q1 = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
        
        # Q2
        self.q2 = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )
    
    def forward(self, state, action):
        sa = torch.cat([state, action], dim=-1)
        return self.q1(sa), self.q2(sa)


class SACAgent:
    """Complete Soft Actor-Critic agent."""
    
    def __init__(
        self,
        state_dim,
        action_dim,
        lr=3e-4,
        gamma=0.99,
        tau=0.005,         # Soft target update rate
        alpha=0.2,         # Entropy temperature (or auto-tuned)
        auto_alpha=True,
        buffer_size=1000000,
        batch_size=256,
        device="cuda"
    ):
        self.device = torch.device(device)
        self.gamma = gamma
        self.tau = tau
        self.batch_size = batch_size
        self.action_dim = action_dim
        
        # Networks
        self.actor = SACActorNetwork(state_dim, action_dim).to(self.device)
        self.critic = SACCriticNetwork(state_dim, action_dim).to(self.device)
        self.critic_target = SACCriticNetwork(state_dim, action_dim).to(self.device)
        self.critic_target.load_state_dict(self.critic.state_dict())
        
        # Optimizers
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=lr)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=lr)
        
        # Auto-tuning alpha (entropy temperature)
        self.auto_alpha = auto_alpha
        if auto_alpha:
            self.target_entropy = -action_dim  # Heuristic: -dim(A)
            self.log_alpha = torch.zeros(1, requires_grad=True, device=self.device)
            self.alpha_optimizer = optim.Adam([self.log_alpha], lr=lr)
            self.alpha = self.log_alpha.exp().item()
        else:
            self.alpha = alpha
        
        # Replay buffer
        self.replay_buffer = ReplayBuffer(capacity=buffer_size)
    
    def select_action(self, state, deterministic=False):
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            if deterministic:
                mean, _ = self.actor(state_tensor)
                action = torch.tanh(mean)
            else:
                action, _ = self.actor.sample(state_tensor)
        
        return action.cpu().numpy().flatten()
    
    def train_step(self):
        if len(self.replay_buffer) < self.batch_size:
            return {}
        
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.FloatTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).unsqueeze(1).to(self.device)
        
        # ---- Update Critic ----
        with torch.no_grad():
            # Sample next action from current policy
            next_action, next_log_prob = self.actor.sample(next_states)
            
            # Target Q-value (use minimum of two targets)
            target_q1, target_q2 = self.critic_target(next_states, next_action)
            target_q = torch.min(target_q1, target_q2) - self.alpha * next_log_prob
            target_q = rewards + (1 - dones) * self.gamma * target_q
        
        # Current Q-values
        current_q1, current_q2 = self.critic(states, actions)
        
        critic_loss = nn.functional.mse_loss(current_q1, target_q) + \
                      nn.functional.mse_loss(current_q2, target_q)
        
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()
        
        # ---- Update Actor ----
        new_action, log_prob = self.actor.sample(states)
        q1, q2 = self.critic(states, new_action)
        min_q = torch.min(q1, q2)
        
        # Actor loss: maximize Q - alpha * log_prob
        actor_loss = (self.alpha * log_prob - min_q).mean()
        
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()
        
        # ---- Update Alpha (temperature) ----
        if self.auto_alpha:
            alpha_loss = -(self.log_alpha.exp() * (log_prob + self.target_entropy).detach()).mean()
            
            self.alpha_optimizer.zero_grad()
            alpha_loss.backward()
            self.alpha_optimizer.step()
            
            self.alpha = self.log_alpha.exp().item()
        
        # ---- Soft Update Target Network ----
        for param, target_param in zip(self.critic.parameters(), self.critic_target.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
        
        return {
            'critic_loss': critic_loss.item(),
            'actor_loss': actor_loss.item(),
            'alpha': self.alpha,
        }
```

---

## 13. Model-Based Reinforcement Learning

Model-free methods (DQN, PPO, SAC) require millions of interactions to learn. Model-based RL learns a model of the environment (transition dynamics) and uses it to plan or generate imagined experience.

### 13.1 Learning a World Model

```python
class WorldModel(nn.Module):
    """
    Learn the environment dynamics: given (state, action), predict (next_state, reward).
    
    This is essentially supervised learning on collected experience.
    """
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super().__init__()
        
        # Transition model: (s, a) -> s'
        self.transition = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, state_dim)
        )
        
        # Reward model: (s, a) -> r
        self.reward = nn.Sequential(
            nn.Linear(state_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
    
    def forward(self, state, action):
        sa = torch.cat([state, action], dim=-1)
        next_state = state + self.transition(sa)  # Predict residual (change)
        reward = self.reward(sa)
        return next_state, reward


def model_based_planning(world_model, current_state, action_dim, horizon=15, n_candidates=1000):
    """
    Random Shooting: sample random action sequences and pick the best one.
    This is a simple planning method used with learned world models.
    """
    best_reward = float('-inf')
    best_actions = None
    
    for _ in range(n_candidates):
        # Random action sequence
        actions = torch.rand(horizon, action_dim) * 2 - 1  # Actions in [-1, 1]
        
        # Simulate using world model
        state = current_state.clone()
        total_reward = 0
        
        with torch.no_grad():
            for t in range(horizon):
                next_state, reward = world_model(state.unsqueeze(0), actions[t].unsqueeze(0))
                total_reward += reward.item()
                state = next_state.squeeze(0)
        
        if total_reward > best_reward:
            best_reward = total_reward
            best_actions = actions
    
    # Return just the first action (re-plan at every step)
    return best_actions[0]


class DreamerWorldModel(nn.Module):
    """
    Dreamer-style world model with:
    1. Encoder: observation -> latent state
    2. Recurrent state-space model (RSSM): latent dynamics
    3. Decoder: latent state -> predicted observation
    4. Reward predictor: latent state -> reward
    
    This learns a compact latent representation of the environment
    and can "dream" (imagine) trajectories for planning.
    """
    def __init__(self, obs_dim, action_dim, latent_dim=200, hidden_dim=200):
        super().__init__()
        
        # Encoder: o -> z (posterior, uses actual observation)
        self.encoder = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim * 2)  # Mean and log_std
        )
        
        # Prior: predict z from h (deterministic state)
        self.prior = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim * 2)
        )
        
        # Recurrent model: (h, z, a) -> h'
        self.rnn = nn.GRUCell(latent_dim + action_dim, hidden_dim)
        
        # Decoder: (h, z) -> o (reconstruct observation)
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim + latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, obs_dim)
        )
        
        # Reward predictor: (h, z) -> r
        self.reward_pred = nn.Sequential(
            nn.Linear(hidden_dim + latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
    
    def imagine(self, initial_h, actions):
        """
        'Dream' a trajectory using the learned model without real observations.
        
        initial_h: (batch, hidden_dim) initial recurrent state
        actions: (batch, T, action_dim) action sequence
        
        Returns imagined observations, rewards
        """
        h = initial_h
        imagined_rewards = []
        imagined_states = []
        
        for t in range(actions.shape[1]):
            # Get prior (no observation available in imagination)
            prior_params = self.prior(h)
            mean, log_std = prior_params.chunk(2, dim=-1)
            z = mean + torch.exp(log_std) * torch.randn_like(mean)
            
            # Predict reward
            hz = torch.cat([h, z], dim=-1)
            reward = self.reward_pred(hz)
            
            # Next recurrent state
            rnn_input = torch.cat([z, actions[:, t]], dim=-1)
            h = self.rnn(rnn_input, h)
            
            imagined_rewards.append(reward)
            imagined_states.append(hz)
        
        return torch.stack(imagined_states, dim=1), torch.stack(imagined_rewards, dim=1)
```

---

## 14. Multi-Agent Reinforcement Learning

In many real-world scenarios, multiple agents interact in the same environment.

```python
class MultiAgentEnvironment:
    """
    Simple multi-agent environment (Predator-Prey).
    
    Predators try to catch the prey. Prey tries to escape.
    """
    def __init__(self, n_predators=3, grid_size=10):
        self.n_predators = n_predators
        self.grid_size = grid_size
    
    def reset(self):
        # Random initial positions
        self.predator_positions = [
            [np.random.randint(0, self.grid_size), np.random.randint(0, self.grid_size)]
            for _ in range(self.n_predators)
        ]
        self.prey_position = [np.random.randint(0, self.grid_size), np.random.randint(0, self.grid_size)]
        
        return self._get_observations()
    
    def _get_observations(self):
        """Each agent sees its own position and all others' positions."""
        observations = {}
        
        for i in range(self.n_predators):
            obs = np.array(self.predator_positions[i] + self.prey_position, dtype=np.float32)
            observations[f"predator_{i}"] = obs / self.grid_size  # Normalize
        
        prey_obs = np.array(self.prey_position, dtype=np.float32)
        for pos in self.predator_positions:
            prey_obs = np.concatenate([prey_obs, np.array(pos, dtype=np.float32)])
        observations["prey"] = prey_obs / self.grid_size
        
        return observations
    
    def step(self, actions):
        """
        actions: dict mapping agent_id -> action (0=up, 1=down, 2=left, 3=right)
        Returns: observations, rewards, dones, infos
        """
        # Move predators
        for i in range(self.n_predators):
            action = actions[f"predator_{i}"]
            self._move_agent(self.predator_positions[i], action)
        
        # Move prey (can be policy-controlled or random)
        self._move_agent(self.prey_position, actions.get("prey", np.random.randint(4)))
        
        # Check if caught
        caught = any(
            pos == self.prey_position for pos in self.predator_positions
        )
        
        # Rewards
        rewards = {}
        for i in range(self.n_predators):
            dist = abs(self.predator_positions[i][0] - self.prey_position[0]) + \
                   abs(self.predator_positions[i][1] - self.prey_position[1])
            rewards[f"predator_{i}"] = 10.0 if caught else -0.1 * dist
        rewards["prey"] = -10.0 if caught else 0.1
        
        done = caught
        
        return self._get_observations(), rewards, done, {}
    
    def _move_agent(self, position, action):
        if action == 0: position[1] = min(position[1] + 1, self.grid_size - 1)
        elif action == 1: position[1] = max(position[1] - 1, 0)
        elif action == 2: position[0] = max(position[0] - 1, 0)
        elif action == 3: position[0] = min(position[0] + 1, self.grid_size - 1)
```

### Independent PPO for Multi-Agent

```python
def train_multi_agent_ppo(env, n_episodes=10000):
    """
    Independent PPO: train a separate PPO agent for each agent.
    Simple but effective baseline for multi-agent RL.
    """
    agents = {}
    
    # Create one PPO agent per entity
    for agent_id in ["predator_0", "predator_1", "predator_2", "prey"]:
        obs_dim = 8 if "predator" in agent_id else 8
        agents[agent_id] = PPOAgent(state_dim=obs_dim, action_dim=4)
    
    for episode in range(n_episodes):
        obs = env.reset()
        done = False
        episode_rewards = {agent_id: 0 for agent_id in agents}
        
        while not done:
            actions = {}
            for agent_id, agent in agents.items():
                state_tensor = torch.FloatTensor(obs[agent_id])
                with torch.no_grad():
                    action, _, _, _ = agent.network.get_action_and_value(state_tensor)
                actions[agent_id] = action.item()
            
            next_obs, rewards, done, _ = env.step(actions)
            
            # Store transitions for each agent
            for agent_id in agents:
                # (would store in agent's buffer for PPO update)
                episode_rewards[agent_id] += rewards[agent_id]
            
            obs = next_obs
        
        if episode % 500 == 0:
            print(f"Episode {episode}, Rewards: {episode_rewards}")
```

---

## 15. Reward Shaping and Curriculum Learning

### 15.1 Reward Shaping

Designing good reward functions is one of the hardest parts of RL. Poor rewards lead to poor or unintended behavior.

```python
def naive_reward(state, goal):
    """
    Sparse reward: only +1 when goal is reached.
    Problem: agent gets no signal until it randomly reaches the goal,
    which may never happen in complex environments.
    """
    if np.allclose(state, goal, atol=0.1):
        return 1.0
    return 0.0


def shaped_reward(state, goal, prev_distance=None):
    """
    Dense, shaped reward: provides continuous feedback.
    
    Guidelines for reward shaping:
    1. Reward progress toward the goal (distance reduction)
    2. Penalize undesired behaviors (collisions, energy waste)
    3. Keep rewards bounded (avoid reward scale issues)
    4. Align rewards with actual objective (avoid reward hacking)
    """
    current_distance = np.linalg.norm(state - goal)
    
    reward = 0.0
    
    # Reward for reaching the goal
    if current_distance < 0.1:
        reward += 100.0
    
    # Reward for getting closer (potential-based shaping)
    if prev_distance is not None:
        reward += (prev_distance - current_distance) * 10.0
    
    # Small step penalty (encourages efficiency)
    reward -= 0.01
    
    return reward


def potential_based_shaping(state, next_state, gamma=0.99):
    """
    Potential-based reward shaping (Ng et al., 1999).
    
    This is the only form of reward shaping guaranteed to not change
    the optimal policy:
    
    F(s, s') = gamma * Phi(s') - Phi(s)
    
    where Phi is a potential function. The shaped reward R' = R + F
    has the same optimal policy as the original reward R.
    """
    def potential(state):
        """Potential function: negative distance to goal."""
        goal = np.array([5.0, 5.0])
        return -np.linalg.norm(state - goal)
    
    return gamma * potential(next_state) - potential(state)
```

### 15.2 Curriculum Learning

Start with easy tasks and gradually increase difficulty:

```python
class CurriculumScheduler:
    """
    Automatically adjust task difficulty based on agent performance.
    """
    def __init__(self, min_difficulty=0.0, max_difficulty=1.0, success_threshold=0.7):
        self.difficulty = min_difficulty
        self.min_difficulty = min_difficulty
        self.max_difficulty = max_difficulty
        self.success_threshold = success_threshold
        self.recent_successes = []
        self.window_size = 100
    
    def get_task(self, base_env):
        """Generate a task at the current difficulty level."""
        # Example: adjust goal distance based on difficulty
        max_distance = 1.0 + self.difficulty * 9.0  # 1 to 10 units
        
        goal = np.random.randn(2) * max_distance
        base_env.set_goal(goal)
        
        return base_env
    
    def report_result(self, success):
        """Report whether the agent succeeded on the latest task."""
        self.recent_successes.append(float(success))
        
        if len(self.recent_successes) > self.window_size:
            self.recent_successes.pop(0)
        
        # Adjust difficulty based on success rate
        if len(self.recent_successes) >= self.window_size:
            success_rate = np.mean(self.recent_successes)
            
            if success_rate > self.success_threshold:
                self.difficulty = min(self.max_difficulty, self.difficulty + 0.05)
                self.recent_successes = []
                print(f"Difficulty increased to {self.difficulty:.2f}")
            elif success_rate < 0.3:
                self.difficulty = max(self.min_difficulty, self.difficulty - 0.05)
                self.recent_successes = []
                print(f"Difficulty decreased to {self.difficulty:.2f}")
```

---

## 16. RLHF (RL from Human Feedback)

RLHF is how large language models like ChatGPT are aligned with human preferences. The process has three phases:

### Phase 1: Supervised Fine-Tuning (SFT)

Fine-tune a pre-trained LLM on high-quality demonstration data.

### Phase 2: Train a Reward Model

Collect human preferences (which of two outputs is better) and train a reward model:

```python
class RewardModel(nn.Module):
    """
    Reward model for RLHF.
    
    Takes a (prompt, response) pair and outputs a scalar reward.
    Trained on human preference comparisons.
    """
    def __init__(self, base_model):
        super().__init__()
        self.base_model = base_model  # Pre-trained LLM (frozen or fine-tuned)
        self.reward_head = nn.Linear(base_model.config.hidden_size, 1)
    
    def forward(self, input_ids, attention_mask):
        """
        Compute reward for a sequence.
        Uses the last token's hidden state as the representation.
        """
        outputs = self.base_model(input_ids, attention_mask=attention_mask)
        last_hidden = outputs.last_hidden_state[:, -1, :]  # Last token
        reward = self.reward_head(last_hidden)
        return reward


def train_reward_model(reward_model, preference_dataset, n_epochs=3, lr=1e-5):
    """
    Train reward model on human preference pairs.
    
    Each example in the dataset has:
    - prompt: the input text
    - chosen: the preferred response
    - rejected: the less preferred response
    
    We train the reward model using the Bradley-Terry preference model:
    P(chosen > rejected) = sigmoid(R(chosen) - R(rejected))
    """
    optimizer = optim.AdamW(reward_model.parameters(), lr=lr)
    
    for epoch in range(n_epochs):
        total_loss = 0
        n_correct = 0
        n_total = 0
        
        for batch in preference_dataset:
            # Get rewards for chosen and rejected responses
            reward_chosen = reward_model(
                batch['chosen_input_ids'],
                batch['chosen_attention_mask']
            )
            
            reward_rejected = reward_model(
                batch['rejected_input_ids'],
                batch['rejected_attention_mask']
            )
            
            # Bradley-Terry loss: -log sigmoid(R_chosen - R_rejected)
            loss = -torch.log(torch.sigmoid(reward_chosen - reward_rejected)).mean()
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            n_correct += (reward_chosen > reward_rejected).sum().item()
            n_total += len(reward_chosen)
        
        accuracy = n_correct / n_total
        print(f"Epoch {epoch}, Loss: {total_loss:.4f}, Accuracy: {accuracy:.2%}")
```

### Phase 3: PPO Fine-Tuning

Use PPO to fine-tune the LLM to maximize the reward model's score, with a KL penalty to prevent the model from deviating too far from the SFT model:

```python
def rlhf_ppo_step(
    policy_model,       # The LLM being trained
    ref_model,          # Frozen copy of SFT model (for KL constraint)
    reward_model,       # Trained reward model
    tokenizer,
    prompts,            # Batch of prompts
    kl_coef=0.1,        # KL penalty coefficient
    clip_epsilon=0.2,
    gamma=1.0,
    lr=1e-6
):
    """
    One PPO step for RLHF.
    
    The reward for each response is:
    R = reward_model(response) - kl_coef * KL(policy || reference)
    
    The KL term prevents the model from drifting too far from the
    original SFT model, which would lead to reward hacking
    (generating gibberish that gets high reward scores).
    """
    optimizer = optim.Adam(policy_model.parameters(), lr=lr)
    
    # Generate responses from the current policy
    with torch.no_grad():
        generated_ids = policy_model.generate(
            prompts,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
    
    # Compute log probabilities under current policy and reference policy
    policy_logprobs = compute_log_probs(policy_model, prompts, generated_ids)
    ref_logprobs = compute_log_probs(ref_model, prompts, generated_ids)
    
    # Per-token KL divergence
    kl_div = policy_logprobs - ref_logprobs
    
    # Reward from the reward model
    with torch.no_grad():
        rewards = reward_model(generated_ids, attention_mask=torch.ones_like(generated_ids))
    
    # Combine reward with KL penalty
    # Apply reward at the last token, KL penalty at every token
    total_rewards = rewards - kl_coef * kl_div.sum(dim=-1, keepdim=True)
    
    # Compute advantages (simplified -- in practice use GAE)
    advantages = total_rewards - total_rewards.mean()
    advantages = advantages / (advantages.std() + 1e-8)
    
    # PPO clipped objective
    old_logprobs = policy_logprobs.detach()
    ratio = torch.exp(policy_logprobs - old_logprobs)
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1 - clip_epsilon, 1 + clip_epsilon) * advantages
    policy_loss = -torch.min(surr1, surr2).mean()
    
    optimizer.zero_grad()
    policy_loss.backward()
    torch.nn.utils.clip_grad_norm_(policy_model.parameters(), max_norm=1.0)
    optimizer.step()
    
    return {
        'reward': rewards.mean().item(),
        'kl': kl_div.mean().item(),
        'policy_loss': policy_loss.item(),
    }
```

### Using TRL (Transformers Reinforcement Learning) Library

```python
# In practice, use the TRL library by Hugging Face for RLHF
from trl import PPOTrainer, PPOConfig, AutoModelForCausalLMWithValueHead
from transformers import AutoTokenizer

# Load model with value head
model = AutoModelForCausalLMWithValueHead.from_pretrained("gpt2")
ref_model = AutoModelForCausalLMWithValueHead.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer.pad_token = tokenizer.eos_token

# PPO config
ppo_config = PPOConfig(
    model_name="gpt2",
    learning_rate=1.41e-5,
    batch_size=256,
    mini_batch_size=16,
    gradient_accumulation_steps=1,
    ppo_epochs=4,
    kl_penalty="kl",
    init_kl_coef=0.2,
)

# Create trainer
ppo_trainer = PPOTrainer(
    config=ppo_config,
    model=model,
    ref_model=ref_model,
    tokenizer=tokenizer,
)

# Training loop
for batch in dataloader:
    queries = batch["input_ids"]
    
    # Generate responses
    response_tensors = ppo_trainer.generate(queries, max_new_tokens=128)
    
    # Compute rewards (from reward model)
    rewards = [reward_model(r) for r in response_tensors]
    
    # PPO step
    stats = ppo_trainer.step(queries, response_tensors, rewards)
    
    print(f"Reward: {stats['ppo/mean_scores']:.4f}, KL: {stats['objective/kl']:.4f}")
```

---

## 17. Practical RL with Gymnasium and Stable-Baselines3

### 17.1 Gymnasium (formerly OpenAI Gym)

```python
import gymnasium as gym

# Create an environment
env = gym.make("CartPole-v1", render_mode="human")

# Environment API
observation, info = env.reset(seed=42)
print(f"Observation space: {env.observation_space}")  # Box(-inf, inf, (4,))
print(f"Action space: {env.action_space}")            # Discrete(2)

# Run a random agent
total_reward = 0
done = False

while not done:
    action = env.action_space.sample()  # Random action
    observation, reward, terminated, truncated, info = env.step(action)
    total_reward += reward
    done = terminated or truncated

print(f"Total reward: {total_reward}")
env.close()
```

### 17.2 Stable-Baselines3

```python
# Install: pip install stable-baselines3[extra]

from stable_baselines3 import PPO, A2C, SAC, DQN, TD3
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback

# --- Simple Training ---

# Discrete action spaces
env = gym.make("CartPole-v1")
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100000)

# Evaluate
mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")

# Save and load
model.save("ppo_cartpole")
loaded_model = PPO.load("ppo_cartpole")


# --- Continuous action spaces ---
env = gym.make("Pendulum-v1")
model = SAC("MlpPolicy", env, verbose=1, learning_rate=3e-4)
model.learn(total_timesteps=100000)


# --- Vectorized environments (parallel) ---
vec_env = make_vec_env("CartPole-v1", n_envs=4)
model = PPO("MlpPolicy", vec_env, verbose=1)
model.learn(total_timesteps=100000)


# --- Custom hyperparameters ---
model = PPO(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.01,
    vf_coef=0.5,
    max_grad_norm=0.5,
    verbose=1,
    tensorboard_log="./tb_logs/"
)
model.learn(total_timesteps=500000)


# --- Callbacks for monitoring ---
eval_callback = EvalCallback(
    env,
    best_model_save_path="./best_model/",
    eval_freq=5000,
    n_eval_episodes=10,
    deterministic=True,
)

checkpoint_callback = CheckpointCallback(
    save_freq=10000,
    save_path="./checkpoints/",
    name_prefix="rl_model"
)

model.learn(
    total_timesteps=500000,
    callback=[eval_callback, checkpoint_callback]
)
```

### 17.3 Creating Custom Environments

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np

class CustomEnv(gym.Env):
    """
    Template for a custom Gymnasium environment.
    
    This example: a 1D navigation task.
    Agent starts at position 0, goal is at position 10.
    Action: continuous force in [-1, 1].
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}
    
    def __init__(self, render_mode=None):
        super().__init__()
        
        # Define action space: continuous force
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(1,), dtype=np.float32
        )
        
        # Define observation space: [position, velocity]
        self.observation_space = spaces.Box(
            low=np.array([-20.0, -5.0]),
            high=np.array([20.0, 5.0]),
            dtype=np.float32
        )
        
        self.goal_position = 10.0
        self.max_steps = 200
        self.render_mode = render_mode
    
    def reset(self, seed=None, options=None):
        """Reset the environment to initial state."""
        super().reset(seed=seed)
        
        self.position = 0.0
        self.velocity = 0.0
        self.step_count = 0
        
        observation = np.array([self.position, self.velocity], dtype=np.float32)
        info = {}
        
        return observation, info
    
    def step(self, action):
        """Take an action and return (observation, reward, terminated, truncated, info)."""
        force = float(action[0])
        
        # Physics update
        self.velocity += force * 0.1
        self.velocity = np.clip(self.velocity, -5.0, 5.0)
        self.position += self.velocity * 0.1
        self.step_count += 1
        
        # Observation
        observation = np.array([self.position, self.velocity], dtype=np.float32)
        
        # Reward
        distance = abs(self.position - self.goal_position)
        reward = -distance * 0.1  # Encourage getting close
        
        # Termination conditions
        terminated = distance < 0.5  # Reached goal
        truncated = self.step_count >= self.max_steps  # Time limit
        
        if terminated:
            reward += 100.0  # Bonus for reaching goal
        
        info = {"distance": distance}
        
        return observation, reward, terminated, truncated, info
    
    def render(self):
        """Render the environment (optional)."""
        if self.render_mode == "human":
            print(f"Position: {self.position:.2f}, Velocity: {self.velocity:.2f}")


# Register the custom environment
gym.register(
    id="CustomNav-v0",
    entry_point="my_envs:CustomEnv",
    max_episode_steps=200,
)

# Train with stable-baselines3
from stable_baselines3 import SAC

env = CustomEnv()
model = SAC("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100000)
```

---

## 18. Summary and Key Takeaways

1. **RL basics**: Agent, environment, state, action, reward, policy, value function. The goal is to learn a policy that maximizes cumulative discounted reward.

2. **MDPs**: The mathematical framework. Bellman equations provide the recursive structure that all RL algorithms exploit.

3. **Dynamic programming**: Works when the model is known. Policy iteration and value iteration find optimal policies.

4. **Monte Carlo**: Learn from complete episodes. No bootstrapping, high variance, no bias.

5. **TD Learning**: Learn from partial episodes via bootstrapping. Lower variance than MC, some bias.

6. **Q-Learning**: Off-policy TD control. Learns optimal Q directly. Forms the basis for DQN.

7. **DQN**: Deep Q-Networks scale Q-learning to complex state spaces using neural networks, replay buffers, and target networks.

8. **Policy gradients**: Directly optimize the policy using the gradient of expected return. REINFORCE is the simplest.

9. **Actor-Critic**: Combine policy gradient (actor) with value estimation (critic). A2C is the synchronous version.

10. **PPO**: The most widely used RL algorithm. Prevents destructive policy updates via clipping. Used in RLHF for LLMs.

11. **SAC**: State-of-the-art for continuous control. Maximizes return AND entropy.

12. **Model-based RL**: Learn a model of the environment for planning. More sample-efficient but harder to implement.

13. **Multi-agent RL**: Multiple agents interacting. Can be cooperative, competitive, or mixed.

14. **Reward shaping**: Design rewards carefully. Potential-based shaping preserves optimal policies.

15. **RLHF**: Use human preferences to train a reward model, then use PPO to align LLMs. The key technique behind ChatGPT/Claude alignment.

16. **Practical tools**: Gymnasium for environments, Stable-Baselines3 for training, TRL for RLHF.

---

[<< Previous: Chapter 11 - 3D Generation](./11_3D_GENERATION.md) | [Next: Chapter 13 - Audio and Speech AI >>](./13_AUDIO_SPEECH.md)
