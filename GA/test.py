from gene import NN
import gym
import pickle
import opensim as osim
from osim.env import RunEnv


def main():

	env = RunEnv(visualize=True)
	env.close()

	with open('save.p', 'r') as f:
		population = pickle.load(f)
	
	nn = population[0][0]
	total_reward = 0
	observation = env.reset()
	
	total_reward = 0
	observation = env.reset()
	for i in range(200):
		step = nn.compute(i)
		observation, reward, done, info = env.step(step)
		
		total_reward += reward
		if done:
			break


	print total_reward

if __name__ == '__main__':
	main()