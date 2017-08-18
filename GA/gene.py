import gym
import random
import numpy as np
from copy import deepcopy
import pickle
import opensim as osim
from osim.env import RunEnv

env = RunEnv(visualize=True)

class NN(object):

	def __init__(self):
		self.activations = [[random.randint(0, 1) for j in range(18)] for i in range(10)]

	def compute(self, i):
		return self.activations[i/20]

	def mutate(self):
		nn = deepcopy(self)
		s = random.randint(0, 2)
		if s <= 2:
			r = random.randint(0, 5)
		else:
			r = random.randint(6, 9)

		nn.activations[r] = [random.randint(0, 1) for j in range(18)]

		return nn

	def crossover(self, partner):
		nn = deepcopy(self)

		for i in range(0, 10, 2):
			nn.activations[i] = partner.activations[i]

		return nn

def run(nn):
	total_reward = 0
	observation = env.reset()
	for i in range(200):
		step = nn.compute(i)
		observation, reward, done, info = env.step(step)
		total_reward += reward
		if done:
			break

	return total_reward	


def main():

	population = [[NN(), 0] for _ in range(100)]
	generation = 0

	for _ in range(2000):
		for i in range(len(population)):
			print i
			population[i][1] = run(population[i][0])

		population = sorted(population, key = lambda x: x[1], reverse = True)
		print np.mean([p[1] for p in population[:5]])
		generation += 1

		population = population[:50]

		for _ in range(20):
			population.append([random.choice(population[:50])[0].mutate(), 0])

		for _ in range(20):
			nn1 = random.choice(population[:20])[0]
			nn2 = random.choice(population[:50])[0]
			population.append([nn1.crossover(nn2), 0])

		for _ in range(10):
			population.append([NN(), 0])

		with open('save.p', 'w') as f:
			pickle.dump(population, f)


if __name__ == '__main__':
	main()