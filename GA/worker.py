import socket
import sys
from gene import NN
import gym
import pickle
import opensim as osim
from osim.env import RunEnv


def run(nn, env):

    total_reward = 0
    observation = env.reset()
    
    for i in range(500):
        step = nn.compute(i)
        observation, reward, done, info = env.step(step)
        
        total_reward += reward
        if done:
            break

    return total_reward


def main():
    env = RunEnv(visualize=False)

    s = socket.socket()
    s.bind(("localhost", 8000))
    s.listen(10) # max number of connections

    while True:
        sc, address = s.accept()
        f = open("work.p", 'wb')
        while (True):      
            l = sc.recv(1024)
            while (l):
                f.write(l)
                l = sc.recv(1024)
        f.close()

        with open('work.p', 'r') as f:
            nn = pickle.load(f)

        reward = run(nn, env)
        sc.send(str(reward))
        sc.close()

    s.close()


if __name__ == '__main__':
    main()