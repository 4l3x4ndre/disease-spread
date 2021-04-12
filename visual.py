import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button


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

        # Drawing
        self.draw()

    def draw(self):
        """
        Draw the graph with the positions stored.
        """
        # Change the color, status, ...
        for node_checked in self.spread_attributes['q']:
            for i in range(len(list(self.g_nx.nodes))):
                node_nx = list(self.g_nx.nodes)[i]
                if node_checked == node_nx:
                    self.colors[i] = '#FF4348'
                    break

        # Clear the figure
        plt.clf()

        # Draw the networkx graph with the same position
        nx.draw(self.g_nx, cmap = plt.get_cmap('jet'), node_color = self.colors, with_labels=True, pos=self.pos, edge_color='#BABBC1')
    
        # Button to continue the spread ([x0, y0, width, height])
        axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
    
        # Reference to the button need to stay inside the class
        self.bnext = Button(axnext, 'Next')
        self.bnext.on_clicked(self.next)
    
        # Show the result
        plt.show()
    

    def next(self, event):
        """
        Continue the spread.
        """
        self.index += 1
        print('step number', self.index)

        # Contiunue the spread
        self.spread_attributes = self.spread(
                self.spread_attributes['g'],
                self.spread_attributes['id'],
                self.spread_attributes['r'],
                self.spread_attributes['q'],
                self.spread_attributes['c']
        ) 

        self.draw()


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
    fig = plt.figure(figsize=(20, 10), edgecolor='y')
    
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
