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
        self.total_p, = plt.plot([0], [1], color='r')
        self.daily_p, = plt.plot([0], [1], color='y')
        self.dead_p, = plt.plot([0], [0], color='black')
        self.immune_p, = plt.plot([0], [0], color='magenta')

        # Legend on the upper left corner
        plt.legend(['total', 'daily', 'dead', 'immune'], loc='upper left')

    def add_values(self, day, total, daily, dead, immune):
        """
        Add values to the plot
        """

        # we add data in x => numpy append: (the_array, the_value)
        self.daily_p.set_xdata(numpy.append(self.daily_p.get_xdata(), day))
	# Same on y axis
        self.daily_p.set_ydata(numpy.append(self.daily_p.get_ydata(), daily))
    
        self.total_p.set_xdata(numpy.append(self.total_p.get_xdata(), day))
        self.total_p.set_ydata(numpy.append(self.total_p.get_ydata(), total))

        self.dead_p.set_xdata(numpy.append(self.dead_p.get_xdata(), day))
        self.dead_p.set_ydata(numpy.append(self.dead_p.get_ydata(), dead))
        
        self.immune_p.set_xdata(numpy.append(self.immune_p.get_xdata(), day))
        self.immune_p.set_ydata(numpy.append(self.immune_p.get_ydata(), immune))

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

