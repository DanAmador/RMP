"""
This program defines the classes for each of the
three different kinds of nodes required for a
trapezoidal map

Author: Ajinkya Dhaigude (ad8454@rit.edu)
"""

from PolygonMesh import Point


class XNode:
    def __init__(self, point, left=None, right=None):
        self.isLeaf = False
        self.type = 'xnode'
        self.set_left(left)
        self.set_right(right)
        self.endPoint = point
        self.endPoint.seen = True

    def set_left(self, node):
        self.left = node
        if node is None:
            return
        if node.isLeaf and self not in node.parents:
            node.parents.append(self)

    def set_right(self, node):
        self.right = node
        if node is None:
            return
        if node.isLeaf and self not in node.parents:
            node.parents.append(self)

    def get_name(self):
        return self.endPoint.name


class YNode:
    def __init__(self, segment, above=None, below=None):
        self.isLeaf = False
        self.type = 'ynode'
        self.set_above(above)
        self.set_below(below)
        self.lineSegment = segment

    def set_above(self, node):
        self.above = node
        if node is None:
            return
        if node.isLeaf and self not in node.parents:
            node.parents.append(self)

    def set_below(self, node):
        self.below = node
        if node is None:
            return
        if node.isLeaf and self not in node.parents:
            node.parents.append(self)

    def get_name(self):
        return self.lineSegment.name


class TrapezoidNode:
    def __init__(self, top_segment, bottom_segment, left_point, right_point):
        self.isLeaf = True
        self.type = 'tnode'
        self.topSegment = top_segment
        self.bottomSegment = bottom_segment
        self.leftPoint = left_point
        self.rightPoint = right_point
        self.parents = []
        self.name = None

    def contains_segment(self, segment):
        if self.contains_point(segment.leftPoint) or self.contains_point(segment.rightPoint):
            return True
        resY = segment.getY(self.leftPoint.x)
        if resY is not None:
            leftIntersection = Point(None, self.leftPoint.x, resY)
            if self.contains_point(leftIntersection):
                return True
        return False

    def contains_point(self, point):
        if self.leftPoint.x <= point.x <= self.rightPoint.x:
            return self.bottomSegment.isPointAbove(point) and not self.topSegment.isPointAbove(point)
        return False

    def replace_position_with(self, tzMap, node):
        if not self.parents:
            tzMap.update_root(node)
            return
        for parent in self.parents:
            if parent.type == 'xnode':
                if parent.left == self:
                    parent.set_left(node)
                else:
                    parent.set_right(node)
            else:
                if parent.above == self:
                    parent.set_above(node)
                else:
                    parent.set_below(node)

    def get_name(self):
        return self.name
