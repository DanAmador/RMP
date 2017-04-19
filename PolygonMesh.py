class Vertex:
        def __init__(self,x,y):
            self.x = x
            self.y = y

class PolygonMesh:
    from scipy.spatial import ConvexHull
    def __init__(self):
        self.Vertices = []
        self.convexHull = []
    def addVertex(self,x,y):
        self.Vertices.append(Vertex(x,y))

    def toPGCoordinates(self):
        return [[vertex.x,vertex.y] for vertex in self.Vertices]

    def qhull(self):
        self.convexHull = ConvexHull(self.toPGCoordinates())
