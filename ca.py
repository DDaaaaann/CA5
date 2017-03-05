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
births = 0
average_age = 0

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

"""Keep track of human states"""
def births_add():
    global births
    births += 1

def normal_deaths_add():
    global normal_deaths
    normal_deaths += 1

def averag_age_add(age):
    global average_age
    average_age += age

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
    def __init__(self, x, y, ave_age, death_rate, sick_days):
        self.color = 4
        self.infected = False
        self.days_with_malaria = 0
        self.age = 0
        self.net = False
        self.immune = False

        # Set by args
        self.x = x
        self.y = y
        self.ave_age = randint(int(ave_age*0.7), int(ave_age*1.1))
        self.death_rate = death_rate
        self.sick_days = sick_days

    def disease(self):
        """Continues the infection by being fatal or getting immune"""
        # sick_days by e.g. medication
        if self.days_with_malaria < self.sick_days:
            # Sadly dying is also an option
            if random() < self.death_rate:
                self.dead = True
                # print "Dead by malaria"
                # print "Age: ", self.age

                malaria_deaths_add()
            else:
                self.days_with_malaria += 1
        else:
            self.immune = True
            self.infected = False
            # print "Immune"
            immunes_add()

    def infect(self):
        """Human gets the infection"""
        if not self.immune:
            self.infected = True
            self.color = 5
            infects_add()

    def older(self):
        """The human ages over time untill ave_age"""
        self.age += 1
        if self.age > self.ave_age:
            self.dead = True
            # print "Dead by age"
            # print "Age: ", self.age
            averag_age_add(self.age)
            normal_deaths_add()

    def update(self):
        self.older()
        if self.infected:
            self.disease()

        return self.dead

class Mosquito(object):
    global glob_width
    global glob_height

    def __init__(self, x, y, hungry_in):
        self.x = x
        self.y = y
        # self.ave_age = ave_age
        self.infected = False
        self.hungry = True
        # Timesteps it take sbeing hungry again
        self.hungry_in = hungry_in
        # Keeps track of timesteps when hungry again
        self.hunger_count = self.hungry_in
        self.color = None
        self.coloring()

    def coloring(self):
        """Creates colors for the graphical simulation"""
        # Infected is more important than hungry (visually)
        if self.infected:
            self.color = 0
        elif self.hungry:
            self.color = 1
        else:
            self.color = 2

    def move(self):
        """Mosquito moves in a Moore neighborhood every timestep"""
        self.x += randint(-1, 1)
        self.y += randint(-1, 1)
        # periodic boundaries
        self.x %= glob_width
        self.y %= glob_height

    def infect(self):
        """Gets infectes by a human"""
        self.infected = True
        self.coloring()

    def satisfied(self):
        """No more hunger"""
        self.hungry = False
        self.hunger_count = self.hungry_in
        self.coloring()


    def need_for_blood(self):
        """Check if stomach is empty or digest blood"""
        if self.hunger_count == 0:
            self.hungry = True
            self.coloring()

        else:
            self.hunger_count -= 1

    def update(self):
        self.move()
        self.need_for_blood()
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

        # self.ave_age = 70
        # self.infection_chance = 0.5
        # self.hungry_in = 5

        # # Using this later on
        self.hum_param = {}
        self.mos_param = {}

        self.humans = 0
        self.mosquitos = 0
        self.infected = 0
        self.nets = 0

        self.make_param('width', 20)
        self.make_param('height', 20)
        self.make_param('nets_percentage', 0, setter=self.setter_nets)
        self.make_param('humans_percentage', 0.5, setter=self.setter_humans)
        self.make_param('mosquitos_percentage', 0.125, setter=self.setter_mosquitos)
        self.make_param('infected_percentage', 0.4, setter=self.setter_infected)

    def setter_infected(self, val):
        """Setter for the infected parameter, clipping its value <= mosquitos"""
        percentage = max(0, min(val, 1))
        self.infected = int(round((self.mosquitos)*float(percentage)))
        return percentage

    def setter_nets(self, val):
        """Setter for the max ammount of mosquitos"""
        percentage = max(0, min(val, (1)))
        self.nets = int(round((self.humans)*float(percentage)))
        print "nets: ", self.nets
        return percentage

    def setter_mosquitos(self, val):
        """Setter for the max ammount of mosquitos"""
        percentage = max(0, min(val, (1)))
        self.mosquitos = int(round((self.width*self.height)*float(percentage)))
        return percentage

    def setter_humans(self, val):
        """Setter for the max ammount of humans"""
        percentage = max(0, min(val, (1)))

        self.humans = int(round((self.width*self.height)*float(percentage)))
        return percentage


    def set_param(self, params):
        """ Sets parameters for the model provided in params """
        for key, value in params.iteritems():
            setattr(self, key, value)

    def statistics(self, statistics):
        infected = 0
        healhty = 0
        immune = 0
        for human in self.human_arr:
            if human.infected:
                infected += 1
            elif human.immune:
                immune += 1
            else:
                healhty += 1
        statistics[0].append(healhty)
        statistics[1].append(infected)
        statistics[2].append(immune)

        return statistics

    def update_situation(self):
        """Keeps track of all species in the grid and checks bites"""
        for mosquito in self.mosquito_arr:
            mosquito.update()

        for human in self.human_arr:
            # If a human died, create a baby in its place
            dead = human.update()
            if dead:
                self.human_arr.remove(human)
                if human.net:
                    # Pass the net to ne newborn
                    self.birth(True, False)
                else:
                    self.birth(False, False)

        for human in self.human_arr:
            # print "human"
            for mosquito in self.mosquito_arr:
                # In the same cell
                # print "mosquito"
                if human.x == mosquito.x and human.y == mosquito.y:
                    if mosquito.hungry:
                        # Human gets infected
                        if not human.infected and mosquito.infected and not human.net:
                            mosquito.satisfied()

                            if random() <= self.hum_param['infection_chance_mh']:
                                human.infect()
                                # print "break"
                                break

                        # Mosquito gets infected
                        elif human.infected and not mosquito.infected and not human.net:
                                mosquito.satisfied()

                                if random() <= self.mos_param['infection_chance_hm']:
                                    # print "break"

                                    mosquito.infect()
                                    break
                        # Mosquito had a thirst quencher
    def birth(self, net, init):
        """Creates a new human baby on an empty cell"""
        found = False
        x = randint(0, self.width-1)
        y = randint(0, self.height-1)
        if self.human_arr != []:

            while not found:
                found = True
                x = randint(0, self.width-1)
                y = randint(0, self.height-1)
                for human in self.human_arr:
                    if human.x == x and human.y == y:
                        found = False
                        break

        new_human = Human(x, y, self.hum_param['ave_age'], self.hum_param['death_rate'], self.hum_param['sick_days'])

        if net:
            new_human.net = True
        if init:
            new_human.age = randint(0, self.hum_param['ave_age'])

        self.human_arr.append(new_human)
        births_add()

    def fill_grid(self):
        """Fills the grid with humans and mosquitos according to parameters"""
        self.human_arr = []
        for i in range(self.humans - self.nets):
            print "birth"
            self.birth(False, True)

        for i in range(self.nets):
            self.birth(True, True)

        self.mosquito_arr = []
        for i in range(self.mosquitos):
            x = randint(0, self.width-1)
            y = randint(0, self.height-1)
            mosq = Mosquito(x, y, self.mos_param['hungry_in'])
            self.mosquito_arr.append(mosq)

        for i in range(self.infected):
            self.mosquito_arr[i].infect()

    def update_grid(self):
        """After each timestep update the visual simuation"""
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
        self.infected = int(round((self.mosquitos)*float(self.infected_percentage)))
        self.humans = int(round((self.width*self.height)*float(self.humans_percentage)))
        self.mosquitos = int(round((self.width*self.height)*float(self.mosquitos_percentage)))
        self.nets = int(round(self.humans)*float(self.nets_percentage))
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
            # sim.reset()

            repetitions = 1
            timesteps = 10000
            interval = 10
            statistics_arr = [[] for _ in range(3)]
            rate = []
            sample_rate = [[] for _ in range(repetitions)]


            final_verdict = []
            mos_params = []
            hum_params = []

            sim.hum_param = {'ave_age':70, 'infection_chance_mh':0.2, 'death_rate':0.0014, 'sick_days': 10}
            sim.mos_param = {'infection_chance_hm':0.2, 'hungry_in': 10}
            sim.mosquitos_percentage = 0.125
            sim.infected_percentage = 0.4
            sim.nets_percentage = 1

            for repeat in range(repetitions):
                sim.reset()
                # reset counters
                malaria_deaths = 0
                normal_deaths = 0
                infects = 0
                immunes = 0
                births = 0
                average_age = 0
                rate = []

                i = 0
                while i < timesteps:
                    sim.step()
                    if i % interval == 0:
                        statistics_arr = sim.statistics(statistics_arr)
                        rate.append(infects/float(births))
                        print "i: ",  i

                    i+=1

                sample_rate[repeat] = rate



            # print statistics_arr
            # plt.plot( final_verdict, label='rate')
            print "births: ", births
            print "infects: ", infects
            print "normal_deaths: ", normal_deaths
            print "malaria_deaths: ", malaria_deaths
            print "immunes: ", immunes
            print "infected: ", sim.infected
            print "verdict: ", infects/float(births)
            print "average_age: ", average_age/float(births)


            print len(sample_rate[0])
            for repeat in range(repetitions):
                plt.plot([interval*i for i in range(timesteps/interval)], sample_rate[repeat], label=repeat)
            title = "Prevalence with grid: " + str(sim.width) + "x" + str(sim.height) + " humans: " + str(sim.humans_percentage) + " mosquitos: " + str(sim.mosquitos_percentage) + " mosquitos infected: " + str(sim.infected_percentage)
            plt.title(title)
            plt.ylabel('Prevalence (infects/births)')
            plt.xlabel('Timesteps (T)')
            # plt.legend()
            plt.show()

            print "rate ", infects/float(births)
            print "normal_deaths", normal_deaths
            print "malaria_deaths", malaria_deaths
            print "infects", infects
            print "immunes", immunes



        elif userinput == 3:
            print "Quit"
            Menu = False
        else:
            print "\nThat's not an option"
