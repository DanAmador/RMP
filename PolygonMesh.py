import copy
from pyhull.convex_hull import ConvexHull
from math import sqrt, inf
import matplotlib.path as mplPath
import numpy as np


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

        self.slope = (self.right_point.y - self.left_point.y) / (self.right_point.x - self.left_point.x) if (
                                                                                                                self.right_point.x - self.left_point.x) != 0 else inf
        self.const = self.left_point.y - (self.slope * self.left_point.x)

        if name is not None:
            self.name = name

    def isPointAbove(self, point):
        if point.y > (self.slope * point.x) + self.const:
            return True
        return False

    def getY(self, x, integer=False):
        if self.left_point.x - 1 <= x <= self.right_point.x + 1:
            return_value = (self.slope * x) + self.const
            return return_value if not integer else int(return_value)
        return None


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

    def is_inside(self, point, r=0.001):
        vertex, edges = self.dcel_info()
        crd = np.array(vertex, dtype='float64')
        bbPath = mplPath.Path(crd)
        return bbPath.contains_point(point, radius=r) or bbPath.contains_point(point, radius=-r)

    def contains_path_with_points(self, segment, up=True):
        points = []
        if segment.slope == inf:
            jump = -1 if up else 1
            y_diff = abs(segment.left_point.y - segment.right_point.y) / 10
            curr_y = segment.left_point.y if up else segment.left_point.y

            for jumps in range(9):
                points.append([segment.left_point.x, int(curr_y)])
                curr_y += y_diff * jump
        else:
            print("not infinite")
            jump = 1
            curr_x = segment.left_point.x + 5
            for jumps in range(int(segment.length)):
                if curr_x < segment.right_point.x:
                    points.append([curr_x, segment.getY(curr_x, integer=True)])
                curr_x += jump

        return [self.is_inside(point_tuple, r=0) for point_tuple in points], points

    def contains_path(self, segment, up=False):
        segment_inside, _ = self.contains_path_with_points(segment, up)

        return any(segment_inside)
    def qhull(self):
        self.convexHull = ConvexHull([[vertex.x, vertex.y] for vertex in self.Vertices])
        for segment in self.convexHull.vertices:
            self.ch_poly.append(Segment(self.Vertices[segment[0]], self.Vertices[segment[1]]))
