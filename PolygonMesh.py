from pyhull.convex_hull import ConvexHull
from DCEL import Vertex
class Segment:
    def __init__(self,s1,s2):
        self.s1 = s1
        self.s2 = s2

    def segment_coordinates(self):
        return [self.s1.x,self.s1.y],[self.s2.x,self.s2.y]

class PolygonMesh:
    def __init__(self):
        self.Vertices = []
        self.convexHull = []

    def add_vertex(self, x, y):
        self.Vertices.append(Vertex(x,y))


    def dcel_info(self, ch = False):
        """
        Creates and returns a tuple for the polygon or the convex hull
        Parameters:
        foo - a foo of type FooType to bar with.
        ch - Boolean value to establish if you want the convex hulls information

        Return vales:
        (Vertex coordinates, Edge Tuple using polygon index)
        """
        if not ch :
            return [[vertex.x, vertex.y] for vertex in self.Vertices], [(index, (index + 1)% len(self.Vertices)) for index, value in enumerate(self.Vertices)]
        else:
            return self.convexHull.points, self.convexHull.vertices

    def qhull(self):
        self.convexHull = ConvexHull([vertex.x, vertex.y] for vertex in self.Vertices)
        #for segment in hull.vertices:
        #   self.convexHull.append(Segment(self.Vertices[segment[0]],self.Vertices[segment[1]]))


    def intersects_itself(self):
        #TODO ADD DCEL
        segments = [Segment(self.Vertices[index], self.Vertices[index+1]) for index,point in  enumerate(self.Vertices[:-1])]

        for s in segments:
            print(s.segment_coordinates())
        return False

