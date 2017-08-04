import opensim as osim

from osim.env import RunEnv
import sys

from osim.http.client import Client



env = RunEnv(visualize=True)
observation = env.reset(difficulty = 0)
#print observation
# sys.exit(0)


def my_controller(observation, ctr):
    vec = [0]*18
    if observation[22] < observation[24]:
        # head is behind the pelvis
        val = 0.8
    else:
        val = 0.2
    
    vec[6] = val
    vec[7] = val
    vec[15] = val
    vec[16] = val

    # if 
    # print (observation)
    return vec

ctr = 0
head0_x = 0
# observation 
# head 22, 23
# pelvis 24, 25
for i in range(130):
    observation, reward, done, info = env.step(my_controller(observation, ctr))
    ctr += 1
