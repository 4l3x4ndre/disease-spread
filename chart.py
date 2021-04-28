import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import random
import numpy


# Use a dedicated backend to handle interactive gui
mpl.use('TkAgg')

# Interactive mode on
plt.ioff()


class Chart:

    def __init__(self):
        self.figure = plt.figure()
        self.ax = plt.gca()
        
        self.setup_chart()
        self.draw()

    def setup_chart(self):
        """
        Initialization of needed chart values
        """
        self.ax.set_autoscale_on(True)

        # plt.plot() return a tuple
        # at start: 1 infected <=> day 0: 1 <=> [0], [1]
        self.hl, = plt.plot([0], [1])

    def add_values(self, x, y):
        """
        Add values to the plot
        """
        # we add data in x => numpy append: (the_array, the_value)
        self.hl.set_xdata(numpy.append(self.hl.get_xdata(), x))

	# Same on y axis
        self.hl.set_ydata(numpy.append(self.hl.get_ydata(), y))
    
        self.draw()

    def draw(self):
        """
        Draw the plot
        """
        # recompute axes
        self.ax.relim()

        # Scale the axes
        self.ax.autoscale_view(True,True,True)

        plt.draw()

def draw_chart():
    plt.plot(range(10))
    
    plt.figure()
    
    plt.draw()

