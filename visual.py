import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import random


# Use a dedicated backend to handle interactive gui
mpl.use('TkAgg')

# Interactive mode on
plt.ion()


class State:
    def __init__(self, g, g_nx, spread_func, root, anim_time, chart, lockdown):

        # ALL THE FOLLOWING OF __INIT__ INITIALIZES VALUES

        self.index = 0
        self.g = g
        self.g_nx = g_nx
        self.root = root

        # Positions of the nodes to keep them in the same place and not redraw completely the graph each time
        self.pos = nx.fruchterman_reingold_layout(self.g_nx)

        # Keep track of graph colors
        self.colors = ['#35FFAD' for i in range(self.g_nx.number_of_nodes())]

        # Spread function to create a step by step spread
        self.spread = spread_func
        self.spread_attributes = {'g': g, 'id': 0, 'r': root, 'to_infect': [root], 'infected': []}

        # Infected nodes: {node_name: day of infection}
        # With the day, we can create an immunity system
        self.infected = {root: 0}

        # Like infected but with immune
        self.immune = {}

        # Nodes under lockdown
        self.locked = {}

        # Values that will be modified
        self.r0 = 3
        self.r0_delta = 3
        # Day to immunity (DTI)
        self.day_to_immunity = 5
        # Immunity period in days
        self.immunity_period = 10
        # Death probability when infected. If random is lower, the vertice is dead.
        self.deathprob = .1

        # Colors
        self.color_pallet = {
            "normal": "#35FFAD",
            "infected": "#FF4348",
            "immune": "#7B02FF",
            "dead": "#000000",
            "lockdown" : "#A19DA4"
        }

        # General information
        self.is_stopped = False
        self.is_auto = False
        self.closing = False
        self.change = True
        self.lockdown = lockdown

        # Time between frames
        self.anim_time = anim_time

        # The number of cases, updated in the 'next' method
        self.nbcases = 1  # the first one is the root
        self.daily_cases = 1
        self.nbdead = 0 

        # Chart to plot spread numbers
        self.chart = chart

    def start_loop(self):
        """
        Start the infinite loop to handle changes and draw them.
        """
        self.loop()

    def loop(self):
        """
        The main loop to maintain the plt on screen.
        """

        # While we did not press the close button -> continue the loop
        while not self.closing:
            # Switching to figure n°0
            plt.figure(0)
            # True when pressing next
            if self.change:
                self.change = False
                self.draw()
            # True when pressing auto
            elif self.is_auto:
                # Check if the auto should stop (aka the Stop button is pressed)
                if not self.check_auto():
                    self.is_auto = False
                    continue
                self.next()
                self.change = False
                self.draw()

            # Updates chart to display new spread numbers
            # Switching to figure n°1 (aka the chart)
            plt.figure(1)
            self.update_chart(self.index, self.nbcases, self.daily_cases, self.nbdead, len(list(self.immune.keys())))

            # Draw then pause
            # Switching to figure n°0
            plt.figure(0)
            plt.draw()

            plt.pause(self.anim_time)

    def update_chart(self, day, total, daily, dead, immune):
        """
        Call chart functions to upadte the chart by adding values.

        Parameters
        ----------
        day: type int: The current day <=> the x position of the given values on the curves.
        total: type int: Total amount of cases at this date.
        daily: type int: Daily amount of cases.
        dead: type int: Total amount of dead at this date.
        immune: type int: Total amount of immuned at this date.

        Returns
        -------
        """

        self.chart.add_values(day, total, daily, dead, immune)

    def set_node_colors(self):
        """
        Set colors according to the node state : immune; dead; infected; normal (and lockdown when asked)
        """

        for i in range(len(list(self.g_nx.nodes))):
            nodex = list(self.g_nx.nodes)[i]  # node name

            # if in immune array -> node is immune
            if nodex in self.immune:
                self.colors[i] = self.color_pallet['immune']
            
            # if under lockdown
            elif nodex in self.locked:
                self.colors[i] = self.color_pallet['lockdown']
            
            # When infected there are two possibilities: dead or infected
            elif nodex in self.infected:
                if self.infected[nodex] == -1:
                    self.colors[i] = self.color_pallet['dead']
                else:
                    self.colors[i] = self.color_pallet['infected']
            
            # If not int all of the cases above -> the vertice is normal
            else:
                self.colors[i] = self.color_pallet['normal']
        

    def draw_buttons(self):
        """
        Draw all buttons in plt.
        """
        # /!\ Definition of a button with axes: [x0, y0, width, height]


        # Button to continue the spread. Adding a reference in the class and an on_click event.
        b_axnext = plt.axes([0.002, 0.02, 0.05, 0.025])
        self.bnext = Button(b_axnext, 'Next')
        self.bnext.on_clicked(self.next)

        # Button to transit to the end <=> auto mode. Adding a reference in the class and an on_click event.
        b_axend = plt.axes([0.002, 0.05, 0.05, 0.025])
        self.bend = Button(b_axend, 'Auto')
        self.bend.on_clicked(self.last_action)

        # Button to stop everything. Adding a reference in the class and an on_click event.
        b_axstop = plt.axes([0.002, 0.08, 0.05, 0.025])
        self.bstop = Button(b_axstop, 'Stop')
        self.bstop.on_clicked(self.stop)

        # Button to close and stop everything. Adding a reference in the class and an on_click event.
        b_axclose = plt.axes([1 - 0.05, 1 - 0.025, 0.05, 0.025])
        self.bclose = Button(b_axclose, 'Close')
        self.bclose.on_clicked(self.close)

    def draw_sliders(self):
        """
        Draws all sliders in plt.
        """

        # r0 slider
        axcolor = 'lightgrey'
        ax_r0slider = plt.axes([0.01, 0.25, 0.015, 0.3], facecolor=axcolor)
        self.r0_slider = Slider(
            ax=ax_r0slider,
            label="R0",
            valmin=0,
            valmax=20,
            valinit=self.r0,
            valfmt='%0.0f',
            valstep=1.0,
            orientation="vertical"
        )
        self.r0_slider.on_changed(self.r0_changed)

        # r0 delta slider
        axcolor = 'lightgrey'
        ax_r0dslider = plt.axes([0.01, 0.617, 0.015, 0.3], facecolor=axcolor)
        self.r0d_slider = Slider(
            ax=ax_r0dslider,
            label="R0\ndelta",
            valmin=0,
            valmax=10,
            valinit=self.r0_delta,
            valfmt='%0.0f',
            valstep=1.0,
            orientation="vertical"
        )
        self.r0d_slider.on_changed(self.r0_delta_changed)

        # day to immunity slider after infection
        axcolor = 'lightgrey'
        ax_dtislider = plt.axes([1-0.035, 0.6, 0.015, 0.3], facecolor=axcolor)
        self.dti_slider = Slider(
            ax=ax_dtislider,
            label="Infected\nperiod\n(days)",
            valmin=0,
            valmax=100,
            valinit=self.day_to_immunity,
            valfmt='%0.0f',
            valstep=1.0,
            orientation="vertical"
        )
        self.dti_slider.on_changed(self.daytoimmunity_changed)

        # immunity period slider
        axcolor = 'lightgrey'
        ax_ipslider = plt.axes([1 - 0.035, 0.2, 0.015, 0.3], facecolor=axcolor)
        self.ip_slider = Slider(
            ax=ax_ipslider,
            label="Immunity\nperdiod\n(days)",
            valmin=0,
            valmax=100,
            valinit=self.immunity_period,
            valfmt='%0.0f',
            valstep=1.0,
            orientation="vertical"
        )
        self.ip_slider.on_changed(self.immunityperiod_changed)

        # death probability slider
        axcolor = 'lightgrey'
        ax_dpslider = plt.axes([1 - 0.035, 0.02, 0.015, 0.11], facecolor=axcolor)
        self.dp_slider = Slider(
            ax=ax_dpslider,
            label="Death\nprob",
            valmin=0,
            valmax=1,
            valinit=self.deathprob,
            valstep=.001,
            orientation="vertical"
        )
        self.dp_slider.on_changed(self.deathproba_changed)

    def draw_texts(self, ax):
        """
        Draws text on plt: total cases and date.

        Parameters
        ----------
        ax: Axes of the plot.

        Returns
        -------
        """

        # Number of total cases
        plt.text(-.05, .2,
                 'Cases: ' + str(self.nbcases) + '/' + str(len(self.g.vertices())),
                 horizontalalignment='left',
                 verticalalignment='center',
                 color='black',
                 transform=ax.transAxes,
                 fontsize=15
                 )

        # Current day
        plt.text(-.05, .15,
                 'Day: ' + str(self.index),
                 horizontalalignment='left',
                 verticalalignment='center',
                 color='r',
                 transform=ax.transAxes,
                 fontsize=20
                 )

    def draw(self):
        """
        Draws the graph. Thanks to the vertices' positions stored, we keep the same graph layout.
        Also draw the buttons, sliders & texts.
        """

        # Set the appropriate color for each node according to its state(immune, infected, ...) to then draw the graph
        self.set_node_colors()

        # Clear the figure
        plt.clf()

        # Create axes in which the graph will fit
        ax = plt.gca()

        # Adjust canvas' size
        plt.subplots_adjust(top=.9, left=0.05, bottom=0, right=.95)

        # Draws the NetworkX graph with the same positions thanks to the node positions stored
        nx.draw(self.g_nx, cmap=plt.get_cmap('jet'), node_color=self.colors, with_labels=True, pos=self.pos,
                edge_color='#BABBC1')

        # Drawing texts, sliders and buttons
        self.draw_texts(ax)
        self.draw_sliders()
        self.draw_buttons()

    def immunityperiod_changed(self, event):
        """
        Changes the immunity_period.
        Called when the slider's value change.

        Parameters
        ----------
        event: The mpl event. Not used but because plt send it we keep a param for it.

        Returns
        -------
        """

        self.immunity_period = int(self.ip_slider.val)

    def daytoimmunity_changed(self, event):
        """
        Changes the day_to_immunity.
        Called when the slider's value change.

        Parameters
        ----------
        event: The mpl event. Not used but because plt send it we keep a param for it.

        Returns
        -------
        """

        self.day_to_immunity = int(self.dti_slider.val)

    def r0_changed(self, event):
        """
        Changes the r0
        Called when the slider's value change.

        Parameters
        ----------
        event: The mpl event. Not used but because plt send it we keep a param for it.

        Returns
        -------
        """
        
        self.r0 = int(self.r0_slider.val)

    def r0_delta_changed(self, event):
        """
        Changes the r0 delta
        Called when the slider's value change.

        Parameters
        ----------
        event: The mpl event. Not used but because plt send it we keep a param for it.

        Returns
        -------
        """

        self.r0_delta = self.r0d_slider.val

    def next(self, event=None):
        """
        Continues the spread. Calls the spread algorithm to proceed the disease spread a step forward.

        Parameters
        ----------
        event: The mpl event. Not used but because plt send it we keep a param for it. We also call this function without
                mpl but by our own and because we do not have an mpl event, we set it None by default.

        Returns
        -------
        """

        # Index/day
        self.index += 1
        print('Day:', self.index)

        # Continue the spread by calling the spread function.
        # The spread function returns a dictionnary with all the values neeeded to proceed another step later. 
        # These values are stored in this classe in `spread_attributes`.
        returned_values = self.spread(
            self.spread_attributes['g'],
            self.locked,
            self.immune,
            self.index,
            self.spread_attributes['r'],
            self.r0,
            self.r0_delta,
            self.spread_attributes['to_infect'],
            self.spread_attributes['infected'],
        )
        self.spread_attributes['to_infect'] = returned_values['to_infect']
        self.spread_attributes['infected'] = returned_values['infected']

        # Cases of the day (used in the chart)
        self.daily_cases = 0

        # Update our infected tracker : 
        # For each new infected => random number => dead ? if no then just infected.
        # As mentionned in `program.py`, a node can be in both `infected` and `to_infect` lists
            # because it cans be infected and infected other vertices.
        # Thus, we check if both lists, with making sure to not check a vertice we already checked.
        for n in self.spread_attributes['infected'] + [n for n in self.spread_attributes['to_infect'] if
                                                n not in self.spread_attributes['infected']]:

            # Add to infected dict only if not infected and note immune
            if n not in self.infected and n not in self.immune:

                # Vital prognosis engaged                
                if random.random() <= self.deathprob:
                    print('xxxx Death info:', n, "just died")
                    
                    # -1 means dead in the `infected` dictionnary
                    self.infected[n] = -1
                    self.nbdead += 1
                    
                    # Dead => remove it from the search algorithm parameters
                    if n in self.spread_attributes['to_infect']:
                        self.spread_attributes['to_infect'].remove(n)
                    if n in self.spread_attributes['infected']:
                        self.spread_attributes['infected'].remvoe(n)

                # If it survived => add to infected
                else:
                    # Key = node's name ; value = infection date.
                    self.infected[n] = self.index
                    self.nbcases += 1

                    # A new infected today
                    self.daily_cases += 1

            # Remove dead nodes from algorithm parameters
            if n in self.infected and self.infected[n] == -1:
                if n in self.spread_attributes['to_infect']: self.spread_attributes['to_infect'].remove(n)
                if n in self.spread_attributes['infected']:self.spread_attributes['infected'].remove(n)

        # Removing the infected that are immune.
        # Two steps are involved because we can't remove from a dict while 
        # looping on it. Thus, two steps:
            # 1. select them
            # 2. remove them

        # 1. select them: 
        infected_to_remove = []
        for n, d in self.infected.items():
            # lockdown enabled, not dead and pre-lockdown done => going to lockdown
            if self.lockdown != -1 and d != -1 and self.index >= d + self.lockdown:
                # Remove this vertice from the algorithm parameters
                if n in self.spread_attributes['to_infect']:
                    self.spread_attributes['to_infect'].remove(n)
                if n in self.spread_attributes['infected']:
                    self.spread_attributes['infected'].remove(n)
                
                # We set the lock date to the infection date. Thus, we keep track of when the node was infected
                # and not only when it was locked
                self.locked[n] = self.infected[n]

                # Remove the node from infected dict
                infected_to_remove.append(n)

            # lockdown disabled, not dead and pre-immune perdiod done => is now immuned
            elif self.lockdown == -1 and d != -1 and self.index >= d + self.day_to_immunity:
                # Remove this vertice from the algorithm parameters
                if n in self.spread_attributes['to_infect']:
                    self.spread_attributes['to_infect'].remove(n)
                if n in self.spread_attributes['infected']:
                    self.spread_attributes['infected'].remove(n)
                
                # The vertice is immune so we remove a case from the count.
                self.nbcases -= 1

                # Key = vertice's name; Value = current date. => we keep track of the start of immune period.
                self.immune[n] = self.index

                # Remove the node infected dict
                infected_to_remove.append(n)
        # 1. end of selection

        # 2. remove them
        for n in infected_to_remove:
            self.infected.pop(n)
        # 2. end of remove

        # Removing immune that arn't immune anymore.
        # Two steps are involved because we can't remove from a dict while 
        # looping on it. Thus, two steps:
            # 1. select
            # 2. remove

        # 1. select
        immunity_to_remove = []
        for n, d in self.immune.items():
            # Below is the condition on the date => if True then the immune period is over.
            if self.index >= d + self.immunity_period:
                immunity_to_remove.append(n)
        # 1. end of selction

        # 2. remove
        for n in immunity_to_remove:
            self.immune.pop(n)
        # 2. end of remove

        # Unlocking the locked nodes.
        # Two steps are involved because we can't remove from a dict while 
        # looping on it. Thus, two steps:
        #   1. Select the nodes
        #   2. Remove them

        # 1. Select
        node_to_unlock = []
        for key, value in self.locked.items():
            # Below is the condition on the date => if True then the lockdown period is over.
            if self.index >= self.day_to_immunity + value:
                print('!!!!!', key)
                node_to_unlock.append(key)

                # When going out of lockdown => we are immune
                self.immune[key] = self.index

                # Immune => remove a case from count
                self.nbcases -= 1
        # 1. End of selection

        # 2. remove
        for n in node_to_unlock:
            self.locked.pop(n)
        # 2. end of remove

        # DEBUG IN CONSOLE: all the locked vertices and the date of their lockdown's start.
        print('--')
        for k, v in self.locked.items():
            print(k, v)
        print('--')

        # DEBUG IN CONSOLE: total amount of infected, dead, immuned. 
        print('+++++Nb Info:', self.nbcases, 'infected')
        print('+++++Nb Info:', self.nbdead, 'dead')
        print('++++ Nb Info:', len(list(self.immune.keys())), 'immuned')
        print()

        # Makes it possible to the main loop to detect changed and redraw.
        self.change = True

    def last_action(self, event):
        """
        Called by the Auto button, starts the automatic process.

        Parameters
        ----------
        event: The mpl event. Not used but because plt send it we keep a param for it.

        Returns
        -------
        """

        # We launch the automatic by unstopping it then activate it
        self.is_stopped = False
        self.is_auto = True

    def check_auto(self):
        """
        Checks if the algorithm is in auto mode.

        Returns
        -------
        boolean: is the algorithm in auto mode ?
        """

        # If no one is infected and the population is 100% normal (or immunen) then it's over.
        # Indeed, no more infections are possible.
        # Thus, returns False
        if self.color_pallet['infected'] not in self.colors and not (
                self.color_pallet['normal'] in self.colors and self.color_pallet['immune'] in self.colors): 
                return False
        
        # Otherwise, returns True
        return True

    def stop(self, event):
        """
        Shutdowns the auto mode by changing values. Thus, the loop will detect it.

        Parameters
        ----------
        event: The mpl event. Not used but because plt send it we keep a param for it.

        Returns
        -------
        """

        print("stop auto")
        self.is_stopped = True
        self.is_auto = False

    def deathproba_changed(self, event):
        """
        Calls when the slider's value changed.

        Parameters
        ----------
        event: The mpl event. Not used but because plt send it we keep a param for it.

        Returns
        -------
        """

        # Getting the value from the slider. Keeping the float value.
        self.deathprob = self.dp_slider.val

    def close(self, event):
        """
        Closes the windows. Called by the Close button.

        Parameters
        ----------
        event: The mpl event. Not used but because plt send it we keep a param for it.

        Returns
        -------
        """

        self.closing = True
        self.is_auto = False
        
        # Asks plt to close all the windows.
        plt.close('all')


def show_graph(g, spread_func, root, animation_time, chart, lockdown):
    """
    Main function of `visual.py`.
    Creates the NetworkX graph based on `g` and create a State instance to show graph.
    The graph (aka State instance) will use the chart given as its instantce to give all values.

    Parameters
    ----------
    g: type Graph_dict: The graph to create the NetworkX graph and where we search with the algorithm.
    spread_fun: A function to handle the spread.
    animation_time: type float: Time between 2 frames of auto_mode.
    chart: The instance of the chart (created in `program.py`)
    lockdown: type int: The lockwdown duration. Or -1 if lockdown is disabled.

    Returns
    -------
    """

    # Networkx Graph setup
    # First we create the graph instance
    g_nx = nx.Graph()

    # The, from our Graph_dict we add each edge to the NetworkX graph.
    for vertice in g.vertices():
        for n in g.neighbors(vertice):
            g_nx.add_edge(vertice, n)

    # Plot setup: windows' id, (height, width)
    fig = plt.figure(num=0, figsize=(9, 10))

    # Creating an instance of State to keep track of the state of the graph.
    state = State(g, g_nx, spread_func, root, animation_time, chart, lockdown)
    # Finally, we start the main loop of the graph that handles changes.
    state.start_loop()
