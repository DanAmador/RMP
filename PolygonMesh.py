from pyhull.convex_hull import ConvexHull
class Vertex:
        def __init__(self,x,y):
            self.x = x
            self.y = y

class PolygonMesh:
    def __init__(self):
        self.Vertices = []
        self.convexHull = []

    def addVertex(self,x,y):
        self.Vertices.append(Vertex(x,y))

    def polygonCoordinates(self):
        return [[vertex.x,vertex.y] for vertex in self.Vertices]

    def chCoordinates(self):
        return [[vertex.x,vertex.y] for vertex in self.convexHull]

    def qhull(self):
        points = self.polygonCoordinates()
        hull = ConvexHull(points)

        hullvS = sorted(hull.vertices)
        print("Real CH", hullvS)
        hull_order = hullvS[0]
        for hull_point in hullvS[1:-1]:
            if hull_point[0] is hull_order[0]:
                hull_order =[hull_point[1]] + hull_order
            else:
                hull_order = [hull_point[0]] + hull_order

        print("Computed CH",hull_order)
        for vertex in hull_order:
            self.convexHull.append(self.Vertices[vertex])