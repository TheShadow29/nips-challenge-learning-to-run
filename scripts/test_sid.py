from __future__ import print_function
import opensim as osim
import pickle
from osim.env import RunEnv
import sys
import pdb
import numpy as np

from osim.http.client import Client



env = RunEnv(visualize=True)
observation = env.reset(difficulty = 2)
#print observation
# sys.exit(0)

f = open('values_jump_new.txt', 'rb')
arrs = pickle.load(f)

g = open('values_second_leg.txt', 'rb')
arrs_new = pickle.load(g)


def my_controller(observation, ctr):
    return map(float, list(arr_list[ctr]))


# head0_x = 0
# observation
# head 22, 23
# pelvis 24, 25
ep_no = 2
arr_list = arrs[ep_no]

# ep_no_new = 1
# arr_list_new = arrs_new[ep_no_new]
arr_list_new = list()

for arr in arr_list[:180]:
    new_arr = np.append(arr[9:], arr[:9])
    arr_list_new.append(new_arr)

arr_list = arr_list[0:180]
arr_list = arr_list + arr_list_new

max_action_steps = len(arr_list)
# pdb.set_trace()
# print max_action_steps
# for i in range(max_action_steps):
#     # print type(my_controller(observation, i)[0])
#     observation, reward, done, info = env.step(my_controller(observation, i))
total_reward = 0
# print max_action_steps
<<<<<<< HEAD:scripts/test_sid.py
#for i in range(max_action_steps):
#    # print type(my_controller(observation, i)[0])
#    observation, reward, done, info = env.step(my_controller(observation, i))

total_reward = 0
# print max_action_steps
for i in range(min(max_action_steps, 500)):
    # print type(my_controller(observation, i)[0])
    observation, reward, done, info = env.step(my_controller(observation, i))
    if (observation[2] < 0.65):
    	break
    total_reward += reward
    print total_reward

print observation
=======
# for i in range(min(max_action_steps, 500)):
#     # print type(my_controller(observation, i)[0])
#     observation, reward, done, info = env.step(my_controller(observation, i))
#     if (observation[2] < 0.65):
#         break
#     total_reward += reward
#     print(total_reward)

i = 0
while True:
    observation, reward, done, info = env.step(my_controller(observation, i % max_action_steps))
    total_reward += reward
    print('Total reward', total_reward, 'Iter', i)
    i += 1
    if (observation[2] < 0.65):
        break

print("Terminating")


# print observation

# print observation
>>>>>>> 9536a3a026843866473e3313a1b14673fa27c703:scripts/test_5.py
