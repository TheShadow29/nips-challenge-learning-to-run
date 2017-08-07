import opensim as osim
import pickle
from osim.env import RunEnv
import sys

from osim.http.client import Client



env = RunEnv(visualize=True)
observation = env.reset(difficulty = 0)
#print observation
# sys.exit(0)

f = open('values_jump_new.txt', 'rb')
arrs = pickle.load(f)

g = open('values_second_leg.txt', 'rb')
arrs_new = pickle.load(g)

def my_controller(observation, ctr):
    return list(arr_list[min(ctr, max_action_steps)])


# head0_x = 0
# observation
# head 22, 23
# pelvis 24, 25
ep_no = 2
arr_list = arrs[ep_no]

ep_no_new = 1
arr_list_new = arrs_new[ep_no_new]

arr_list = arr_list[0:180]
arr_list = arr_list + arr_list_new

max_action_steps = len(arr_list)
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