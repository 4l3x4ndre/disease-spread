class Graphe_mat:

    def __init__(self, n):
        self.n = n
        self.mat = [[False] * n for _ in range(n)]

    def add_edge(self, s1, s2):
        self.mat[s1][s2] = True
        self.mat[s2][s1] = True

    def edge(self, s1, s2):
        return self.mat[s1][s2]

    def neighbougrs(self, s):
        v = []
        for i in range(self.n):
            if self.mat[s][i]:
                v.append(i)
        return v


class Graph_dic:

    def __init__(self):
        self.dic = {}

    def add_vertice(self, v):
        if v not in self.dic:
            self.dic[v] = []

    def add_edge(self, v1, v2):
        self.add_vertice(v1)
        if v2 not in self.dic[v1]:
            self.add_vertice(v2)
            self.dic[v1].append(v2)
            self.dic[v2].append(v1)

    def edge(self, v1, v2):
        return v2 in self.dic[v1]

    def vertice(self):
        return list(self.dic)

    def neighbors(self, v):
        return self.dic[v]

def width_course(graph):
    """width course = parcous en largeur en français"""
    queue = Queue()
    queue.onqueue(graph)
    saw = []
    for n in graph.neighbors():
        v = queue.enqueue()
        if v not in saw:
            saw.append(v)
            for n2 in v.neighbors():
                queue.onqueue(n2)
    return saw

def change_status(L):
    """"change people's status of the database to not sick to sick"""
    for i in L :









