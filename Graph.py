import numpy


class Gnode:
    def __init__(self, x, y, name):
        self.name = name
        self.x = x
        self.y = y
        self.coordinates = (x, y)
        self.rank = 0


class Edge:
    def __init__(self, from_node, to_node):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = round(
            numpy.linalg.norm(numpy.asarray(from_node.coordinates) - numpy.asarray(to_node.coordinates)))

    def contains(self, name):
        return name == self.from_node.name or name == self.to_node.name

    def string_repr(self):
        return "Edge from {} to {} with weight of {}".format(self.from_node.name, self.to_node.name, self.weight)


class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self._parent, self._rank = {}, {}

    def add_vertex(self, vertex):
        if isinstance(vertex, Gnode):
            self.nodes.append(vertex)

    def add_vertices(self, vertices):
        for vertex in vertices:
            if isinstance(vertex, Gnode):
                self.nodes.append(vertex)

    def add_edge(self, vertex_from, vertex_to):
        if isinstance(vertex_from, Gnode) and isinstance(vertex_to, Gnode):
            vertex_to.rank += 1
            vertex_from.rank += 1
            self.edges.append(Edge(vertex_from, vertex_to))

    def add_edges(self, edges):
        for edge in edges:
            self.add_edge(edge[0], edge[1])

    def remove_node(self, to_remove):
        self.nodes = [node for node in self.nodes if node != to_remove]
        self.edges = [edge for edge in self.edges if edge.contains(to_remove)]

    def kruskals(self):
        for vertex in self.nodes:
            self.make_set(vertex.name)

        minimum_spanning_tree = set()

        print(self._parent)
        self.edges.sort(key=lambda x: x.weight)
        for edge in self.edges:
            if self.find(edge.from_node.name) != self.find(edge.to_node.name):
                self.union(edge.from_node.name, edge.to_node.name)
                minimum_spanning_tree.add(edge)

        self.edges = list(minimum_spanning_tree)

    def find(self, vertice):
        if self._parent[vertice] != vertice:
            self._parent[vertice] = self.find(self._parent[vertice])
        return self._parent[vertice]

    def make_set(self, vertice):
        self._parent[vertice] = vertice
        self._rank[vertice] = 0

    def union(self, vertice1, vertice2):
        root1 = self.find(vertice1)
        root2 = self.find(vertice2)
        if root1 != root2:
            if self._rank[root1] > self._rank[root2]:
                self._parent[root2] = root1
            else:
                self._parent[root1] = root2
                if self._rank[root1] == self._rank[root2]:
                    self._rank[root2] += 1
                    # KRUSKAL(G):

# 1 A = ∅
# 2 foreach v ∈ G.V:
# 3    MAKE-SET(v)
# 4 foreach (u, v) in G.E ordered by weight(u, v), increasing:
# 5    if FIND-SET(u) ≠ FIND-SET(v):
# 6       A = A ∪ {(u, v)}
# 7       UNION(u, v)
# 8 return A
