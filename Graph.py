import numpy


class Gnode:
    def __init__(self, x, y, name):
        self.name = name
        self.neighbors = []
        self.x = x
        self.y = y
        self.coordinates = (x, y)

    def add_neighbor(self, neighbor):
        if isinstance(neighbor, Gnode):
            if neighbor.name not in self.neighbors:
                self.neighbors.append({'node': neighbor, 'weight': self.get_weight(neighbor)}
                                      )
                neighbor.neighbors.append({'node': self, 'weight': self.get_weight(neighbor)})
                self.neighbors = sorted(self.neighbors, key=lambda n: n['node'].name)
                neighbor.neighbors = sorted(neighbor.neighbors, key=lambda n: n['node'].name)
        else:
            return False

    def get_weight(self, node):
        return round(numpy.linalg.norm(numpy.asarray(self.coordinates) - numpy.asarray(node.coordinates)))

    def add_neighbors(self, neighbors):
        for neighbor in neighbors:
            self.add_neighbor(neighbor)

    def __repr__(self):
        return str(self.neighbors)


class Graph:
    def __init__(self):
        self.vertices = []

    def add_vertex(self, vertex):
        if isinstance(vertex, Gnode):
            self.vertices.append(vertex)

    def add_vertices(self, vertices):
        for vertex in vertices:
            if isinstance(vertex, Gnode):
                self.vertices.append(vertex)

    def add_edge(self, vertex_from, vertex_to):
        if isinstance(vertex_from, Gnode) and isinstance(vertex_to, Gnode):
            vertex_from.add_neighbor(vertex_to)

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(edge[0], edge[1])


    # def kruskals(self):
    #     for node in self.vertices[]
#         KRUSKAL(G):
# 1 A = ∅
# 2 foreach v ∈ G.V:
# 3    MAKE-SET(v)
# 4 foreach (u, v) in G.E ordered by weight(u, v), increasing:
# 5    if FIND-SET(u) ≠ FIND-SET(v):
# 6       A = A ∪ {(u, v)}
# 7       UNION(u, v)
# 8 return A
