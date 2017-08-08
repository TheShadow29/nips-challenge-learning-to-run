import opensim as osim
from osim.http.client import Client
from osim.env import RunEnv

import pickle, sys
import numpy as np

# Settings
remote_base = "http://grader.crowdai.org:1729"
crowdai_token = "e5d9c43bc6add5150e8e23029d118215"

client = Client(remote_base)

# Create environment
observation = client.env_create(crowdai_token)


f = open('values_jump_new.txt', 'rb')
arrs = pickle.load(f)

g = open('values_second_leg.txt', 'rb')
arrs_new = pickle.load(g)

def my_controller(observation, ctr):
    return [float(x) for x in list(arr_list[min(ctr, max_action_steps-1)])]


ep_no = 2
arr_list = arrs[ep_no]

ep_no_new = 1
arr_list_new = arrs_new[ep_no_new]

arr_list = arr_list[0:180]
arr_list = arr_list + arr_list_new

max_action_steps = len(arr_list)

ctr = 0

while True:
    [observation, reward, done, info] = client.env_step(my_controller(observation, ctr), True)
    ctr += 1
    if done:
        observation = client.env_reset()
        ctr = 0
        if not observation:
            break

client.submit()
