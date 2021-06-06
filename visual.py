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
        self.spread_attributes = {'g': g, 'id': 0, 'r': root, 'q': [root], 'c': []}

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
        # Death probability when infected
        self.deathprob = .1

        # Colors
        self.color_pallet = {
            "normal": "#35FFAD",
            "infected": "#FF4348",
            "immune": "#7B02FF",
            "dead": "#000000",
            "lockdown" : "#A19DA4"
        }

        # General infos
        self.is_stopped = False
        self.is_auto = False
        self.closing = False
        self.change = True
        self.lockdown = lockdown

        # Time between frames
        self.anim_time = anim_time

        # The number of cases, updated in the 'next' method
        self.nbcases = 1  # the first one is the root
        self.nbdead = 0 

        # Chart to plot spread numbers
        self.chart = chart

    def start_loop(self):
        """
        Start the infinite loop to handle changes and draw them
        """
        self.loop()

    def loop(self):
        """
        The main loop to maintain the plt on
        """

        # While we did not press the close button -> continue the loop
        while not self.closing:
            # True when pressing next
            if self.change:
                self.change = False
                self.draw()
            # True when pressing auto
            elif self.is_auto:
                # Check if the auto should stop
                if not self.check_auto():
                    self.is_auto = False
                    continue
                self.next()
                self.change = False
                self.draw()
                plt.pause(self.anim_time)

            # Draw then pause
            plt.draw()
            plt.pause(.5)

    def update_chart(self, day, total, daily, dead, immune):
        """
        Call chart functions to upadte the chart
        day: the index of the current day
        other params: spread numbers
        """
        self.chart.add_values(day, total, daily, dead, immune)

    def set_node_colors(self):
        """
        Set colors according to immune/normal or infected/dead
        """

        # immune/normal
        for i in range(len(list(self.g_nx.nodes))):
            nodex = list(self.g_nx.nodes)[i]  # node name

            # if in immune array -> node is immune
            if nodex in self.immune:
                self.colors[i] = self.color_pallet['immune']
            # if under lockdown
            elif nodex in self.locked:
                self.colors[i] = self.color_pallet['lockdown']
            elif nodex in self.infected:
                if self.infected[nodex] == -1:
                    self.colors[i] = self.color_pallet['dead']
                else:
                    self.colors[i] = self.color_pallet['infected']
            else:
                self.colors[i] = self.color_pallet['normal']
        

    def draw_buttons(self):
        """
        Draw all buttons in plt.
        """
        # Button to continue the spread ([x0, y0, width, height])
        b_axnext = plt.axes([0.002, 0.02, 0.05, 0.025])
        # Reference to the button need to stay inside the class
        self.bnext = Button(b_axnext, 'Next')
        self.bnext.on_clicked(self.next)

        # Button to transit to the end
        b_axend = plt.axes([0.002, 0.05, 0.05, 0.025])
        # Reference to that button
        self.bend = Button(b_axend, 'Auto')
        self.bend.on_clicked(self.last_action)

        # Button to stop everything
        b_axstop = plt.axes([0.002, 0.08, 0.05, 0.025])
        # Reference to that button
        self.bstop = Button(b_axstop, 'Stop')
        self.bstop.on_clicked(self.stop)

        # Button to close
        b_axclose = plt.axes([1 - 0.05, 1 - 0.025, 0.05, 0.025])
        # Reference to that button
        self.bclose = Button(b_axclose, 'Close')
        self.bclose.on_clicked(self.close)

    def draw_sliders(self):
        """
        raw all sliders in plt.
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

        # day to immunity slider
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
        Draw all texts in plt.
        ax: the plot ax
        """

        # Stats on the spread
        plt.text(-.05, .2,
                 'Cases: ' + str(self.nbcases) + '/' + str(len(self.g.vertices())),
                 horizontalalignment='left',
                 verticalalignment='center',
                 color='black',
                 transform=ax.transAxes,
                 fontsize=15
                 )

        # Text to keep track of days
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
        Draw the graph with the positions stored as well as buttons/texts/sliders.
        """

        # Set the appropriate color for each node according to its state(immune, infected, ...) to then draw the graph
        self.set_node_colors()

        # Clear the figure
        plt.clf()

        # Create axes in which the graph will fit
        ax = plt.gca()

        # Adjust canvas size
        plt.subplots_adjust(top=.9, left=0.05, bottom=0, right=.95)

        # Draw the networkx graph with the same position thanks to the node positions stored
        nx.draw(self.g_nx, cmap=plt.get_cmap('jet'), node_color=self.colors, with_labels=True, pos=self.pos,
                edge_color='#BABBC1')

        self.draw_texts(ax)
        self.draw_sliders()
        self.draw_buttons()

    def immunityperiod_changed(self, event):
        """
        Change the immunity_period.
        Called when the slider's value change.
        """
        self.immunity_period = int(self.ip_slider.val)

    def daytoimmunity_changed(self, event):
        """
        Change the day_to_immunity.
        Called when the slider's value change.
        """
        self.day_to_immunity = int(self.dti_slider.val)

    def r0_changed(self, event):
        """
        Change the r0
        Called when the slider's value change.
        """
        # Converting the value of the slider in int as we need a int r0
        self.r0 = int(self.r0_slider.val)

    def r0_delta_changed(self, event):
        """
        Change the r0 delta
        Called when the slider's value change.
        """
        self.r0_delta = self.r0d_slider.val

    def next(self, event=None):
        """
        Continue the spread.
        """
        # Index/day
        self.index += 1
        print('Day:', self.index)

        # Continue the spread by calling the spread function
        r = self.spread(
            self.spread_attributes['g'],
            self.locked,
            self.immune,
            self.index,
            self.spread_attributes['r'],
            self.r0,
            self.r0_delta,
            self.spread_attributes['q'],
            self.spread_attributes['c'],
        )
        self.spread_attributes['q'] = r['q']
        self.spread_attributes['c'] = r['c']

        # Case of the day (used in the chart)
        daily_cases = 0

        # Update our infected tracker : new infected => current day or dead
        for n in self.spread_attributes['c'] + [n for n in self.spread_attributes['q'] if
                                                n not in self.spread_attributes['c']]:

            # Add to infected dict only if not infected and note immune
            if n not in self.infected and n not in self.immune:
                # Vital prognosis engaged                
                if random.random() <= self.deathprob:
                    print('xxxx Death info:', n, "just died")
                    # -1 means dead
                    self.infected[n] = -1
                    self.nbdead += 1
                    
                    # Dead => remove it from the search algorithm parameters
                    if n in self.spread_attributes['c']:
                        c = self.spread_attributes['c'].copy()
                        c.remove(n)
                        self.spread_attributes['c'] = c.copy()
                    if n in self.spread_attributes['q']:
                        c = self.spread_attributes['q'].copy()
                        c.remove(n)
                        self.spread_attributes['q'] = c.copy()

                # If it survive => add to infected
                else:
                    self.infected[n] = self.index
                    self.nbcases += 1

                    # A new infected today
                    daily_cases += 1

            # Remove dead nodes from algorithm parameters
            elif n in self.infected and self.infected[n] == -1:
                if n in self.spread_attributes['c']:
                    c = self.spread_attributes['c'].copy()
                    c.remove(n)
                    self.spread_attributes['c'] = c.copy()
                if n in self.spread_attributes['q']:
                    c = self.spread_attributes['q'].copy()
                    c.remove(n)
                    self.spread_attributes['q'] = c.copy()

        # Remove the infected that are immune
            # 1. select them
            # 2. remove them
        # 1. select them
        infected_to_remove = []
        for n, d in self.infected.items():
            # lockdown enabled
            if self.lockdown != -1 and d != -1 and self.index >= d + self.lockdown:
                if n in self.spread_attributes['c']:
                    c = self.spread_attributes['c'].copy()
                    c.remove(n)
                    self.spread_attributes['c'] = c.copy()
                if n in self.spread_attributes['q']:
                    c = self.spread_attributes['q'].copy()
                    c.remove(n)
                    self.spread_attributes['q'] = c.copy()
                # We set the lock date to the infection date. Thus, we keep track of when the node was infected
                # and not only when it was locked
                self.locked[n] = self.infected[n]
                infected_to_remove.append(n)
            # immune
            elif (self.lockdown == -1 and d != -1 and self.index >= d + self.day_to_immunity):
                if n in self.spread_attributes['c']:
                    c = self.spread_attributes['c'].copy()
                    c.remove(n)
                    self.spread_attributes['c'] = c.copy()
                if n in self.spread_attributes['q']:
                    c = self.spread_attributes['q'].copy()
                    c.remove(n)
                    self.spread_attributes['q'] = c.copy()
                self.nbcases -= 1
                self.immune[n] = self.index
                infected_to_remove.append(n)


        # 2. remove them
        for n in infected_to_remove:
            self.infected.pop(n)

        # Remove immune that arn't immune anymore
            # 1. select
            # 2. remove
        # 1. select
        immunity_to_remove = []
        for n, d in self.immune.items():
            if self.index >= d + self.immunity_period:
                immunity_to_remove.append(n)

        # 2. remove
        for n in immunity_to_remove:
            self.immune.pop(n)

        # unlock locked nodes
        node_to_unlock = []
        for key, value in self.locked.items():
            if self.index >= self.day_to_immunity + value:
                print('!!!!!', key)
                node_to_unlock.append(key)
                self.immune[key] = self.index
                self.nbcases -= 1

        for n in node_to_unlock:
            self.locked.pop(n)

        print('--')
        for k, v in self.locked.items():
            print(k, v)
        print('--')

        # Infos 
        print('+++++Nb Info:', self.nbcases, 'infected')
        print('+++++Nb Info:', self.nbdead, 'dead')
        print('++++ Nb Info:', len(list(self.immune.keys())), 'immune')
        print()

        # Make it possible to the loop to detect changed        
        self.change = True

        # Update chart to display new spread numbers
        self.update_chart(self.index, self.nbcases, daily_cases, self.nbdead, len(list(self.immune.keys())))

    def last_action(self, event):
        """
        Called by a button, start the automatic process.
        """

        # We launch the automatic by unstopping it then activate it
        self.is_stopped = False
        self.is_auto = True

    def check_auto(self):
        # If no one is infected and the population ir 100% normal (or immune) then it's over
        if self.color_pallet['infected'] not in self.colors and not (
                self.color_pallet['normal'] in self.colors and self.color_pallet['immune'] in self.colors): return False
        return True

    def stop(self, event):
        """
        Shutdown (just a value) the process.
        """
        print("stop auto")
        self.is_stopped = True
        self.is_auto = False

    def deathproba_changed(self, event):
        """
        Call when the slider's value changed.
        """
        self.deathprob = self.dp_slider.val

    def close(self, event):
        """
        Close the windows.
        Called by a button.
        """
        self.closing = True
        self.is_auto = False
        plt.close('all')


def show_graph(g, spread_func, root, animation_time, chart, lockdown):
    """
    Display the graph
    Called from program.py
    g: the graph
    spread_fun: the spread algorithm to use (function to call)
    root: the origin of the spread
    animation_time: time between frames
    """

    # Networkx Graph setup
    g_nx = nx.Graph()
    for vertice in g.vertices():
        for n in g.neighbors(vertice):
            g_nx.add_edge(vertice, n)

    # Plot setup (height, width)
    fig = plt.figure(figsize=(15, 7))

    # Creating an instance of State to keep track of the state of the graph
    state = State(g, g_nx, spread_func, root, animation_time, chart, lockdown)
    state.start_loop()
