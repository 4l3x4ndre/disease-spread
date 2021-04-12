import database as db
import graph
import visual as gui


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


def breadth_first_search_step_by_step(g, step_id, root, queue=[], checked=[]):
    if queue == [] and checked == []:
        queue = [root]
        checked = []

    new_queue = []
    while len(queue) > 0:
        vertice = queue.pop(0)
        for n in g.neighbors(vertice):
            if n not in checked:
                new_queue.append(n)
        checked.append(vertice)

    return {'g':g, 'id':step_id+1, 'r':root, 'q':new_queue, 'c':checked}


def main():
    vert_db = db.Database('marvel_vertices')
    edges_db = db.Database('marvel_edges')

    g = create_graph(vert_db, edges_db)
    #path = breadth_first_search(g, 'Donald J. Trump')

    root = 'Deadpool / Jack / Wade W'
    gui.show_graph(g, breadth_first_search_step_by_step, root)


main()
