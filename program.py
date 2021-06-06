import database as db
import graph
import visual as gui
import chart
import random
import argparse

# ArgumentParser is used to get the command line options from the terminal.
parser = argparse.ArgumentParser(
    description='Start a vizualisation of a virus spread',
    epilog='Any questions? Refers to the GitHub page for information and contact'
)
# We are here intializing all of the possible options.
parser.add_argument(
    '-t',
    '--animationtime',
    type=float,
    default=1,
    help='auto animation time'
)
parser.add_argument(
    '-r',
    '--root',
    type=str,
    default='',
    help='the firt infected node. Default is random'
)
parser.add_argument(
    '-db',
    '--database',
    type=str,
    default='got',
    help='Default accept: got / trump / marvel. Refer to the GitHub page.'
)
parser.add_argument(
    '-l',
    '--lockdown',
    type=int,
    default=-1,
    help='Number of days between infection day and start of lockdown. By default lockdown is disable.'
)


def create_graph(edges_db):
    """
    Creates a graph representing the database.
    Parameters
    ----------
    edges_db: type Database: database of all links between people.

    Returns
    -------
    type Graph_dict

    """

    g = graph.Graph_dic()
    edges = edges_db.select_item()

    for e in edges:
        # e is an item of the databse: (person1, person2)
        # To create a link between them we simply get the name of the two person to link
        g.add_edge(e[0], e[1])

    return g


def breadth_first_search(g, root):
    """
    Simple search used in testing.
    Parameters
    ----------
    g: type Graph_dict: graph in which we want to search
    root: The name of the starting vertice.

    Returns
    -------
    type list: List of the all the vertices checked, order by chronology of reaching.

    """
    queue = [root]
    checked = []

    while len(queue) > 0:
        vertice = queue.pop(0)
        for n in g.neighbors(vertice):
            if n not in checked:
                queue.append(n)
        checked.append(vertice)

    return checked


def breadth_first_search_step_by_step(g, locked, immune, step_id, root, r0, r0_delta, queue=[], checked=[]):
    """
    Executes a step of breadth first search from the graph g starting at root with known states queue and checked.
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
            if n not in checked and n not in new_queue and not n in immune and not n in locked:
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

    # Show the usage of the command if no options were used (we can imagine that the user doesn't know how to use it).
    if args.database == 'got' and args.root == '' and args.animationtime == 1:
        print(parser.print_help())

    # Load the main database we are going to use to create the graph
    db_name = args.database
    edges_db = None
    if db_name == 'got':
        edges_db = db.Database('got_edges')
    elif db_name == 'trump':
        edges_db = db.Database('trump_edges')
    elif db_name == 'marvel':
        edges_db = db.Database('marvel_edges')
    else:
        edges_db = db.Database(db_name + '_edges')

    # Create the graph
    g = create_graph(edges_db)

    # The root is the starting point of the spread
    # if None, get a random starting point
    root = args.root
    if root == '':
        root = g.vertices()[random.randint(0, len(g.vertices())-1)]

    # Chart to plot spread numbers
    chart_instance = chart.Chart()

    # Start the GUI process to render the spread
    gui.show_graph(g, breadth_first_search_step_by_step, root, abs(args.animationtime), chart_instance, args.lockdown)


if __name__ == '__main__':
    main()
