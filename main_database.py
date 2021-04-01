import database as db
import graph


def create_graph(database_vertices, database_edges):
    g = graph.Graph_dic()

    edges = database_edges.select_item()
    for e in edges:
        g.add_edge(e[0], e[1])

    return g


def main():

    # WARNING :
    # On windows please use a \
    # On Linux please use a /
    database_vertices = db.Database('trump_vertices', '/')
    database_edge = db.Database('trump_edges', '/')

    g = create_graph(database_vertices, database_edge)
    database_vertices.change_status('Paul Teller', 1)
    print(
        g.neighbors('Christopher Ruddy')
    )


if __name__ == '__main__':
    main()
