"""
This program defines the classes for each of the
three different kinds of nodes required for a
trapezoidal map

Author: Ajinkya Dhaigude (ad8454@rit.edu)
"""

from PolygonMesh import Point


class XNode:
    def __init__(self, point, left=None, right=None):
        self.is_leaf = False
        self.type = 'xnode'
        self.left = None
        self.right = None
        self.set_left(left)
        self.set_right(right)
        self.end_point = point
        self.end_point.seen = True

    def set_left(self, node):
        self.left = node
        if node is None:
            return
        if node.is_leaf and self not in node.parents:
            node.parents.append(self)

    def set_right(self, node):
        self.right = node
        if node is None:
            return
        if node.is_leaf and self not in node.parents:
            node.parents.append(self)

    def get_name(self):
        return self.end_point.name


class YNode:
    def __init__(self, segment, above=None, below=None):
        self.is_leaf = False
        self.type = 'ynode'
        self.above = None
        self.below = None
        self.set_above(above)
        self.set_below(below)
        self.line_segment = segment

    def set_above(self, node):
        self.above = node
        if node is None:
            return
        if node.is_leaf and self not in node.parents:
            node.parents.append(self)

    def set_below(self, node):
        self.below = node
        if node is None:
            return
        if node.is_leaf and self not in node.parents:
            node.parents.append(self)

    def get_name(self):
        return self.line_segment.name


class TrapezoidNode:
    def __init__(self, top_segment, bottom_segment, left_point, right_point):
        self.is_leaf = True
        self.type = 'tnode'
        self.top_segment = top_segment
        self.bottom_segment = bottom_segment
        self.left_point = left_point
        self.right_point = right_point
        self.parents = []
        print("Bound Left")
        self.bound_left = ((left_point.x, left_point.y), (left_point.x, top_segment.getY(bottom_segment.left_point.x)))
        print("Bound right")
        self.bound_right = ((right_point.x, right_point.y), (right_point.x, bottom_segment.getY(top_segment.right_point.x)))
        print("\n")
        self.name = None

    def contains_segment(self, segment):
        if self.contains_point(segment.left_point) or self.contains_point(segment.right_point):
            return True
        res_y = segment.getY(self.left_point.x)
        if res_y is not None:
            left_intersection = Point(None, self.left_point.x, res_y)
            if self.contains_point(left_intersection):
                return True
        return False

    def contains_point(self, point):
        if self.left_point.x <= point.x <= self.right_point.x:
            return self.bottom_segment.isPointAbove(point) and not self.top_segment.isPointAbove(point)
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
