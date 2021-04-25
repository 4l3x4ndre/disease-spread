import database as db
import graph
import visual as gui
import random
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-animt', type=float, default=1, help='auto animation time')
parser.add_argument('-root', type=str, default='', help='root: the firt infected')
parser.add_argument('-db', type=str, default='got', help='database: accept : got / trump / marvel')

def create_graph(vertices_db, edges_db):
    g = graph.Graph_dic()
    edges = edges_db.select_item()
    for e in edges:
        # e is an item of the databse: (person1, person2)
        # To create a link between them we simply get their name
        g.add_edge(e[0], e[1])

    return g


def breadth_first_search(g, root):
    queue = [root]
    checked = []

    while len(queue) > 0:
        vertice = queue.pop(0)
        for n in g.neighbors(vertice):
            if n not in checked:
                queue.append(n)
        checked.append(vertice)

    return checked


def breadth_first_search_step_by_step(g, immune, step_id, root, r0, r0_delta, queue=[], checked=[]):
    """
    Executing a step of breadth first search from the graph g starting at root with known states queue and checked.
    R0 and r0_delta are used to spread the disease.
    """
    # Initialization
    if step_id == 0 and queue == [] and checked == []:
        queue = [root]
        checked = []

    # New queue to return, used to keep track of the current search's state
    new_queue = []

    # Starting the breadth first search
    while len(queue) > 0:

        # Get the current vertice to get its neighbors
        vertice = queue.pop(0)
        neighbors = g.neighbors(vertice)

        # Set a r0
        random_r0 = int(random.uniform(r0 - r0_delta, r0 + r0_delta))
        print('~~~~ Spread Info:', vertice, 'contaminated', random_r0, 'people')

        # We check as many nodes as random_r0 allows us, but we are limited by the number of neighbors
        length = min(random_r0, len(neighbors))

        # We will remove nodes, so we need to keep a copy (python way)
        neighbors_copy = [n for n in neighbors]

        # Checking neighbors according to the r0 possibilty
        for i in range(length):

            # We select a random neighbors to infect
            n = neighbors_copy.pop(random.randint(0, len(neighbors_copy) - 1))
            if n not in checked and n not in new_queue and not n in immune:
                new_queue.append(n)

        # Add the vertice to the queue because it can infect other nodes
        # It will be remove when needed by the Next function of visual.py
        if not vertice in new_queue:
            new_queue.append(vertice)
        # The current vertice has been infected 
        elif vertice not in checked:
            checked.append(vertice)

    return {'g': g, 'id': step_id + 1, 'r': root, 'q': new_queue, 'c': checked}


def main():
    # Get arguments
    args = parser.parse_args()

    # Load the two main databases from which we create the graph
    db_name = args.db
    if db_name == 'got':
        vert_db = db.Database('got_vertices')
        edges_db = db.Database('got_edges')
    elif db_name == 'trump':
        vert_db = db.Database('trump_vertices')
        edges_db = db.Database('trump_edges')
    elif db_name == 'marvel':
        vert_db = db.Database('marvel_vertices')
        edges_db = db.Database('marvel_edges')
    else:
        vert_db = db.Database(db_name + '_vertices')
        edges_db = db.Database(db_name + '_edges')


    # Create the graph
    g = create_graph(vert_db, edges_db)

    # The root is the starting point of the spread
    # if None, get a random starting point
    root = args.root
    if root == '':
        root = g.vertices()[random.randin(0, len(g.vertices())-1)]

    # Start the GUI process to render the spread
    gui.show_graph(g, breadth_first_search_step_by_step, root, abs(args.animt))


if __name__ == '__main__':
    main()
