# Name: Daan de Graaf
# StudentNr. : 10360093
import numpy as np
import random
from sweep_params import paramsweep
from pyics import Model
from draw import draw
from scipy import optimize as opt
from scipy import stats
import matplotlib.pyplot as plt




def decimal_to_base_k(Model):
    """ Converts a decimal to any base number """
    # https://www.cs.umd.edu/class/sum2003/cmsc311/Notes/Data/toBaseK.html
    rule = Model.rule
    k = Model.k
    r = Model.r
    rule_set_size = k**(2 * r + 1)

    index = 0
    ruleInBaseK = [0 for _ in range(rule_set_size)]
    while(rule != 0):
        ruleInBaseK[ index ] = rule % k
        rule /= k
        index += 1

    return ruleInBaseK

def base_k_to_decimal(digits, k):
    """ Converts any base number to a decimal """
    # http://cs.umd.edu/class/sum2003/cmsc311/Notes/Data/toBaseTen.html
    n = 0
    for d in digits:
        n = k * n + d
    return int(n)

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

def poly_plot(x, y, f):
    ''' Plots function f with y as scatter '''
    plt.close()
    x_new = np.linspace(x[0], x[-1], 50)
    y_new = f(x_new)

    plt.plot(x,y,'o', x_new, y_new)
    plt.xlim([x[0], x[-1]])
    plt.show()

def poly_fit(data, step_size):
    ''' Fits a third degree polynomial through data points from data'''
    ''' and returns the maximum '''
    steps = [i*step_size for i in range(int(1/step_size) + 1)]
    mean = np.mean(data, axis=1)

    z = np.polyfit(steps,mean, 3)
    f = np.poly1d(z)
    # poly_plot(steps, mean, f)
    return find_maximum(f)

def find_maximum(f):
    ''' Returns maximum of a given function f '''
    return float(opt.fmin(lambda x: -f(x), 0))



class CASim(Model):
    def __init__(self):
        Model.__init__(self)

        self.car_flow = 0

        self.t = 0
        self.rule_set = []
        self.config = None
        self.row = None
        self.step_size = 0.1
        # self.make_param()
        self.make_param('density', 0.0, setter=self.setter_density)
        self.make_param('r', 1)
        self.make_param('k', 2)
        self.make_param('width', 50)
        self.make_param('height', 50)
        self.make_param('rule', 184, setter=self.setter_rule)


    def setter_rule(self, val):
        """Setter for the rule parameter, clipping its value to 184"""
        return 184

    def setter_density(self, val):
        ''' Clipping density value between 0 and 1'''
        return max(0, min(val, 1))

    def build_rule_set(self):
        """Sets the rule set for the current rule.
        A rule set is a list with the new state for every old configuration.

        For example, for rule=34, k=3, r=1 this function should set rule_set to
        [0, ..., 0, 1, 0, 2, 1] (length 27). This means that for example
        [2, 2, 2] -> 0 and [0, 0, 1] -> 2."""

        self.rule_set = decimal_to_base_k(self)

    def check_rule(self, inp):
        """Returns the new state based on the input states.

        The input state will be an array of 2r+1 items between 0 and k, the
        neighbourhood which the state of the new cell depends on."""
        result = base_k_to_decimal(inp, self.k)
        new = self.rule_set[result]

        return new

    def set_param(self, params):
        """ Sets parameters for the model provided in params """
        for key, value in params.iteritems():
            setattr(self, key, value)


    def setup_initial_row(self):
        """Returns an array of length `width' with the initial state for each of
        the cells in the first row. Values should be between 0 and k."""
        cars = int(round(self.density*self.width))

        zeroes = [0 for i in range(self.width - cars)]
        ones = [1 for i in range(cars)]
        row = zeroes + ones
        random.shuffle(row)
        return row

    def check_car_flow(self):
        ''' Increases car flow when a car passes the right of the grid '''
        if self.row[0] == 0 and self.row[self.width - 1] == 1:
            self.car_flow += 1

    def find_critical_density(self, repetitions, params, critical_density):
        ''' Loops through T finding the critical density for n repetitions '''
        ''' Shows a plot of critical densities through time'''
        ''' And plotting the 90 percent probability of correctness'''

        T_arr = [T for T in range(1, 30)]
        # critical density array
        Dc_arr = [[] for rep in range(repetitions)]
        prob_correct = []
        accuracy = 0
        for T in range(1, 30): # Must be enough
            print "T = ", self.height

            for rep in range(repetitions):
                self.height = T

                flow = paramsweep(self, 10, params)
                phase_pos = poly_fit(flow, self.step_size)

                if phase_pos < 0:
                    phase_pos = 0

                Dc_arr[rep].append(phase_pos)

                # if the found critical density is within the interval, it is a hit
                if critical_density - 0.05 <= phase_pos <= critical_density + 0.05:
                    accuracy += 1

            # convert to probability
            prob_correct.append(accuracy/float(repetitions))
            accuracy = 0

        plt.close()
        # Plot all the found values
        for rep in range(repetitions):
            plt.plot(T_arr, Dc_arr[rep])
        plt.axhline(y=critical_density + 0.05, color='y', linestyle=':')
        plt.axhline(y=critical_density - 0.05, color='y', linestyle=':')
        title = str(repetitions) + ' repetitions and their critical density per\
timestep (T). Width: ' + str(params['width']) + ' stepsize: ' + str(params['step_size'])
        plt.title(title)
        plt.ylabel('Critical density')
        plt.xlabel('timesteps (T)')
        plt.show()
        # plt.clf()

        plt.figure()
        # Plot the probability of correctness
        plt.ylim([0, 1.1])
        plt.ylabel('Probability correct')
        plt.xlabel('timesteps (T)')
        title = 'Probability of correctness for each timestep (T) Width: '\
+ str(params['width']) + ' stepsize: ' + str(params['step_size']) + ' repetitions: ' + str(repetitions)
        plt.title(title)
        plt.axhline(y=0.9, color='y', linestyle=':')
        plt.plot(prob_correct)
        plt.show()



    def reset(self):
        """Initializes the configuration of the cells and converts the entered
        rule number to a rule set."""

        self.t = 0
        self.config = np.zeros([self.height, self.width])
        self.config[0, :] = self.setup_initial_row()
        self.row = self.setup_initial_row()
        self.car_flow = 0
        # self.setup_initial_row()
        self.build_rule_set()

    def draw(self):
        """Draws the current state of the grid."""

        import matplotlib
        import matplotlib.pyplot as plt

        plt.cla()
        if not plt.gca().yaxis_inverted():
            plt.gca().invert_yaxis()
        plt.imshow(self.config, interpolation='none', vmin=0, vmax=self.k - 1,
                cmap=matplotlib.cm.binary)
        plt.axis('image')
        plt.title('t = %d' % self.t)

    def step_simple(self):
        ''' Recreates the step function without storing previous configurations '''
        ''' Since this is only needed when drawing the gui '''
        self.t += 1
        if self.t >= self.height:
            return True
        new_row = []
        for patch in range(self.width):
            values = [self.row[i % self.width] for i in range(patch - self.r, patch + self.r + 1)]
            new_row.append(self.check_rule(values))

        self.row = new_row
        self.check_car_flow()



    def step(self):
        """Performs a single step of the simulation by advancing time (and thus
        row) and applying the rule to determine the state of the cells."""
        self.t += 1
        if self.t >= self.height:
            return True

        for patch in range(self.width):
            # We want the items r to the left and to the right of this patch,
            # while wrapping around (e.g. index -1 is the last item on the row).
            # Since slices do not support this, we create an array with the
            # indices we want and use that to index our grid.
            indices = [i % self.width
                    for i in range(patch - self.r, patch + self.r + 1)]
            values = self.config[self.t - 1, indices]
            self.config[self.t, patch] = self.check_rule(values)



if __name__ == '__main__':
    Menu = True
    critical_density = -1
    while Menu:
        print "\n1. Question 1"
        print "4. Question 4"
        print "5. Question 5"
        print "6. Question 6"
        print "7. Quit"

        userinput = get_input("   Pick an option: ")

####### QUESTION 1 #######
        if userinput == 1:
            sim = CASim()
            from pyics import GUI
            cx = GUI(sim)
            cx.start()

####### QUESTION 4 #######
        elif userinput == 4:
            print "\n ...QUESTION 4... \n"
            sim = CASim()
            repetitions = 5
            params = {'r':1, 'k':2, 'width': 50, 'height':1000, 'step_size':0.1}
            print "Using the following parameters: "
            print params
            print "Repetitions: " + str(repetitions)
            print "Running..."

            title = 'Car flow and mean. Using ' + str(repetitions) + ' repetitions and \
a width of: ' + str(params['width']) + ' and a height of: ' + str(params['height'])

            sim.set_param(params)
            flow = paramsweep(sim, repetitions, params)
            draw(flow, repetitions, title, sim.step_size)
            critical_density = poly_fit(flow, sim.step_size)

####### QUESTION 5 #######
        elif userinput == 5:
            print "\n ...QUESTION 5... \n"
            sim = CASim()
            repetitions = 3
            params = {'r':1, 'k':2, 'width': 50, 'height':5, 'step_size':0.1}
            print "Using the following parameters: "
            print params
            print "Repetitions: " + str(repetitions)
            print "Running..."

            title = 'Car flow and mean. Using ' + str(repetitions) + ' repetitions and \
a width of: ' + str(params['width']) + ' and a height of: ' + str(params['height'])

            sim.set_param(params)
            flow = paramsweep(sim, repetitions, params)
            draw(flow, repetitions, title, sim.step_size)

####### QUESTION 6 #######
        elif userinput == 6:
            print "\n ...QUESTION 6... \n"

            sim = CASim()

            # Find the critical density for a big height
            if critical_density == -1:
                print "Finding critical density with values like we did at question 4"
                repetitions = 10
                params = {'r':1, 'k':2, 'width': 50, 'height':1000, 'step_size':0.1}
                print "find"
                flow = paramsweep(sim, repetitions, params)
                # This is the 'estimated' critical density based on the parameters above
                critical_density = poly_fit(flow, sim.step_size)


            # Here we actually start the question
            params = {'r':1, 'k':2, 'width': 50, 'step_size':0.1}

            print "critical: ", critical_density
            result = sim.find_critical_density(10, params, critical_density)


        elif userinput == 7:
            print "Quit"
            Menu = False
        else:
            print "\nThat's not an option"
