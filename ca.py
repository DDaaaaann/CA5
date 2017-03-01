# Name: Daan de Graaf
# StudentNr. : 10360093
# Name: Bjorn Hato
# StudentNr. :???
import numpy as np
from random import randint
from sweep_params import paramsweep
from pyics import Model
from draw import draw
from scipy import optimize as opt
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

""" 0 infected mosquito """
""" 1 hungry mosquito """
""" 2 mosquito """
""" 3 empty """
""" 4 human """
""" 5 infected human """
""" 6 immune human """




class Human(object):
    age = 0
    immune = False
    dead = False
    def __init__(self, x, y, max_age, infected):
        self.color = 4
        self.x = x
        self.y = y
        self.max_age = max_age
        self.infected = infected

    def infect():
        self.infected = 1

    def older():
        age += 1
        if age > max_age:
            dead = True

    def update():
        self.older()

class Mosquito(object):

    def __init__(self, x, y, max_age, infected):
        self.x = x
        self.y = y
        self.max_age = max_age
        self.infected = False
        self.color = 2


    def move(self, width, height):
        self.x += randint(-1, 1)
        self.y += randint(-1, 1)
        self.x %= width
        self.y %= height

    def infect(self):
        self.infected = True
        print "infected"
        self.color = 0

class CASim(Model):
    def __init__(self):
        Model.__init__(self)

        self.human_arr = []
        self.mosquito_arr = []
        self.t = 0
        self.config = None
        self.k = 20
        # self.make_param()
        self.make_param('width', 50)
        self.make_param('height', 50)
        self.make_param('humans', 50, setter=self.setter_max)
        self.make_param('mosquitos', 50, setter=self.setter_max)
        self.make_param('infected', 20,  setter=self.setter_infected)


    def setter_infected(self, val):
        """Setter for the infected parameter, clipping its value <= mosquitos"""
        return max(0, min(val, self.mosquitos))

    def setter_max(self, val):
        """Setter for the max ammount of human/mosquitos"""
        return max(0, min(val, (self.width*self.height)))


    def set_param(self, params):
        """ Sets parameters for the model provided in params """
        for key, value in params.iteritems():
            setattr(self, key, value)

    def fill_grid(self):
        self.human_arr = []
        for i in range(self.humans):
            x = randint(0, self.width-1)
            y = randint(0, self.height-1)
            human = Human(x, y, 80, 0)
            self.human_arr.append(human)

        self.mosquito_arr = []
        for i in range(self.mosquitos):
            x = randint(0, self.width-1)
            y = randint(0, self.height-1)
            mosq = Mosquito(x, y, 80, 0)
            self.mosquito_arr.append(mosq)

        for i in range(self.infected):
            self.mosquito_arr[i].infect()

    def update_grid(self):
        self.config = [[3 for _ in range(self.width)] for i in range(self.height)]
        for human in self.human_arr:
            self.config[human.x][human.y] = human.color
        for mosquito in self.mosquito_arr:
            print mosquito.color
            self.config[mosquito.x][mosquito.y] = mosquito.color



    def reset(self):
        """Initializes the configuration of the cells and converts the entered
        rule number to a rule set."""

        self.t = 0
        self.config = [[3 for _ in range(self.width)] for i in range(self.height)]
        self.fill_grid()
        self.update_grid()

    def draw(self):
        """Draws the current state of the grid."""

        import matplotlib
        import matplotlib.pyplot as plt

        plt.cla()
        if not plt.gca().yaxis_inverted():
            plt.gca().invert_yaxis()
        im = plt.imshow(self.config, interpolation='none', vmin=0, vmax=6,
                cmap=matplotlib.cm.seismic, label=['mug'])

        values= [0, 1, 2, 3, 4, 5, 6]
        states = ['infected musquito', 'hungry mosquito', 'mosquito', 'empty', 'human', 'infected human', 'imume human']
        colors = [ im.cmap(im.norm(value)) for value in values]
        patches = [ mpatches.Patch(color=colors[i], label=states[i] ) for i in range(len(values)) ]
        plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )

        plt.axis('image')
        plt.title('t = %d' % self.t)



    def step(self):
        """Performs a single step of the simulation by advancing time (and thus
        row) and applying the rule to determine the state of the cells."""

        for mosquito in self.mosquito_arr:
            mosquito.move(self.width, self.height)

        self.update_grid()



if __name__ == '__main__':

    sim = CASim()
    from pyics import GUI

    cx = GUI(sim)
    cx.start()

    human_arr = []
