import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy


# Use a dedicated backend to handle interactive gui
mpl.use('TkAgg')

# Interactive mode on
plt.ioff()


class Chart:

    def __init__(self):
        # Figure to draw on, its id is 1
        self.figure = plt.figure(num=1)

        # Axes of the chart (used later to specify autoscale)
        self.ax = plt.gca()

        # To use later in setup_chart()
        self.total_p = self.daily_p = self.dead_p = self.immune_p = None

        # Initialization & drawing
        self.setup_chart()
        self.draw()
        
        # Draw !
        # Switching to figure n°1
        plt.figure(num=1)
        plt.draw()

    def setup_chart(self):
        """
        Initialization of needed chart values
        """

        # Switching to figure n°1
        plt.figure(num=1)

        # Auto scale axes to fit the curves
        self.ax.set_autoscale_on(True)

        # plt.plot() return a tuple
        # Why this values:
        #   1) at start: 1 infected
        #   2) <=> day 0: 1 infected
        #   3) <=> [0], [1]
        #   Doing this for all curves
        self.total_p, = plt.plot([0], [1], color='#FF4348')
        self.daily_p, = plt.plot([0], [1], color='y')
        self.dead_p, = plt.plot([0], [0], color='#000000')
        self.immune_p, = plt.plot([0], [0], color='#7B02FF')

        # Legend on the upper left corner
        plt.legend(['total', 'daily', 'dead', 'immune'], loc='upper left')

    def add_values(self, day, total, daily, dead, immune):
        """
        Add values to the plot. For each value: to set_data => in x and y (coordinate of point)

        Parameters
        ----------
        day: type int: n° of the current day
        total: type int: total cases
        daily: type int: daily cases
        dead: type int: total death at this date
        immune: type int: total immuned at this date

        Returns
        -------

        """
        
        # Switching to figure n°1
        plt.figure(num=1)

        # We add data in x => numpy.append: (the_array, the_value)
        # Same on y axis
        self.daily_p.set_xdata(numpy.append(self.daily_p.get_xdata(), day))
        self.daily_p.set_ydata(numpy.append(self.daily_p.get_ydata(), daily))
    
        self.total_p.set_xdata(numpy.append(self.total_p.get_xdata(), day))
        self.total_p.set_ydata(numpy.append(self.total_p.get_ydata(), total))

        self.dead_p.set_xdata(numpy.append(self.dead_p.get_xdata(), day))
        self.dead_p.set_ydata(numpy.append(self.dead_p.get_ydata(), dead))
        
        self.immune_p.set_xdata(numpy.append(self.immune_p.get_xdata(), day))
        self.immune_p.set_ydata(numpy.append(self.immune_p.get_ydata(), immune))

        # (Re)Drawing to update visible curves
        self.draw()

    def draw(self):
        """
        Draw the plot.
        """

        # Recompute axes
        self.ax.relim()

        # Scale the axes
        self.ax.autoscale_view(True, True, True)

        # Draw !
        # Switching to figure n°1
        plt.figure(1)
        plt.draw()
