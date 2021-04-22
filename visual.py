import networkx as nx
import matplotlib as mpl
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider, Rectangle
import time


class State:
    def __init__(self, g, g_nx, spread_func, root):
        self.index = 0
        self.g = g
        self.g_nx = g_nx
        self.root = root

        # Positions of the nodes to keep them in the same place and not
        # redraw completely the graph
        self.pos = nx.fruchterman_reingold_layout(self.g_nx)

        # Keep track of graph colors
        self.colors = ['#35FFAD' for i in range(self.g_nx.number_of_nodes())]

        # Spread function to create a step by step spread
        self.spread = spread_func
        self.spread_attributes = {'g':g, 'id':0, 'r':root, 'q':[root], 'c':[]}

        # Infected nodes: {node_name: day of infection}
        # With the day, we can create an immunity system
        self.infected = {}

        # Values that will be modified
        self.r0 = 3 
        self.r0_delta = 3
        # Day to immunity (DTI)
        self.day_to_immunity = 3
        # Immunity period in days
        self.immunity_period = 10

        # Colors
        self.color_pallet = {
            "normal": "#35FFAD", # also in self.colors
            "infected": "#FF4348",
            "immune": "#7B02FF"
        }

        # General infos
        self.is_shutdown = False

        # Drawing
        self.draw()

    def draw(self):
        """
        Draw the graph with the positions stored.
        """

        # Set color to normal when the immunity is gone
        for i in range(len(list(self.g_nx.nodes))):
            nodex = list(self.g_nx.nodes)[i]
            if nodex not in self.infected:
                self.colors[i] = self.color_pallet['normal']


        # Change the color for the checked ones
        for node_checked in self.spread_attributes['q']:
            for i in range(len(list(self.g_nx.nodes))):
                node_nx = list(self.g_nx.nodes)[i]
                if node_checked == node_nx:
                    self.colors[i] = self.color_pallet['infected']
                    break

        # Immune color
        for node, d in self.infected.items():
            # In that case, the current node is not immune yet
            if self.index < d + self.day_to_immunity: continue

            for i in range(len(list(self.g_nx.nodes))):
                node_nx = list(self.g_nx.nodes)[i]
                if node == node_nx:
                    self.colors[i] = self.color_pallet['immune']
                    break

        # Clear the figure
        plt.clf()

        # Adjust canvas size
        plt.subplots_adjust(top=.9, left=0.05, bottom=0, right=.95)
        
        # Create axes in which the graph will fit
        ax = plt.gca()

        # To have the number of cases
        infected = self.spread_attributes['q'] + [x for x in self.spread_attributes['c'] if x not in self.spread_attributes['q']]

        # Stats on the spread
        plt.text(-.05,.2,
                'Cases: ' + str(len(infected)) + '/' + str(len(self.g.vertices())),
                horizontalalignment='left',
                verticalalignment='center', 
                color='black', 
                transform=ax.transAxes,
                fontsize = 15
        )

        # Text to keep track of days
        plt.text(-.05,.15,
            'Day: ' + str(self.index),
            horizontalalignment='left',
            verticalalignment='center',
            color='r',
            transform=ax.transAxes,
            fontsize = 20
        )

        # Draw the networkx graph with the same position thanks to the node positions stored
        nx.draw(self.g_nx, cmap = plt.get_cmap('jet'), node_color = self.colors, with_labels=True, pos=self.pos, edge_color='#BABBC1')
    
        # Button to continue the spread ([x0, y0, width, height])
        b_axnext = plt.axes([0.002, 0.02, 0.05, 0.025])
    
        # Reference to the button need to stay inside the class
        self.bnext = Button(b_axnext, 'Next')
        self.bnext.on_clicked(self.next)

        # Button to transit to the end
        b_axend = plt.axes([0.002, 0.05, 0.05, 0.025])
        #Reference to that button
        self.bend = Button(b_axend, 'Auto')
        self.bend.on_clicked(self.last_action)

        # Button to stop everything
        b_axstop = plt.axes([0.002, 0.08, 0.05, 0.025])
        #Reference to that button
        self.bstop = Button(b_axstop, 'Stop')
        self.bstop.on_clicked(self.shutdown)
        
        # r0 slider
        axcolor = 'lightgrey'
        ax_r0slider = plt.axes([0.01, 0.25, 0.015, 0.3], facecolor=axcolor)
        self.r0_slider = Slider(
            ax=ax_r0slider,
            label="R0",
            valmin=0,
            valmax=10,
            valinit=self.r0,
            valfmt='%0.0f',
            valstep =1.0,
            orientation="vertical"
        )
        self.r0_slider.on_changed(self.r0_changed)

        # day to immunity slider
        axcolor = 'lightgrey'
        ax_dtislider = plt.axes([0.01, 0.617, 0.015, 0.3], facecolor=axcolor)
        self.dti_slider = Slider(
            ax=ax_dtislider,
            label="Infected\nperiod\n(days)",
            valmin=0,
            valmax=10,
            valinit=self.day_to_immunity,
            valfmt='%0.0f',
            valstep =1.0,
            orientation="vertical"
        )
        self.dti_slider.on_changed(self.daytoimmunity_changed)

        
        # immunity period slider
        axcolor = 'lightgrey'
        ax_ipslider = plt.axes([1-0.035, 0.25, 0.015, 0.5], facecolor=axcolor)
        self.ip_slider = Slider(
            ax=ax_ipslider,
            label="Immunity\nperdiod\n(days)",
            valmin=0,
            valmax=100,
            valinit=self.immunity_period,
            valfmt='%0.0f',
            valstep =1.0,
            orientation="vertical"
        )
        self.ip_slider.on_changed(self.immunityperiod_changed)

        # Show the result
        plt.show()
   
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

        # Updating our delta: min and max infections that are possible for the same node
        self.r0_delta = int(self.r0/2)


    def next(self, event=None):
        """
        Continue the spread.
        """
        # Index/day
        self.index += 1

        # Continue the spread by calling the spread function
        self.spread_attributes = self.spread(
                self.spread_attributes['g'],
                self.spread_attributes['id'],
                self.spread_attributes['r'],
                self.r0,
                self.r0_delta,
                self.spread_attributes['q'],
                self.spread_attributes['c']
        ) 
        
        # Update our infected tracker : new infected => current day
        for n in self.spread_attributes['c'] + [n for n in self.spread_attributes['q'] if n not in self.spread_attributes['c']]:
            if n not in self.infected:
                self.infected[n] = self.index
            else: 
                # if its already infected, then check if the immune is over
                # that's right we could have done that somewhere else
                if self.index >= self.infected[n] + self.day_to_immunity + self.immunity_period:
                    self.infected.pop(n)
                    if n in self.spread_attributes['c']: self.spread_attributes['c'].remove(n)
                    if n in self.spread_attributes['q']: self.spread_attributes['q'].remove(n)


        # Debug infected
        print('////////////////////////')
        for n, d in self.infected.items():
            print(n, d)
        print(len(list(self.infected.keys())))
        print('////////////////////////')

        # Debug info
        print('############################# start checked')
        print(self.spread_attributes['c'])
        print('############################# start queued')
        print(self.spread_attributes['q'])


        # Drawing after update
        self.draw()


    def last(self):
        """
        Go to the last cases.
        lasttime: time in seconds of the previous call. Default is -1
        """

        if self.is_shutdown: return

        # If no one is infected and the population ir 100% normal (or immune) then it's over
        if self.color_pallet['infected'] not in self.colors and not (self.color_pallet['normal'] in self.colors and self.color_pallet['immune'] in self.colors): return
       
        # Proceding the next spread step
        self.next()

        # Wait 1 seconds
        # time.sleep() can't be use, with matplotlib we need to use plt.pause(t) with t in seconds
        plt.pause(1)

        # Recursion
        self.last()

    
    def last_action(self, event):
        """
        Called by a button, start the automatic process.
        """

        # Allow the automatic process to happen
        self.is_shutdown = False

        # Calling the function that recall itself
        self.last()


    def shutdown(self, event):
        """
        Shutdown (just a value) the process.
        """
        print("shutting down")
        self.is_shutdown = True


def show_graph(g, spread_func, root):

    
    # Networkx Graph setup
    g_nx = nx.Graph()
    for vertice in g.vertices():
        for n in g.neighbors(vertice):
            g_nx.add_edge(vertice, n)

    print(
            g_nx.number_of_nodes(),
            g_nx.number_of_edges()
    )

    # Plot setup (height, width)
    fig = plt.figure(figsize=(15, 7))
    
    # Creating an instance of State to keep track of the state of the graph
    state = State(g, g_nx, spread_func, root)


# What follow isn't used. It is just a basic understanding of Tkinter
'''
from tkinter import *
def test_with_tkinter(g):
    window = Tk()
    window.geometry("2500x750")
    
    # Label is the title inside the window
    label = Label(window, text="Disease Spread")
    label.pack()
    
    
    canvas = Canvas(window, width=450, height=400, bg='ivory')

    # Graph creation
    n = g.nb_neighbors()
    
    # Dot size
    padding = 5
    canvas_padding = 10
    window.update()
    ds = (window.winfo_width()-4*canvas_padding)/(n+padding)
    for i in range(n):
        x, y = canvas_padding + i*(ds+padding), 50
        canvas.create_oval(x, y, x+ds, y+ds, fill='green')
    
    


    # End graph creation

    canvas.pack(side=TOP, padx=canvas_padding, pady=canvas_padding, fill=BOTH, expand=YES)
    
    Button(window, text ='Next').pack(side=LEFT, padx=5, pady=5)
   
    window.mainloop()
'''
