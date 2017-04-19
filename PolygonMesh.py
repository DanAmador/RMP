class Vertex:
        def __init__(self,x,y):
            self.x = x
            self.y = y

class PolygonMesh:
    def __init__(self):
        self.Vertices = []

    def addVertex(self,x,y):
        self.Vertices.append(Vertex(x,y))

    def toPGCoordinates(self):
        return [[vertex.x,vertex.y] for vertex in self.Vertices]