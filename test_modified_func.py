import opensim as osim

from osim.env import RunEnv
import sys

from osim.http.client import Client
import types

def modified_init(self, visualize = True, max_obstacles = 3):
    self.max_obstacles = max_obstacles
    super(RunEnv, self).__init__(visualize = False, noutput = self.noutput)
    self.osim_model.model.setUseVisualizer(visualize)
    self.create_obstacles()
    state = self.osim_model.model.initSystem()
    print 'Modified Init'
    state = [-0.12318915143209062, 0.8572259102524259, 0.8941775106918655, -0.01404221329096258, 0.2295314378679483, -0.021037075157206642, -0.681491323768328, 0.31352610722416563, -0.7920196539712908, -0.1582820172462255, 0.311412855895345, -0.10984746585998507, -0.02296411197489962, -0.00802550380398804, -0.0017461366413788204, -0.3041740263231416, 0.016811307539095512, 0.1819317051058162, 0.7530491584560023, 0.976491955750641, 0.21107478867080567, -0.014844146458944022, 0.898891834890124, 1.5194984121043213, 0.8572259102524259, 0.8941775106918655, 0.7562374616756263, 0.9883207301533766, 0.8043896105729741, -0.02441792460823137, 0.2730685561935682, 0.051075198992798276, 0.6779778525960489, 0.029056095674362847, 0.2780392718810951, 0.18824186908999707, 1, 1, 100, 0, 0]

    if visualize:
        manager = opensim.Manager(self.osim_model.model)
        manager.setInitialTime(-0.00001)
        manager.setFinalTime(0.0)
        manager.integrate(state)


env = RunEnv(visualize=True)

env.__init__ = types.MethodType(modified_init, env)
observation = env.reset(difficulty = 0)

for i in range(200):
    observation, reward, done, info = env.step([1.0]*18)
    print reward

