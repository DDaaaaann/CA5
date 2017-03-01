# Name: Daan de Graaf
# StudentNr. : 10360093
# Name: Bjorn Hato
# StudentNr. :???
import numpy as np
from random import randint
from random import random
from pyics import Model
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

""" 0 infected mosquito """
""" 1 hungry mosquito """
""" 2 mosquito """
""" 3 empty """
""" 4 human """
""" 5 infected human """
""" 6 immune human """
glob_width = None
glob_height = None
# Used for the legend
values= [0, 1, 2, 3, 4, 5, 6]
states = ['infected musquito', 'hungry mosquito', 'mosquito', '', 'human', 'infected human', 'imume human']

malaria_deaths = 0
normal_deaths = 0
infects = 0
immunes = 0

def get_input(text):
    """ Gets input from user and checks input """
    while True:
        try:
            number = int(input(text))
            if number < 0:
                print("Please give a positive number")
                continue
            break
        except:
            print("Try to use numbers")
    return number

def normal_deaths_add():
    global normal_deaths
    normal_deaths += 1

def infects_add():
    global infects
    infects += 1

def malaria_deaths_add():
    global malaria_deaths
    malaria_deaths += 1

def immunes_add():
    global immunes
    immunes += 1


class Human(object):
    dead = False

    def __init__(self, x, y, max_age):
        self.color = 4
        self.x = x
        self.y = y
        self.max_age = max_age
        self.infected = False
        self.age = 0
        self.days_with_malaria = 0
        self.net = False

        self.mortality_rate = 0.01
        self.survival = 20
        self.immune = False

    def disease(self):
        if self.days_with_malaria < self.survival:
            if random() < self.mortality_rate:
                self.dead = True
                print "Dead by malaria"
                print "Age: ", self.age

                malaria_deaths_add()
            else:
                self.days_with_malaria += 1
        else:
            self.immune = True
            self.infected = False
            print "Immune"
            immunes_add()

    def infect(self):
        self.infected = True
        self.color = 5
        print "Infected"
        infects_add()

    def older(self):
        self.age += 1
        if self.age > self.max_age:
            self.dead = True
            print "Dead by age"
            print "Age: ", self.age
            normal_deaths_add()

    def update(self):
        self.older()
        if self.infected:
            self.disease()

        return self.dead

class Mosquito(object):
    global glob_width
    global glob_height

    def __init__(self, x, y, max_age, hungry_in):
        self.x = x
        self.y = y
        self.max_age = max_age
        self.infected = False
        self.hungry = True
        self.hungry_in = hungry_in
        self.hunger_count = self.hungry_in
        self.color = None
        self.coloring()

    def coloring(self):
        # Infected is more important than hungry
        if self.infected:
            self.color = 0
        elif self.hungry:
            self.color = 1
        else:
            self.color = 2

    def move(self):
        self.x += randint(-1, 1)
        self.y += randint(-1, 1)
        self.x %= glob_width
        self.y %= glob_height

    def infect(self):
        self.infected = True
        self.coloring()

    def satisfied(self):
        self.hungry = False
        self.hunger_count = self.hungry_in
        self.coloring()


    def hunger(self):
        if self.hunger_count == 0:
            self.hungry = True
            self.coloring()

        else:
            self.hunger_count -= 1

    def update(self):
        self.move()
        self.hunger()
        # self.hungry()

class CASim(Model):
    def __init__(self):
        Model.__init__(self)
        # global glob_height
        # global glob_width


        self.t = 0

        self.human_arr = []
        self.mosquito_arr = []
        self.config = None

        self.max_age = 70
        self.infection_change = 0.5
        self.hungry_in = 5

        self.parameters = {'max_age':60, 'infection_change':0.5, 'mortality_rate':0.1, 'survival': 20}

        self.make_param('width', 10)
        self.make_param('height', 20)
        self.make_param('humans', 5, setter=self.setter_max)
        self.make_param('mosquitos', 5, setter=self.setter_max)
        self.make_param('infected', 1,  setter=self.setter_infected)

        # glob_height = self.height
        # glob_width = self.width

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


    def update_situation(self):
        """Keeps track of all species in the grid and checks bites"""
        for mosquito in self.mosquito_arr:
            mosquito.update()

        for human in self.human_arr:
            dead = human.update()
            if dead:
                self.human_arr.remove(human)
                self.birth()

        for human in self.human_arr:
            for mosquito in self.mosquito_arr:
                if human.x == mosquito.x and human.y == mosquito.y:
                    if mosquito.hungry:
                        if not human.infected and mosquito.infected and not human.immune:
                            if random() < self.parameters['infection_change']:
                                human.infect()
                        elif human.infected and not mosquito.infected:
                            mosquito.infect()
                        mosquito.satisfied()

    def birth(self):
        ok = False
        x = randint(0, self.width-1)
        y = randint(0, self.height-1)
        if self.human_arr != []:
            while not ok:
                for human in self.human_arr:
                    if human.x != x and human.y != y:
                        ok = True
                x = randint(0, self.width-1)
                y = randint(0, self.height-1)

        self.human_arr.append(Human(x, y, 80))

    def fill_grid(self):
        self.human_arr = []
        for i in range(self.humans):
            self.birth()

        self.mosquito_arr = []
        for i in range(self.mosquitos):
            x = randint(0, self.width-1)
            y = randint(0, self.height-1)
            mosq = Mosquito(x, y, 80, 10)
            self.mosquito_arr.append(mosq)

        for i in range(self.infected):
            self.mosquito_arr[i].infect()

    def update_grid(self):
        self.config = [[3 for i in range(self.width)] for j in range(self.height)]

        for human in self.human_arr:
            # Flip y and x since we're using a 2d array
            self.config[human.y][human.x] = human.color

        for mosquito in self.mosquito_arr:
            # Flip y and x since we're using a 2d array
            self.config[mosquito.y][mosquito.x] = mosquito.color


    def reset(self):
        """Initializes the configuration of the cells and converts the entered
        rule number to a rule set."""
        global glob_width
        global glob_height
        self.t = 0
        self.config = [[3 for _ in range(self.width)] for i in range(self.height)]
        glob_height = self.height
        glob_width = self.width
        self.fill_grid()
        self.update_grid()

    def draw(self):
        """Draws the current state of the grid."""

        plt.cla()
        # if not plt.gca().yaxis_inverted():
        #     plt.gca().invert_yaxis()
        im = plt.imshow(self.config, interpolation='none', vmin=0, vmax=6,
                cmap=matplotlib.cm.seismic)


        colors = [ im.cmap(im.norm(value)) for value in values]
        patches = [ mpatches.Patch(color=colors[i], label=states[i] ) for i in range(len(values)) ]
        plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )

        plt.axis('image')
        plt.title('t = %d' % self.t)



    def step(self):
        """Performs a single step of the simulation by advancing time (and thus
        row) and applying the rule to determine the state of the cells."""

        self.t += 1

        self.update_situation()
        self.update_grid()



if __name__ == '__main__':
    sim = CASim()
    Menu = True

    while Menu:
        print "\n1. Graphical simulation"
        print "2. Just calculate"
        print "3. Quit"

        userinput = get_input("Pick an option: ")

        if userinput == 1:
            sim = CASim()
            from pyics import GUI
            cx = GUI(sim)
            cx.start()
        elif userinput == 2:
            sim.reset()

            i = 0
            while i < 10000:
                sim.step()
                # print i
                i+=1

            print "normal_deaths", normal_deaths
            print "malaria_deaths", malaria_deaths
            print "infects", infects
            print "immunes", immunes

        elif userinput == 3:
            print "Quit"
            Menu = False
        else:
            print "\nThat's not an option"
