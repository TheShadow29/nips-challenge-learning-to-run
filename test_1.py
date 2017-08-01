from osim.env import RunEnv
import sys

env = RunEnv(visualize=True)
observation = env.reset(difficulty = 0)
print observation
# sys.exit(0)

for i in range(200):
    # print env.action_space
    # sys.exit(0)
    vec = [0.0385]*18
    val = 0.12
    vec[3] = val
    vec[12] = val
    vec[2] = 0.12
    vec[11] = 0.12
    observation, reward, done, info = env.step(vec)

print observation