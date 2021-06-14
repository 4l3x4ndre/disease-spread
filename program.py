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


def breadth_first_search_step_by_step(g, locked, immune, step_id, root, r0, r0_delta, to_infect=[], infected=[]):
    """
    The explanations below will mention a queue as if it was a variable. In fact, it is! The variable 'to_infect'
    represents a queue of all the node that we will infect. Let's dive into the mechanism.

    Executes a step of a breadth first search in the graph 'g' starting at 'root' with know states.
    The idea is the following:
        1) at start, no infected. Just the root in queue.
        2) each call of this function represents a step in the search (the spread).
            2) A) We unqueue a vertice
            2) B) Then we infect some of its neighbors
                Because scientifically, the r0 is an average, in this project we first define it, then we define
                its variation: the r0_delta.
                Doing so, each vertice can infect a random number of vertices between: r0 - r0_delta and r0 + r0_delta.
                Thus, during the spread of the disease, if we calculate the r0 manually (average of the number of
                infected by vertice) we will find the r0 we defined earlier.
            2) C) And we add them to the queue, to check later their own neighbors
        3) At the end of the step, we return all information needed to call the function later at the same step.

    WARNING: A vertice can be queued and infected.
    Indeed, being queued means that at the next step we will be infected.
    So, during the next step we are infected. But during this step (where we are infected) the algorithm also selects
    our neighbors to infect during the next step.
    However, not all of our neighbors are necessarily infected! As mentioned we select randomly the neighbors to infect.
    Thus, we can be queued (again), because we are still infected and not all of our neighbors are infected !

    Parameters
    ----------
    g: type Graph_dict: The graph in which we search.
    locked: type list: Vertices under lockdown -> they can not infect other vertices.
    immune: type list: Vertices immuned -> they can not infect other vertices.
    step_id: type int: The n° of the current step. Used to identify the first call.
    root: Name of the first infected vertice.
    r0: type int: The r0 of the spread.
    r0_delta: type int: The delta/variation of the r0
    to_infect: type list: A list of all the neighbors that has been selected to be infected later on.
    infected: type list: A list of all the infected nodes.

    Returns
    -------
    type dict: a dictionnary with all the values that need to be sent to call the function later.
    """

    # Initialization: step 0 => The beginning => No one is infected and queued except the root.
    if step_id == 0 and len(to_infect) == 0 and len(infected) == 0:
        to_infect = [root]


    # New queue to return, used to keep track of the current search's state for the next call of the function.
    to_infect_next_step = []

    # Starting the breadth first search. Continue untill we visit all of the vertices to infect for this step.
    while len(to_infect) > 0:

        # Get the current vertice to get its neighbors
        vertice = to_infect.pop(0)
        neighbors = g.neighbors(vertice)

        # Set a r0
        random_r0 = int(random.uniform(r0 - r0_delta, r0 + r0_delta))
        print('~~~~ Spread Info:', vertice, 'will contaminate', random_r0, 'people')

        # We check as many nodes as random_r0 allows us, but we are limited by the number of neighbors of this vertice.
        # So, we use the minimum to avoid selecting outside of 'neighbors' array.
        length = min(random_r0, len(neighbors))

        # We will remove nodes, so we need to keep a copy (python way)
        neighbors_copy = [n for n in neighbors]

        # Checking neighbors according to the r0 possibilty
        for i in range(length):

            # We select a random neighbors to infect
            n = neighbors_copy.pop(random.randint(0, len(neighbors_copy) - 1))

            # And we add it to the queue of the next step.
            if n not in infected and n not in to_infect_next_step and n not in immune and n not in locked:
                to_infect_next_step.append(n)

        # UNTIL THE CURRENT VERTICE IS INFECTED, IT MEANS IT HAS THE POSSIBILITY TO INFECT ITS NEIGHBORS DURING
        # UPCOMING STEPS. SO WE KEEP THIS NODE INSIDE THE QUEUE DURING ALL ITS INFECTION.
        # It will be remove when needed by the next function of 'visual.py' according to its state (immune, locked, ...)
        if vertice not in to_infect_next_step:
            to_infect_next_step.append(vertice)
        # Moreover, the current vertice is infected so we add it to the list of infected vertices
        if vertice not in infected:
            infected.append(vertice)

    return {'g': g, 'id': step_id + 1, 'r': root, 'to_infect': to_infect_next_step, 'infected': infected}


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
        root = g.vertices()[random.randint(0, len(g.vertices()) - 1)]

    # Chart to plot spread numbers
    chart_instance = chart.Chart()

    # Start the GUI process to render the spread
    gui.show_graph(g, breadth_first_search_step_by_step, root, abs(args.animationtime), chart_instance, args.lockdown)


if __name__ == '__main__':
    main()
