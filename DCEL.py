#!/usr/bin/env python
# Copyright Angel Yanguas-Gil, 2008.

"""

xygraph implements a 2D map formed by undirected edges between
vertices.
"""
from PolygonMesh import Segment

__author__ = "Angel Yanguas-Gil"

import math as m


class Xygraph:
    """Represents a set of vertices connected by undirected edges.
    The vertices are stored in a list of coordinates, while
    the edges are stored as a pair of indices (i,j) of the vertices
    list.
    """

    def __init__(self, vl=[], el=[]):
        """Creates the 2D graph formed by a list of vertices (x,y)
        and a list of indices (i,j)
        """
        self.vl = vl
        self.el = el
        if self.vl != []:
            self.minmax()

    def minmax(self):
        """Determines the boundary box of the vertices in the graph"""
        vx = [v[0] for v in self.vl]
        vy = [v[1] for v in self.vl]
        self.xmax, self.xmin = max(vx), min(vx)
        self.ymax, self.ymin = max(vy), min(vy)

    def clip(self, clipbox):
        """Trims the vertex and edge list of elements that lie
        outside a clipping box [(xmin,xmax),(ymin,ymax)]"""
        pmin, pmax = clipbox
        ind = []
        vlt = []
        # Direct elimination of out of bounds edges and vertices
        for i in range(len(self.vl)):
            if self.vl[i][0] < pmin[0] or self.vl[i][1] < pmin[1] or \
                            self.vl[i][0] > pmax[0] or self.vl[i][1] > pmax[1]:
                ind.append(i)
            else:
                vlt.append(self.vl[i])
        elt = filter((lambda x: (x[0] not in ind) and (x[1] not in ind)),
                     self.el)
        li = filter((lambda x: x not in ind), range(len(self.vl)))
        # We rename the indices in the trimmed edge list
        lf = range(len(self.vl) - len(ind))
        equiv = {}
        for i in range(len(li)):
            if li[i] != lf[i]:
                equiv[li[i]] = lf[i]

        for i in range(len(elt)):
            if elt[i][0] in equiv:
                x = equiv[elt[i][0]]
            else:
                x = elt[i][0]
            if elt[i][1] in equiv:
                y = equiv[elt[i][1]]
            else:
                y = elt[i][1]
            elt[i] = (x, y)

        self.vl = vlt
        self.el = elt
        self.minmax()


class DcelError(Exception): pass


class Vertex:
    """Minimal implementation of a vertex of a 2D dcel"""

    def __init__(self, px, py):
        self.x = px
        self.y = py
        self.hedgelist = []
        self.coordinates = (self.x, self.y)

    def sort_incident(self):
        self.hedgelist.sort(key=cmp_to_key(hsort), reverse=True)


class Hedge:
    """Minimal implementation of a half-edge of a 2D dcel"""

    def __init__(self, v1, v2):
        # The origin is defined as the vertex it points to
        self.origin = v2
        self.twin = None
        self.face = None
        self.nexthedge = None
        self.angle = hangle(v2.x - v1.x, v2.y - v1.y)
        self.prevhedge = None
        self.length = m.sqrt((v2.x - v1.x) ** 2 + (v2.y - v1.y) ** 2)


class Face:
    """Implements a face of a 2D dcel"""

    def __init__(self):
        self.wedge = None
        self.data = None
        self.external = None

    def area(self) -> float:
        h = self.wedge
        a = 0
        while not h.nexthedge is self.wedge:
            p1 = h.origin
            p2 = h.nexthedge.origin
            a += p1.x * p2.y - p2.x * p1.y
            h = h.nexthedge

        p1 = h.origin
        p2 = self.wedge.origin
        a = (a + p1.x * p2.y - p2.x * p1.y) / 2
        return a

    def perimeter(self) -> int:
        h = self.wedge
        p = 0
        while not h.nexthedge is self.wedge:
            p += h.length
            h = h.nexthedge
        return p

    def vertex_list(self) -> list:
        h = self.wedge
        pl = [h.origin]
        while not h.nexthedge is self.wedge:
            h = h.nexthedge
            pl.append(h.origin)
        return pl

    def is_inside(self, p) -> bool:
        """Determines whether a point is inside a face"""
        h = self.wedge
        inside = False
        if lefton(h, p):
            while not h.nexthedge is self.wedge:
                h = h.nexthedge
                if not lefton(h, p):
                    return False
            return True
        else:
            return False


class Dcel(Xygraph):
    """
    Implements a doubly-connected edge list
    """

    def __init__(self, vl=[], el=[], clip=None):
        Xygraph.__init__(self, vl, el)
        self.vertices = []
        self.hedges = []
        self.faces = []
        if vl != []:
            if clip is not None:
                self.clip(clip)
            self.build_dcel()

    def build_dcel(self):
        """
        Creates the dcel from the list of vertices and edges
        """

        # Step 1: vertex list creation
        for v in self.vl:
            self.vertices.append(Vertex(v[0], v[1]))

        # Step 2: hedge list creation. Assignment of twins and
        # vertices

        for e in self.el:
            if e[0] >= 0 and e[1] >= 0:
                h1 = Hedge(self.vertices[e[0]],
                           self.vertices[e[1]])
                h2 = Hedge(self.vertices[e[1]], self.vertices[e[0]])
                h1.twin = h2
                h2.twin = h1
                self.vertices[e[1]].hedgelist.append(h1)
                self.vertices[e[0]].hedgelist.append(h2)
                self.hedges.append(h2)
                self.hedges.append(h1)
            else:
                print("oh shit boi wadup")

        # Step 3: Identification of next and prev hedges
        for index, v in enumerate(self.vertices):
            v.sort_incident()
            l = len(v.hedgelist)
            if l < 2:
                raise DcelError("Badly formed dcel: less than two hedges in vertex:" + str(index))
            else:
                for i in range(l - 1):
                    v.hedgelist[i].nexthedge = v.hedgelist[i + 1].twin
                    v.hedgelist[i + 1].prevhedge = v.hedgelist[i]
                v.hedgelist[l - 1].nexthedge = v.hedgelist[0].twin
                v.hedgelist[0].prevhedge = v.hedgelist[l - 1]

        # Step 4: Face assignment
        provlist = self.hedges[:]
        nf = 0
        nh = len(self.hedges)

        while nh > 0:
            h = provlist.pop()
            nh -= 1
            # We check if the hedge already points to a face
            if h.face == None:
                f = Face()
                nf += 1
                # We link the hedge to the new face
                f.wedge = h
                f.wedge.face = f
                # And we traverse the boundary of the new face
                while not h.nexthedge is f.wedge:
                    h = h.nexthedge
                    h.face = f
                self.faces.append(f)
        # And finally we have to determine the external face
        for f in self.faces:
            f.external = f.area() < 0

    def findpoints(self, pl, onetoone=False):
        """Given a list of points pl, returns a list of
        with the corresponding face each point belongs to and
        None if it is outside the map.

        """

        ans = []
        if onetoone:
            fl = self.faces[:]
            for p in pl:
                found = False
                for f in fl:
                    if f.external:
                        continue
                    if f.is_inside(p):
                        fl.remove(f)
                        found = True
                        ans.append(f)
                        break
                if not found:
                    ans.append(None)

        else:
            for p in pl:
                found = False
                for f in self.faces:
                    if f.external:
                        continue
                    if f.is_inside(p):
                        found = True
                        ans.append(f)
                        break
                if not found:
                    ans.append(None)

        return ans

    def areas(self):
        return [f.area() for f in self.faces if not f.external]

    def perimeters(self):
        return [f.perimeter() for f in self.faces if not f.external]

    def nfaces(self):
        return len(self.faces)

    def nvertices(self):
        return len(self.vertices)

    def nedges(self):
        return len(self.hedges) / 2


# Misc. functions
def hsort(h1, h2) -> int:
    """Sorts two half edges counterclockwise"""

    if h1.angle < h2.angle:
        return -1
    elif h1.angle > h2.angle:
        return 1
    else:
        return 0


def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'

    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

    return K


def checkhedges(hl):
    """Consistency check of a hedge list: nexthedge, prevhedge"""

    for h in hl:
        if h.nexthedge not in hl or h.prevhedge not in hl:
            raise DcelError("Problems with an orphan hedge...")


def area2(hedge, point) -> float:
    """Determines the area of the triangle formed by a hedge and
    an external point"""

    pa = hedge.twin.origin
    pb = hedge.origin
    pc = point
    return (pb.x - pa.x) * (pc[1] - pa.y) - (pc[0] - pa.x) * (pb.y - pa.y)


def is_in_convex_polygon(point, polygons):
    pos, neg = 0, 0
    for i, polygon in enumerate(polygons):

        s1 = polygons[i]
        # Cross Product
        d = (point[0] - s1[0][0]) * (s1[1][1] - s1[0][1]) - (point[1] - s1[0][1]) * (s1[1][0] - s1[0][0])

        if d > 0: pos += 1
        if d < 0: neg += 1

        if pos > 0 and neg > 0:
            return False
    return True


def lefton(hedge, point):
    """Determines if a point is to the left of a hedge"""

    return area2(hedge, point) >= 0


def hangle(dx, dy):
    """Determines the angle with respect to the x axis of a segment
    of coordinates dx and dy
    """

    l = m.sqrt(dx * dx + dy * dy)
    if dy > 0:
        return m.acos(dx / l)
    else:
        return 2 * m.pi - m.acos(dx / l)
