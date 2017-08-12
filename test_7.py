import opensim as osim

from osim.env import RunEnv
import sys

from osim.http.client import Client



env = RunEnv(visualize=True)
observation = env.reset(difficulty = 0)
#print observation
# sys.exit(0)


def my_controller(observation, ctr):
    # bol1 = 0
    if ctr < 50:
        vec = [0]*18
        vec[0] = 1
        vec[1] = 1
        vec[9:] = [1]*9
        # vec[4] = 1
        # vec[5] = 1
        # vec[6] = 1
        # vec[7] = 1
        # vec[8] = 1
    elif ctr < 100:
        vec = [0]*18
        vec[9] = 1
        vec[10] = 1
        vec[:9] = [1]*9 
        
    else:
        vec = [0]*18
        # vec[15] = 0.5
        # vec[16] = 0.5
    # if ctr < 75: #tilt forward till 70 cycles
    #      vec=[0.1]*18
    # elif ctr < 85:
    #     vec=[0.3]*18 #contract upper muscles
    #     val = 0.8
    #     vec[0] = val
    #     # vec[9] = val
    # elif ctr < 95: #contract lower muscles and push the body forward
    #     vec=[0.3]*18
    #     val = 0.9
    #     vec[7] = val
    #     # vec[16] = val
    # elif ctr < 105:
    #     vec=[0.2]*18
    #     val = 0.9
    #     vec[9] = val
    # elif ctr < 115:
    #     vec=[0.2]*18 #contract upper muscles
    #     val = 0.9
    #     vec[16] = val
    # elif ctr < 125:
    #     vec=[0.0]*18
    #     val = 0.9
    #     vec[0] = val
    #     vec[9] = val
    # else:
    #     vec=[0.0]*18

    # print (observation)
    return vec

ctr = 0
for i in range(1000):
    observation, reward, done, info = env.step(my_controller(observation, ctr))
    ctr += 1
    ctr = ctr % 100
    print(ctr)
