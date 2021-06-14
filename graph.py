class Graphe_mat:
    """
    Graph using matrix. (NOT USED)
    """
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
    """
    Graph using a dict.
    """
    def __init__(self):
        self.dic = {}

    def add_vertice(self, v):
        """
        Adding vertice v to the graph.

        Parameters
        ----------
        v: Name of the vertice

        Returns
        -------

        """
        if v not in self.dic:
            self.dic[v] = []

    def add_edge(self, v1, v2):
        """
        Adding edge to the graph.

        Parameters
        ----------
        v1: Vertice 1 to link with
        v2: Vertice 2 to link with

        Returns
        -------

        """
        self.add_vertice(v1)
        if v2 not in self.dic[v1]:
            self.add_vertice(v2)
            self.dic[v1].append(v2)
            self.dic[v2].append(v1)

    def edge(self, v1, v2):
        """
        Returns True if there is a link betwwen v1 and v2

        Parameters
        ----------
        v1: Vertice 1
        v2: Vertice 2

        Returns
        -------
        boolean
        """
        return v2 in self.dic[v1]

    def vertices(self):
        """
        Returns all the vertices of the graph.

        Returns
        -------
        list
        """
        return list(self.dic)

    def neighbors(self, v):
        """
        Returns all the neighbors (vertices connected) of the vertice v.

        Parameters
        ----------
        v: Vertice from which we want to get the neighbors.

        Returns
        -------
        list
        """
        return self.dic[v]

    def nb_neighbors(self):
        """
        Returns the number of vertices in the graph.

        Returns
        -------
        int
        """
        return len(self.dic)
