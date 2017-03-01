# Name: Daan de Graaf
# StudentNr. : 10360093
from draw import draw
import numpy as np
import time

def paramsweep(model, iterations, params):
    """ Iterates through the model using the given parameters"""
    done = False

    flow = [[0 for i in range(iterations)] for _ in range(int(1/model.step_size) + 1)]

    count = 0
    density = 0

    for density in np.arange(0.0, 1.0 + model.step_size, model.step_size):
        model.density = density

        for i in range(iterations):
            model.reset()

            while not done:
                done = model.step_simple()

            flow[count][i] = model.car_flow / float(model.height)

            # Reset for next iteration
            done = False
        count += 1

    return flow

    # draw(flow, iterations, model.width, model.height, model.step_size)
