# Derived from keras-rl
import opensim as osim
import numpy as np
import pickle
import sys

from keras.models import Sequential, Model
from keras.layers import Dense, Activation, Flatten, Input, concatenate
from keras.optimizers import Adam

import numpy as np

from rl.agents import DDPGAgent
from rl.memory import SequentialMemory
from rl.random import OrnsteinUhlenbeckProcess
from rl.callbacks import Callback

from osim.env import *

from keras.optimizers import RMSprop

import argparse
import math
import types

# Command line parameters

parser = argparse.ArgumentParser(description='Train or test neural net motor controller')
parser.add_argument('--train', dest='train', action='store_true', default=True)
parser.add_argument('--test', dest='train', action='store_false', default=True)
parser.add_argument('--steps', dest='steps', action='store', default=1000000, type=int)
parser.add_argument('--visualize', dest='visualize', action='store_true', default=False)
parser.add_argument('--model', dest='model', action='store', default="arka.h5f")
args = parser.parse_args()

# Load walking environment
env = RunEnv(args.visualize)
env.reset()
obs = env.reset(difficulty=0)


class Histories(Callback):
    def __init__(self):
        Callback.__init__(self)
        self.action_dict_list = dict()
        self.ep_ctr = 0

    def on_episode_begin(self, episode, logs={}):
        self.action_dict_list[self.ep_ctr] = list()
        pass

    def on_action_end(self, action, logs={}):
        # self.action_list.append(action)
        self.action_dict_list[self.ep_ctr].append(action)

    def on_episode_end(self, episode, logs={}):
        self.ep_ctr += 1


def compute_reward_new(self):
    reward = -(self.current_state[2] - 0.91)**2
    return reward


if args.train:
    print('TRAIN')
    env.compute_reward = types.MethodType(compute_reward_new, env)

nb_actions = env.action_space.shape[0]

# Total number of steps in training
nallsteps = args.steps

# Create networks for DDPG
# Next, we build a very simple model.
actor = Sequential()
actor.add(Flatten(input_shape=(1,) + env.observation_space.shape))
actor.add(Dense(32))
actor.add(Activation('relu'))
actor.add(Dense(32))
actor.add(Activation('relu'))
actor.add(Dense(32))
actor.add(Activation('relu'))
actor.add(Dense(nb_actions))
actor.add(Activation('sigmoid'))
print(actor.summary())

action_input = Input(shape=(nb_actions,), name='action_input')
observation_input = Input(shape=(1,) + env.observation_space.shape, name='observation_input')
flattened_observation = Flatten()(observation_input)
x = concatenate([action_input, flattened_observation])
x = Dense(64)(x)
x = Activation('relu')(x)
x = Dense(64)(x)
x = Activation('relu')(x)
x = Dense(64)(x)
x = Activation('relu')(x)
x = Dense(1)(x)
critic = Model(inputs=[action_input, observation_input], outputs=x)
print(critic.summary())

# Set up the agent for training
memory = SequentialMemory(limit=100000, window_length=1)
random_process = OrnsteinUhlenbeckProcess(theta=.15, mu=0., sigma=.2, size=env.noutput)
agent = DDPGAgent(nb_actions=nb_actions, actor=actor, critic=critic, critic_action_input=action_input,
                  memory=memory, nb_steps_warmup_critic=100, nb_steps_warmup_actor=100,
                  random_process=random_process, gamma=.99, target_model_update=1e-3,
                  delta_clip=1.)
# agent = ContinuousDQNAgent(nb_actions=env.noutput, V_model=V_model, L_model=L_model, mu_model=mu_model,
#                            memory=memory, nb_steps_warmup=1000, random_process=random_process,
#                            gamma=.99, target_model_update=0.1)
agent.compile(Adam(lr=.001, clipnorm=1.), metrics=['mae'])

# Okay, now it's time to learn something! We visualize the training here for show, but this
# slows down training quite a lot. You can always safely abort the training prematurely using
# Ctrl + C.
if args.train:
    agent.fit(env, nb_steps=nallsteps, visualize=True, verbose=1, nb_max_episode_steps=1000, log_interval=1000)
    print 'TRAINED THE MODELS'
    # After training is done, we save the final weights.
    agent.save_weights(args.model, overwrite=True)

if not args.train:
    print args.model
    agent.load_weights(args.model)
    # sys.exit(0)
    # Finally, evaluate our algorithm for 1 episode.
    h = Histories()
    agent.test(env, nb_episodes=10, visualize=False, nb_max_episode_steps=1000, action_repetition=3, callbacks=[h])
    # print h.action_list
    f = open('values3.txt', 'w')
    # f.write(str(h.action_list)
    pickle.dump(h.action_dict_list, f)
    f.close()
    print("done pickling")
    # for i in range(600):
    #     ac = agent.forward(obs)
    #     f.write(str(ac))
    #     f.write('\n\n\n')
    #     obs, rew, _, _ = env.step(ac)

    # f.close()
