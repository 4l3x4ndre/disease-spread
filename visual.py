import networkx as nx
import matplotlib.pyplot as plt


def draw(g):
    g_nx = nx.Graph()
    for vertice in g.vertices():
        for n in g.neighbors(vertice):
            g_nx.add_edge(vertice, n)
    print(
            g_nx.number_of_nodes(),
            g_nx.number_of_edges()
    )

    colors = [0.25 for v in g.vertices()]
    nx.draw(g_nx, cmap = plt.get_cmap('jet'), node_color = colors)
    plt.show()


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
