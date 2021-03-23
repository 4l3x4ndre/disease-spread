class Graph:

    def __init__(self):
        self.gdict = {}

    def add_vertices(self, i):
        if i not in self.gdict:
            self.gdict[i] = set()

    def add_edges(self, v1, v2):
        self.add_edges(v1)
        self.add_edges(v2)
        self.gdict[v1].add(v2)

    def remove_edges(self, v1, v2):
        if v1 in self.gdict and v2 in self.gdict[v1]:
            self.gdict[v1].remove(v2)

    def vertices_from(self, e):
        return self.gdict[e]