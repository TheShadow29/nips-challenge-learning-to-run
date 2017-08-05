import opensim as osim
from osim.http.client import Client
from osim.env import RunEnv

import pickle, sys
import numpy as np

# Settings
remote_base = "http://grader.crowdai.org:1729"
crowdai_token = "eb91fbcaff6edd1cf9478ee56e41319a"

client = Client(remote_base)

# Create environment
observation = client.env_create(crowdai_token)

f = open('values.txt', 'rb')
arrs = pickle.load(f)

def my_controller(observation, ctr):
    # print list(arr_list[ctr])
    return list(arr_list[ctr])


# head0_x = 0
# observation
# head 22, 23
# pelvis 24, 25
ep_no = 2
arr_list = arrs[ep_no]

ctr = 0

while True:
    [observation, reward, done, info] = client.env_step(my_controller(observation, ctr), True)
    ctr += 1
    if done:
        observation = client.env_reset()
        if not observation:
            break

client.submit()