class Graphe_mat:

    def __init__(self, n):
        self.n = n
        self.mat = [[False] * n for _ in range(n)]

    def add_edge(self, s1, s2):
        self.mat[s1][s2] = True

    def edge(self, s1, s2):
        return self.mat[s1][s2]

    def neighbors(self, s):
        v = []
        for i in range(self.n):
            if self.mat[s][i]:
                v.append(i)
        return v