import database as db
import graph


def create_graph(database_edges):
    """
    Creation of a graph (using dict) representing the database.

    Parameters
    ----------
    database_edges: type Database: database of links between people.

    Returns
    -------
    g: type Graph_dict: graph representation using dictionnaries.
    """

    # Initialization of the graph using Graph_dict class
    g = graph.Graph_dic()

    # Selection of all the social links
    edges = database_edges.select_item()

    # edges is a list of links represented by tuples. i.e. ('Person1',  'Person2')
    # so we take each one of them and add it to the graph
    for e in edges:
        g.add_edge(e[0], e[1])

    # Giving the graph back
    return g


def main():
    """
    Main function of this file. Not used.
    Returns
    -------

    """
    database_edge = db.Database('trump_edges')

    g = create_graph(database_edge)


if __name__ == '__main__':
    main()
