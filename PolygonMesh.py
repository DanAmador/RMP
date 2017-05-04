import copy
from pyhull.convex_hull import ConvexHull
from math import sqrt


class Point:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
        self.seen = False
        self.coordinates = (x, y)


class Segment:
    def __init__(self, s1, s2, name=None):
        self.left_point = s1
        self.right_point = s2
        if s1.x > s2.x:
            self.left_point = s2
            self.right_point = s1
        self.segment_coordinates = [self.left_point.x, self.left_point.y], [self.right_point.x, self.right_point.y]
        self.length = sqrt((s1.x - s2.x) ** 2 + (s1.y - s2.y) ** 2)
        self.middle_point = ((s1.x + s2.x) / 2, (s1.y + s2.y) / 2)

        self.slope = (self.right_point.y - self.left_point.y) / (self.right_point.x - self.left_point.x)
        self.const = self.left_point.y - (self.slope * self.left_point.x)

        if name is not None:
            self.name = name


    def isPointAbove(self, point):
        if point.y > (self.slope * point.x) + self.const:
            return True
        return False

    def getY(self, x):
        print(self.left_point.x, "<=", x, "<= ", self.right_point.x)
        if self.left_point.x -1 <= x <= self.right_point.x +1 :
            return (self.slope * x) + self.const
        return None

    def getY_back(self,x):
        print(self.left_point.x, ">=", x, ">= ", self.right_point.x)
        return int((self.slope * x) + self.const)
    def point_vertical_intersection(self, point):

            pass


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

    def is_inside(self, point):
        odd_nodes = False
        x, y = point
        polygon = self.Vertices[:]
        j = len(polygon) - 1
        for i, p in enumerate(self.Vertices):
            if polygon[i].y > y and polygon[j].y >= y or polygon[j].y < y and polygon[i].y >= y:
                if polygon[i].x + (x - polygon[i].y) / (polygon[j].y - polygon[i].x) * (
                            polygon[j].x - polygon[i].x) < x:
                    odd_nodes = not odd_nodes
            j = i
        return odd_nodes

    def clear(self):
        self.Vertices = []
        self.convexHull = []
        self.ch_poly = []
