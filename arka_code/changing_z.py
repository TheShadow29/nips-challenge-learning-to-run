from __future__ import print_function
from __future__ import division
import opensim as osim
import numpy as np
import keras
import rl

import argparse

from modified_functions import fit_new, test_new

import osim.env as oenv

from rl.callbacks import Callback
import types


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


class ddpg_keras():
    def __init__(self, env):
        self.env = env
        self.obs_space_dim = self.env.observation_space.shape[0]
        self.action_space_dim = self.env.action_space.shape[0]
        self.actor = self.create_actor()
        self.critic, self.action_input = self.create_critic()
        self.memory = rl.memory.SequentialMemory(limit=10000, window_length=1)
        self.random_process = rl.random.OrnsteinUhlenbeckProcess(
            theta=.15, mu=0., sigma=.2, size=self.env.noutput)
        self.agent = rl.agents.DDPGAgent(nb_actions=self.action_space_dim,
                                         actor=self.actor, critic=self.critic,
                                         critic_action_input=self.action_input,
                                         memory=self.memory, random_process=self.random_process,
                                         delta_clip=1)

        self.agent.compile(keras.optimizers.Adam(lr=.001, clipnorm=1.), metrics=['mae'])

    def create_actor(self):
        # can try to use selu instead of relu as well
        actor = keras.models.Sequential([
            keras.layers.Flatten(input_shape=(1,) + self.env.observation_space.shape),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(self.action_space_dim, activation='sigmoid')
        ])
        print(actor.summary())
        return actor

    def create_critic(self):
        # critic = keras.models.Sequential([
        #     keras.layers.Flatten(input_shape=(1,) + self.env.action_space + self.env.obs_space)
        #     keras.layers.Flatten()
        # ])
        action_input = keras.layers.Input(shape=(nb_actions,))
        obs_input = keras.layers.Input(shape=(1,) + self.env.observation_space.shape)
        flattened_observation = keras.layers.Flatten()(obs_input)
        x = keras.layers.concatenate([action_input, flattened_observation])
        x = keras.layers.Dense(128, activation='relu')(x)
        x = keras.layers.Dense(256, activation='relu')(x)
        x = keras.layers.Dense(128, activation='relu')(x)
        x = keras.layers.Dense(64, activation='relu')(x)
        x = keras.layers.Dense(32, activation='relu')(x)
        x = keras.layers.Dense(16, activation='relu')(x)
        x = keras.layers.Dense(1, activation='relu')(x)
        critic = keras.models.Model(inputs=[action_input, obs_input], outputs=x)
        print(critic.summary())
        return critic, action_input

    def train_model(self, changing_z=True, load_weights=False, load_weights_path=None,
                    nallsteps=1000000):

        obs1 = self.env.reset(difficulty=0)
        if load_weights:
            self.agent.load_weights(load_weights_path)
        self.agent.fit = types.MethodType(fit_new, self.agent)
        # print(env.difficulty)
        self.agent.fit(self.env, nb_steps=nallsteps, visualize=True,
                       verbose=1, nb_max_episode_steps=1000,
                       log_interval=1000, difficulty=0)
        print('Trained models')
        self.agent.save_weights(args.model, overwrite=True)
        return

    def test_model(self, load_weights_path=None):
        if load_weights_path:
            self.agent.load_weights(load_weights_path)
        self.agent.test = types.MethodType(test_new, self.agent)  #
        h = Histories()
        self.agent.test(self.env, nb_episodes=2, visualize=True, nb_max_episode_steps=250,
                        action_repetition=2, callbacks=[h], difficulty=0)


if __name__ == '__main__':
    # print('hello')
    parser = argparse.ArgumentParser(description='Train or test neural net motor controller')
    parser.add_argument('--train', dest='train', action='store_true', default=True)
    parser.add_argument('--test', dest='train', action='store_false', default=True)
    parser.add_argument('--steps', dest='steps', action='store', default=1000000, type=int)
    parser.add_argument('--visualize', dest='visualize', action='store_true', default=False)
    # parser.add_argument('--model', dest='model', action='store', default="less_params.h5f")
    parser.add_argument('--model', dest='model', action='store',
                        default="z_changing")
    parser.add_argument('--load_initial', dest='load_initial', action='store_true', default=False)
    args = parser.parse_args()

    env = oenv.RunEnv(args.visualize)
    # env.reset()
    obs = env.reset(difficulty=0)

    nb_actions = env.action_space.shape[0]
    nallsteps = args.steps
    model = ddpg_keras(env)
    if args.train:
        print('Training')
        model.train_model()
    else:
        print('Testing')
        model.test_model()
