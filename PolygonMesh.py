from pyhull.convex_hull import ConvexHull
class Vertex:
        def __init__(self,x,y):
            self.x = x
            self.y = y

class Segment:
    def __init__(self,s1,s2):
        self.s1 = s1
        self.s2 = s2

    def segmentCoordinates(self):
        return [self.s1.x,self.s1.y],[self.s2.x,self.s2.y]

class PolygonMesh:
    def __init__(self):
        self.Vertices = []
        self.convexHull = []

    def addVertex(self,x,y):
        self.Vertices.append(Vertex(x,y))

    def polygonCoordinates(self, ch = False):
        if not ch :
            return [[vertex.x,vertex.y] for vertex in self.Vertices]
        else:
            return [segment.segmentCoordinates() for segment in self.convexHull]


    def qhull(self):
        points = self.polygonCoordinates()
        hull = ConvexHull(points)

        for segment in hull.vertices:
            self.convexHull.append(Segment(self.Vertices[segment[0]]
                                           ,self.Vertices[segment[1]]))

