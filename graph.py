class Graphe_mat:

    def __init__(self, n):
        self.n = n
        self.mat = [[False] * n for _ in range(n)]

    def add_edge(self, s1, s2):
        self.mat[s1][s2] = True
        self.mat[s2][s1] = True

    def edge(self, s1, s2):
        return self.mat[s1][s2]

    def neighbogrs(self, s):
        v = []
        for i in range(self.n):
            if self.mat[s][i]:
                v.append(i)
        return v



class Queue:
    """Structure de file"""

    def __init__(self):
        self.tete = None
        self.queue = None

    def is_empty(self):
        " Une file est vide lorsque la tete vaut None"
        return self.tete is None

    def onqueue(self, x):
        """ Ajout d'un élément à l'arrière de la file
            Attention à gêrer le cas particulier où la file est vide
        """
        c = Cellule(x, None)
        if self.est_vide():
            self.tete = c
        else:
            self.queue.suivante = c
        self.queue = c

    def enqueue(self):
        """ Supprime et renvoie le premier élément de la liste
            Attention à gêrer le cas particulier où la file a un unique élément"""
        if self.est_vide():
            raise IndexError("retirer sur une fille vide")
        v = self.tete.valeur
        self.tete = self.tete.suivante
        if self.tete is None:
            self.queue = None
        return v


class Graph_dic:
    """ Un graphe comme dictionnaire d'adjacence"""

    def __init__(self):
        self.adj = {}

    def add_vertice(self, s):
        if s not in self.adj:
            self.adj[s] = []

    def add_edge(self, s1, s2):
        self.ajouter_sommet(s1)
        if s2 not in self.adj[s1]:
            self.ajouter_sommet(s2)
            self.adj[s1].append(s2)

    def edge(self, s1, s2):
        return s2 in self.adj[s1]

    def vertice(self):
        return list(self.adj)

    def neighbors(self, s):
        return self.adj[s]


def parcours_largeur(s):
    file = File()
    file.enfiler(s)
    vus = []
    for v in s.neighbors():
        file.enfiler(v)
        if v not in vus:
            vus.append(v)
            for

