import opensim as osim

from osim.env import RunEnv
import sys

from osim.http.client import Client



env = RunEnv(visualize=True)
observation = env.reset(difficulty = 0)
#print observation
# sys.exit(0)


def my_controller(observation, ctr):
    if ctr < 75: #tilt forward till 70 cycles
         vec=[0.1]*18
    elif ctr < 85:
        vec=[0.3]*18 #contract upper muscles
        val = 0.8
        vec[0] = val
        # vec[9] = val
    elif ctr < 95: #contract lower muscles and push the body forward
        vec=[0.3]*18
        val = 0.9
        vec[7] = val
        # vec[16] = val
    elif ctr < 105:
        vec=[0.2]*18
        val = 0.9
        vec[9] = val
    elif ctr < 115:
        vec=[0.2]*18 #contract upper muscles
        val = 0.9
        vec[16] = val
    elif ctr < 125:
        vec=[0.0]*18
        val = 0.9
        vec[0] = val
        vec[9] = val


    # elif ctr < 75: #tilt forward till 70 cycles
    #      vec=[0.0]*18
    # elif ctr < 75:
    #     vec=[0.0]*18 #contract upper muscles
    #     val = 0.8
    #     vec[0] = val
    #     # vec[9] = val
    # elif ctr < 84: #contract lower muscles and push the body forward
    #     vec=[0.0]*18
    #     val = 0.3
    #     vec[7] = val
    #     # vec[16] = val
    # elif ctr < 90:
    #     vec=[0.0]*18
    #     val = 0.3
    #     vec[7] = val
    #     # vec[16] = val
    #     vec[0] = 2*val
    #     # vec[9] = 2*val
    # elif ctr < 100:
    #     vec=[0.0]*18 #contract upper muscles
    #     val = 0.9
    #     vec[7] = val
    #     # vec[16] = val
    #     vec[6] = val
    #     # vec[15] = val
    # elif ctr < 125:
    #     vec=[0.0]*18
    #     val = 0.9
    #     vec[0] = val
        # vec[9] = val
    # elif ctr < 120:
    #     vec=[1.0]*18
    # elif ctr < 130:
    #     vec=[0.0]*18
    #     val = 1.0
        # vec[7] = val
        # vec[16] = val
        # vec[6] = val
        # vec[15] = val
    else:
        vec=[0.0]*18

    # print (observation)
    return vec

ctr = 70
for i in range(130):
    observation, reward, done, info = env.step(my_controller(observation, ctr))
    ctr += 1

# for i in range(75):
#     # print env.action_space
#     # sys.exit(0)
#     vec=[0.0]*18
#     observation, reward, done, info = env.step(vec)
#     #print reward

# #for k in range(6):
# for i in range(10):
#     # print env.action_space
#     # sys.exit(0)
#     vec=[0.0]*18
#     val = 0.8
#     vec[0] = val
#     vec[9] = val
#     observation, reward, done, info = env.step(vec)
#     #print reward

# for i in range(10):
#     # print env.action_space
#     # sys.exit(0)
#     vec=[0.0]*18
#     val = 0.8
#     vec[7] = val
#     vec[16] = val
#     observation, reward, done, info = env.step(vec)
#     #print reward

# for i in range(10):
#     # print env.action_space
#     # sys.exit(0)
#     vec=[1.0]*18
#     observation, reward, done, info = env.step(vec)
#     #print reward

# for i in range(25):
#     # print env.action_space
#     # sys.exit(0)
#     vec=[0.0]*18
#     val = 1.0
#     vec[7] = val
#     vec[16] = val
#     vec[6] = val
#     vec[15] = val
#     observation, reward, done, info = env.step(vec)
#     #print reward