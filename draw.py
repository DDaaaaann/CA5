# Name: Daan de Graaf
# StudentNr. : 10360093
import matplotlib.pyplot as plt
import numpy as np

def draw(car_flow, repetitions, title, step_size):
    """ Plots the given data as a scatter plot """
    plt.close()
    step = 0
    for m in range(len(car_flow)):
        plt.scatter([step for i in range(repetitions)], car_flow[m])
        step += step_size

    steps = [i*step_size for i in range(int(1/step_size) + 1)]
    mean = np.mean(car_flow, axis=1)

    plt.plot(steps, mean, '-')

    plt.ylabel('Car flow')
    plt.xlabel('Density')
    plt.title(title)

    print "Showing car flow plot"
    plt.show()
