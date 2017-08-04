import opensim as osim
import pickle
from osim.env import RunEnv
import sys

from osim.http.client import Client



env = RunEnv(visualize=True)
observation = env.reset(difficulty = 0)
#print observation
# sys.exit(0)

f = open('./scripts/values.txt', 'rb')
arrs = pickle.load(f)
def my_controller(observation, ctr):
    return arr_list[ctr]


# head0_x = 0
# observation
# head 22, 23
# pelvis 24, 25
ep_no = 2
arr_list = arrs[ep_no]
max_action_steps = len(arr_list)
# print max_action_steps
for i in range(max_action_steps):
    observation, reward, done, info = env.step(my_controller(observation, i))
    print reward
    # ctr += 1
