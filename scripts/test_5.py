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
    return arr_list[ctr]


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

# print max_action_steps
for i in range(max_action_steps):
    observation, reward, done, info = env.step(my_controller(observation, i))

print observation