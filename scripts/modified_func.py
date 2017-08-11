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
from keras.callbacks import History

from rl.callbacks import TestLogger, TrainEpisodeLogger, TrainIntervalLogger, Visualizer, CallbackList
import warnings
from copy import deepcopy

from osim.env import *

from keras.optimizers import RMSprop

import argparse
import math
import types


def fit_new(self, env, nb_steps, action_repetition=1, callbacks=None, verbose=1,
            visualize=False, nb_max_start_steps=0, start_step_policy=None, log_interval=10000,
            nb_max_episode_steps=None, arr=None):
        print 'FIT CHANGED ... Yayyyyy!!!!'
        """Trains the agent on the given environment.
        # Arguments
            env: (`Env` instance): Environment that the agent interacts with. See [Env](#env) for details.
            nb_steps (integer): Number of training steps to be performed.
            action_repetition (integer): Number of times the agent repeats the same action without
                observing the environment again. Setting this to a value > 1 can be useful
                if a single action only has a very small effect on the environment.
            callbacks (list of `keras.callbacks.Callback` or `rl.callbacks.Callback` instances):
                List of callbacks to apply during training. See [callbacks](/callbacks) for details.
            verbose (integer): 0 for no logging, 1 for interval logging (compare `log_interval`), 2 for episode logging
            visualize (boolean): If `True`, the environment is visualized during training. However,
                this is likely going to slow down training significantly and is thus intended to be
                a debugging instrument.
            nb_max_start_steps (integer): Number of maximum steps that the agent performs at the beginning
                of each episode using `start_step_policy`. Notice that this is an upper limit since
                the exact number of steps to be performed is sampled uniformly from [0, max_start_steps]
                at the beginning of each episode.
            start_step_policy (`lambda observation: action`): The policy
                to follow if `nb_max_start_steps` > 0. If set to `None`, a random action is performed.
            log_interval (integer): If `verbose` = 1, the number of steps that are considered to be an interval.
            nb_max_episode_steps (integer): Number of steps per episode that the agent performs before
                automatically resetting the environment. Set to `None` if each episode should run
                (potentially indefinitely) until the environment signals a terminal state.
        # Returns
            A `keras.callbacks.History` instance that recorded the entire training process.
        """
        if not self.compiled:
            raise RuntimeError('Your tried to fit your agent but it hasn\'t been compiled yet. Please call `compile()` before `fit()`.')
        if action_repetition < 1:
            raise ValueError('action_repetition must be >= 1, is {}'.format(action_repetition))

        self.training = True

        callbacks = [] if not callbacks else callbacks[:]

        if verbose == 1:
            callbacks += [TrainIntervalLogger(interval=log_interval)]
        elif verbose > 1:
            callbacks += [TrainEpisodeLogger()]
        if visualize:
            callbacks += [Visualizer()]
        history = History()
        callbacks += [history]
        callbacks = CallbackList(callbacks)
        if hasattr(callbacks, 'set_model'):
            callbacks.set_model(self)
        else:
            callbacks._set_model(self)
        callbacks._set_env(env)
        params = {
            'nb_steps': nb_steps,
        }
        if hasattr(callbacks, 'set_params'):
            callbacks.set_params(params)
        else:
            callbacks._set_params(params)
        self._on_train_begin()
        callbacks.on_train_begin()

        episode = 0
        self.step = 0
        observation = None
        episode_reward = None
        episode_step = None
        did_abort = False
        try:
            while self.step < nb_steps:
                if observation is None:  # start of a new episode
                    callbacks.on_episode_begin(episode)
                    episode_step = 0
                    episode_reward = 0.

                    # Obtain the initial observation by resetting the environment.
                    self.reset_states()
                    observation = deepcopy(env.reset())

                    if self.processor is not None:
                        observation = self.processor.process_observation(observation)
                    assert observation is not None

                    ############### HERE ##################
                    for ac in arr[:]:
                        # print type(ac), ac
                        if self.processor is not None:
                            ac = self.processor.process_action(ac)
                        callbacks.on_action_begin(ac)
                        observation, reward, done, info = env.step(ac)
                        observation = deepcopy(observation)
                        if self.processor is not None:
                            observation, reward, done, info = self.processor.process_step(observation, reward, done, info)
                        callbacks.on_action_end(ac)
                        if done:
                            #warnings.warn('Env ended before the deterministic non-neural steps could end.')
                            observation = deepcopy(env.reset())
                            if self.processor is not None:
                                observation = self.processor.process_observation(observation)
                            break

                    #############

                    # Perform random starts at beginning of episode and do not record them into the experience.
                    # This slightly changes the start position between games.
                    nb_random_start_steps = 0 if nb_max_start_steps == 0 else np.random.randint(nb_max_start_steps)
                    for _ in range(nb_random_start_steps):
                        if start_step_policy is None:
                            action = env.action_space.sample()
                        else:
                            action = start_step_policy(observation)
                        if self.processor is not None:
                            action = self.processor.process_action(action)
                        callbacks.on_action_begin(action)
                        observation, reward, done, info = env.step(action)
                        observation = deepcopy(observation)
                        if self.processor is not None:
                            observation, reward, done, info = self.processor.process_step(observation, reward, done, info)
                        callbacks.on_action_end(action)
                        if done:
                            warnings.warn('Env ended before {} random steps could be performed at the start. You should probably lower the `nb_max_start_steps` parameter.'.format(nb_random_start_steps))
                            observation = deepcopy(env.reset())
                            if self.processor is not None:
                                observation = self.processor.process_observation(observation)
                            break

                # At this point, we expect to be fully initialized.
                assert episode_reward is not None
                assert episode_step is not None
                assert observation is not None

                # Run a single step.
                callbacks.on_step_begin(episode_step)
                # This is were all of the work happens. We first perceive and compute the action
                # (forward step) and then use the reward to improve (backward step).
                action = self.forward(observation)
                if self.processor is not None:
                    action = self.processor.process_action(action)
                reward = 0.
                accumulated_info = {}
                done = False
                for _ in range(action_repetition):
                    callbacks.on_action_begin(action)
                    observation, r, done, info = env.step(action)
                    observation = deepcopy(observation)
                    if self.processor is not None:
                        observation, r, done, info = self.processor.process_step(observation, r, done, info)
                    for key, value in info.items():
                        if not np.isreal(value):
                            continue
                        if key not in accumulated_info:
                            accumulated_info[key] = np.zeros_like(value)
                        accumulated_info[key] += value
                    callbacks.on_action_end(action)
                    reward += r
                    if done:
                        break
                if nb_max_episode_steps and episode_step >= nb_max_episode_steps - 1:
                    # Force a terminal state.
                    done = True
                metrics = self.backward(reward, terminal=done)
                episode_reward += reward

                step_logs = {
                    'action': action,
                    'observation': observation,
                    'reward': reward,
                    'metrics': metrics,
                    'episode': episode,
                    'info': accumulated_info,
                }
                callbacks.on_step_end(episode_step, step_logs)
                episode_step += 1
                self.step += 1

                if done:
                    # We are in a terminal state but the agent hasn't yet seen it. We therefore
                    # perform one more forward-backward call and simply ignore the action before
                    # resetting the environment. We need to pass in `terminal=False` here since
                    # the *next* state, that is the state of the newly reset environment, is
                    # always non-terminal by convention.
                    self.forward(observation)
                    self.backward(0., terminal=False)

                    # This episode is finished, report and reset.
                    episode_logs = {
                        'episode_reward': episode_reward,
                        'nb_episode_steps': episode_step,
                        'nb_steps': self.step,
                    }
                    callbacks.on_episode_end(episode, episode_logs)

                    episode += 1
                    observation = None
                    episode_step = None
                    episode_reward = None
        except KeyboardInterrupt:
            # We catch keyboard interrupts here so that training can be be safely aborted.
            # This is so common that we've built this right into this function, which ensures that
            # the `on_train_end` method is properly called.
            did_abort = True
        callbacks.on_train_end(logs={'did_abort': did_abort})
        self._on_train_end()

        return history


def test_new(self, env, nb_episodes=1, action_repetition=1, callbacks=None, visualize=True,
         nb_max_episode_steps=None, nb_max_start_steps=0, start_step_policy=None, verbose=1, arr=None):
    """Callback that is called before training begins."
    """
    if not self.compiled:
        raise RuntimeError('Your tried to test your agent but it hasn\'t been compiled yet. Please call `compile()` before `test()`.')
    if action_repetition < 1:
        raise ValueError('action_repetition must be >= 1, is {}'.format(action_repetition))

    self.training = False
    self.step = 0

    callbacks = [] if not callbacks else callbacks[:]

    if verbose >= 1:
        callbacks += [TestLogger()]
    if visualize:
        callbacks += [Visualizer()]
    history = History()
    callbacks += [history]
    callbacks = CallbackList(callbacks)
    if hasattr(callbacks, 'set_model'):
        callbacks.set_model(self)
    else:
        callbacks._set_model(self)
    callbacks._set_env(env)
    params = {
        'nb_episodes': nb_episodes,
    }
    if hasattr(callbacks, 'set_params'):
        callbacks.set_params(params)
    else:
        callbacks._set_params(params)

    self._on_test_begin()
    callbacks.on_train_begin()
    for episode in range(nb_episodes):
        callbacks.on_episode_begin(episode)
        episode_reward = 0.
        episode_step = 0

        # Obtain the initial observation by resetting the environment.
        self.reset_states()
        observation = deepcopy(env.reset())
        if self.processor is not None:
            observation = self.processor.process_observation(observation)
        assert observation is not None

        for ac in arr:
            # print type(ac), ac
            if self.processor is not None:
                ac = self.processor.process_action(ac)
            callbacks.on_action_begin(ac)
            observation, reward, done, info = env.step(ac)
            observation = deepcopy(observation)
            if self.processor is not None:
                observation, reward, done, info = self.processor.process_step(observation, reward, done, info)
            callbacks.on_action_end(ac)
            self.step += 1
            episode_step += 1
            episode_reward += reward
            if done:
                #warnings.warn('Env ended before the deterministic non-neural steps could end.')
                observation = deepcopy(env.reset())
                if self.processor is not None:
                    observation = self.processor.process_observation(observation)
                break

        # Perform random starts at beginning of episode and do not record them into the experience.
        # This slightly changes the start position between games.
        nb_random_start_steps = 0 if nb_max_start_steps == 0 else np.random.randint(nb_max_start_steps)
        for _ in range(nb_random_start_steps):
            if start_step_policy is None:
                action = env.action_space.sample()
            else:
                action = start_step_policy(observation)
            if self.processor is not None:
                action = self.processor.process_action(action)
            callbacks.on_action_begin(action)
            observation, r, done, info = env.step(action)
            observation = deepcopy(observation)
            if self.processor is not None:
                observation, r, done, info = self.processor.process_step(observation, r, done, info)
            callbacks.on_action_end(action)

            if done:
                warnings.warn('Env ended before {} random steps could be performed at the start. You should probably lower the `nb_max_start_steps` parameter.'.format(nb_random_start_steps))
                observation = deepcopy(env.reset())
                if self.processor is not None:
                    observation = self.processor.process_observation(observation)
                break

        # Run the episode until we're done.
        done = False
        while not done:
            callbacks.on_step_begin(episode_step)

            action = self.forward(observation)
            if self.processor is not None:
                action = self.processor.process_action(action)
            reward = 0.
            accumulated_info = {}
            for _ in range(action_repetition):
                callbacks.on_action_begin(action)
                observation, r, d, info = env.step(action)
                observation = deepcopy(observation)
                if self.processor is not None:
                    observation, r, d, info = self.processor.process_step(observation, r, d, info)
                callbacks.on_action_end(action)
                reward += r
                for key, value in info.items():
                    if not np.isreal(value):
                        continue
                    if key not in accumulated_info:
                        accumulated_info[key] = np.zeros_like(value)
                    accumulated_info[key] += value
                if d:
                    done = True
                    break
            if nb_max_episode_steps and episode_step >= nb_max_episode_steps - 1:
                done = True
            self.backward(reward, terminal=done)
            episode_reward += reward

            step_logs = {
                'action': action,
                'observation': observation,
                'reward': reward,
                'episode': episode,
                'info': accumulated_info,
            }
            callbacks.on_step_end(episode_step, step_logs)
            episode_step += 1
            self.step += 1

        # We are in a terminal state but the agent hasn't yet seen it. We therefore
        # perform one more forward-backward call and simply ignore the action before
        # resetting the environment. We need to pass in `terminal=False` here since
        # the *next* state, that is the state of the newly reset environment, is
        # always non-terminal by convention.
        self.forward(observation)
        self.backward(0., terminal=False)

        # Report end of episode.
        episode_logs = {
            'episode_reward': episode_reward,
            'nb_steps': episode_step,
        }
        callbacks.on_episode_end(episode, episode_logs)
    callbacks.on_train_end()
    self._on_test_end()

    return history
