from pyhull.convex_hull import ConvexHull
from math import sqrt

class Segment:
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2
        self.segment_coordinates = [self.s1.x, self.s1.y], [self.s2.x, self.s2.y]
        self.length = sqrt((s1.x - s2.x) ** 2 + (s1.y - s2.y) ** 2)
        self.middle_point = ((s1.x + s2.x) / 2, (s1.y + s2.y) / 2)

    def inverse(self):
        return Segment(self.s2, self.s1)


class PolygonMesh:
    def __init__(self):
        self.Vertices = []
        self.convexHull = []
        self.ch_poly = []

    def add_vertex(self, x, y):
        from DCEL import Vertex
        self.Vertices.append(Vertex(x, y))

    def dcel_info(self, ch=False) -> tuple:
        """
        Creates and returns a tuple for the polygon or the convex hull
        Parameters:
        foo - a foo of type FooType to bar with.
        ch - Boolean value to establish if you want the convex hulls information

        Return vales:
        (Vertex coordinates, Edge Tuple using polygon index)
        """
        if not ch:
            return [(vertex.x, vertex.y) for vertex in self.Vertices], [(index, (index + 1) % len(self.Vertices)) for
                                                                        index, value in enumerate(self.Vertices)]
        else:
            return self.convexHull.points, [(el[0], el[1]) for el in self.convexHull.vertices]

    def polygon_coordinates(self, ch=False) -> list:
        return [[el.x, el.y] for el in self.Vertices] if not ch else [segment.segment_coordinates for segment in
                                                                      self.ch_poly]

    def qhull(self):
        self.convexHull = ConvexHull([[vertex.x, vertex.y] for vertex in self.Vertices])
        for segment in self.convexHull.vertices:
            self.ch_poly.append(Segment(self.Vertices[segment[0]], self.Vertices[segment[1]]))

    def clear(self):
        self.Vertices = []
        self.convexHull = []
        self.ch_poly = []
