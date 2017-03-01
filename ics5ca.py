# Name: Mees Kalf
# UvaID: 10462074
# Assignment: ca2
#
# Main for simulating cellular automata.

from random import shuffle
import numpy as np
from pyics import Model
import matplotlib
import matplotlib.pyplot as plt
from random import randint
import copy



class animal:
    def __init__(self):
        self.infected = 0
        self.age = 0
        self.name = ''

    def older(self):
        self.age += 1
        return self.age

    def get_malaria(self):
        self.infected = 1

    def species(self):
        return self.name


class CASim(Model):
    def __init__(self):
        Model.__init__(self)
        self.t = 0
        self.config = None
        self.malaria_count = 0
        self.human_count = 0
        self.mug_count = 0
        self.k = 20
        self.animals_with_malaria = 0
        self.make_param('width', 20)
        self.make_param('height', 20)
        self.make_param('human_amount', 10)
        self.make_param('mug_amount', 100)
        self.make_param('malaria_amount', 4)

    def reset(self):
        self.config = np.zeros([self.width, self.height])
        self.content = [[[] for j in xrange(self.width)] for i in xrange(self.height)]
        self.t = 0
        self.human_count = 0
        self.mug_count = 0
        self.malaria_count = 0


        while self.malaria_count != self.malaria_amount:
            x = randint(0,self.width - 1)
            y = randint(0,self.height - 1)
            self.content[x][y].insert(0, animal())
            self.content[x][y][0].name = 'human'
            self.content[x][y][0].get_malaria()
            self.content[x][y][0].age = randint(0,50)
            self.malaria_count += 1


    def refill_farm(self):
        # initial generation humans is computed with random age, second etc are
        # born when anyone dies.
        while self.human_count != self.human_amount:
            x = randint(0,self.width - 1)
            y = randint(0,self.height - 1)
            self.content[x][y].insert(0, animal())
            self.content[x][y][0].name = 'human'
            if self.t == 0: self.content[x][y][0].age = randint(0,50)
            self.human_count += 1
        # initial generation mug is computed with random age, second etc are
        # born when anyone dies
        while self.mug_count != self.mug_amount:
            x = randint(0,self.width - 1)
            y = randint(0,self.height - 1)
            self.content[x][y].insert(0, animal())
            self.content[x][y][0].name = 'mug'
            if self.t == 0: self.content[x][y][0].age = randint(0,50)
            self.mug_count += 1

    def draw(self):
        plt.cla()
        if not plt.gca().yaxis_inverted():
            plt.gca().invert_yaxis()
        plt.imshow(self.config, interpolation='none', vmin=0, vmax=self.k - 1,
                cmap=matplotlib.cm.Dark2) ## andere colormap maken hiero voor mensen, muggen, net, infected etc!
        plt.axis('image')
        plt.title('t = %d' % self.t)

    def step(self):
        self.refill_farm()
        self.animals_with_malaria = 0

        self.config = np.zeros([self.height, self.width])
        temp = 0
        self.t += 1
        temp = copy.deepcopy(self.content)
        self.content = [[[] for j in xrange(self.width)] for i in xrange(self.height)]

        for i in range(0,self.width):
            for j in range(0, self.height):

                for p in temp[i][j]:
                    if ('human' in p.name):
                        for x in temp[i][j]:
                            if x.infected:
                                for z in temp[i][j]:
                                    z.get_malaria()
                            break
                        else: continue
                        break


                while(temp[i][j]):
                    ii = i + randint(-1,1)
                    jj = j + randint(-1,1)
                    while (ii == self.width or jj == self.height or ii == -1 or jj == -1 ):
                        ii = i + randint(-1,1)
                        jj = j + randint(-1,1)
                    #while (self.content[ii][jj]):
                    #    for k in range(len(self.content[ii][jj])):
                    #        if (self.content[ii][jj][k].species() == 'human'):
                    #            ii = i + randint(-1,1)
                    #            if ii == self.width: ii= self.width -1
                    #            jj = j + randint(-1,1)
                    #            if jj == self.width: jj = self.width - 1
                    if (temp[i][j][0].older() < 50):
                        self.content[ii][jj].extend([temp[i][j].pop(0)])
                    else:
                        if temp[i][j][0].species() == 'human': self.human_count -= 1
                        if temp[i][j][0].species() == 'mug': self.mug_count -= 1
                        temp[i][j].pop(0)


        for i in range (0,self.width):
            for j in range(0,self.height):
                amount = 0
                if (self.content[i][j] != []):

                    for each in self.content[i][j]:
                        if each.infected:
                            self.animals_with_malaria += 1
                            amount += 20
                        if each.name == 'human':
                            amount += 10
                        else:
                            amount += 2
                    self.config[i][j] = amount

        print 'amount of infected animals: ', self.animals_with_malaria
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# wat moet er gebeuren als er 8 man om 1 man heen staan en iemand gaat op zijn
# plek staan? kan hij nergens heen?! ( mag max 1 persoon pet blokje).
# als geinfecteerde dood gaan niet opnieuw geboren laten worden toch?
# random generen van immuum, allergisch etc? of zelf kunnen instellen?
# zodra meerdere muggen bij 1 man zijn en een van de muggen if geinfecteerd
# of de man, dan iedereen geinfecteerd toch?

if __name__ == '__main__':

    sim = CASim()


    from pyics import GUI
    cx = GUI(sim)
    cx.start()
