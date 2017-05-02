"""
This is the main program that reads in the input file and
builds the trapezoidal map. It then accepts a user input for
coordinates and calls a method to output the traversal path.

Author: Ajinkya Dhaigude (ad8454@rit.edu)
"""
from Nodes import XNode, YNode, TrapezoidNode
from PolygonMesh import Point, Segment
from TZMap import TZMap


def build_tmap(segments, bounding_box_tuple):

    x1, y1, x2, y2 = bounding_box_tuple
    line_segments = []
    id_num = 1
    unique_points = []
    lower_eft = Point('ll', x1, y1)
    upper_right = Point('ur', x2, y2)
    lower_right = Point('lr', x2, y1)
    upper_left = Point('ul', x1, y2)
    top_segment = Segment(upper_left, upper_right, 'bT')
    bottom_segment = Segment(lower_eft, lower_right, 'bB')
    bounding_box = TrapezoidNode(top_segment, bottom_segment, upper_left, upper_right)
    # create a map instance with initially only the bounding box
    tz_map = TZMap(bounding_box)
    for segment in segments:
        x1, y1 = segment[0]
        x2, y2 = segment[1]
        print(segment)
        point1 = Point('P' + str(id_num), x1, y1)
        point2 = Point('Q' + str(id_num), x2, y2)
        is_point1_unique = True
        is_point2_unique = True
        # store point only if it is unique
        for point in unique_points:
            if point.x == point1.x and point.y == point1.y:
                point1 = point
                is_point1_unique = False
            if point.x == point2.x and point.y == point2.y:
                point2 = point
                is_point2_unique = False

        if is_point1_unique:
            unique_points.append(point1)
        if is_point2_unique:
            unique_points.append(point2)
        line_segments.append(Segment(point1, point2, 'S' + str(id_num)))
        id_num += 1
    # add segments incrementally to the map
    for segment in line_segments:
        intersecting_trapezoids = []
        find_intersecting_trapezoids(tz_map.root, segment, intersecting_trapezoids)
        # handle new segment in two cases: it either intersects one trapezoid or many of them
        if len(intersecting_trapezoids) == 1:
            update_map_for_one_trapezoid(tz_map, intersecting_trapezoids[0], segment)
        else:
            update_map_for_many_trapezoids(tz_map, intersecting_trapezoids, segment)

    # assign unique names to all trapezoids in the map
    tot_trapezoids = tz_map.assign_trapezoid_names()
    print('Map built successfully:- Points: ' + str(len(unique_points)) + ', Segments:' + str(len(line_segments)) + ', '+'Trapezoids: ' + str(tot_trapezoids))
    # convert map to a adjacency matrix and print to file
    tz_map.create_adj_matrix(unique_points, len(line_segments), tot_trapezoids)
    return tz_map


def update_map_for_one_trapezoid(tzMap, trapezoid, segment):
    """
    Function to update the map if the new segment lies entirely
    within one existing trapezoid.
    :param tzMap: graph instance of the trapezoidal map
    :param trapezoid: existing trapezoid encompassing the segment
    :param segment: new segment to be added to the map
    :return: None
    """
    left_trapezoid = TrapezoidNode(trapezoid.top_segment, trapezoid.bottom_segment, trapezoid.left_point,
                                   segment.left_point)
    top_trapezoid = TrapezoidNode(trapezoid.top_segment, segment, segment.left_point, segment.right_point)
    bottom_trapezoid = TrapezoidNode(segment, trapezoid.bottom_segment, segment.left_point, segment.right_point)
    right_trapezoid = TrapezoidNode(trapezoid.top_segment, trapezoid.bottom_segment, segment.right_point,
                                    trapezoid.right_point)

    seg_node = YNode(segment, top_trapezoid, bottom_trapezoid)
    q = XNode(segment.right_point, seg_node, right_trapezoid)
    p = XNode(segment.left_point, left_trapezoid, q)
    trapezoid.replace_position_with(tzMap, p)


def update_map_for_many_trapezoids(tzMap, intersectingTrapezoids, segment):
    """
    Function to update map if the new segment lies within
    several existing trapezoids.
    :param tzMap:graph instance of the trapezoidal map
    :param intersectingTrapezoids: list of existing trapezoids
                                        encompassing the segment
    :param segment: new segment to be added to the map
    :return: None
    """
    upper_mid_trapezoid = None
    lower_mid_trapezoid = None
    merge_upper = False

    for trapezoid in intersectingTrapezoids:

        if trapezoid.contains_point(segment.left_point):
            # case where the left endpoint of the new segment lies in the trapezoid
            left_trapezoid = TrapezoidNode(trapezoid.top_segment, trapezoid.bottom_segment, trapezoid.left_point,
                                           segment.left_point)
            if segment.isPointAbove(trapezoid.right_point):
                upper_mid_trapezoid = TrapezoidNode(trapezoid.top_segment, segment, segment.left_point,
                                                    trapezoid.right_point)
                lower_mid_trapezoid = TrapezoidNode(segment, trapezoid.bottom_segment, segment.left_point, None)
                merge_upper = False
            else:
                upper_mid_trapezoid = TrapezoidNode(trapezoid.top_segment, segment, segment.left_point, None)
                lower_mid_trapezoid = TrapezoidNode(segment, trapezoid.bottom_segment, segment.left_point,
                                                    trapezoid.right_point)
                merge_upper = True

            if segment.left_point.seen:
                continue
            seg_node = YNode(segment, upper_mid_trapezoid, lower_mid_trapezoid)
            p = XNode(segment.left_point, left_trapezoid, seg_node)
            trapezoid.replace_position_with(tzMap, p)

        elif trapezoid.contains_point(segment.right_point):
            # case where the right endpoint of the new segment lies in the trapezoid
            right_trapezoid = TrapezoidNode(trapezoid.top_segment, trapezoid.bottom_segment, segment.right_point,
                                            trapezoid.right_point)
            if merge_upper:
                upper_mid_trapezoid.right_point = segment.right_point
                lower_mid_trapezoid = TrapezoidNode(segment, trapezoid.bottom_segment, trapezoid.left_point,
                                                    segment.right_point)
            else:
                upper_mid_trapezoid = TrapezoidNode(trapezoid.top_segment, segment, trapezoid.left_point,
                                                    segment.right_point)
                lower_mid_trapezoid.right_point = segment.right_point
            if segment.right_point.seen:
                continue
            seg_node = YNode(segment, upper_mid_trapezoid, lower_mid_trapezoid)
            q = XNode(segment.right_point, seg_node, right_trapezoid)
            trapezoid.replace_position_with(tzMap, q)

        else:
            # case where the no endpoint of the new segment lies in the trapezoid
            if merge_upper:
                lower_mid_trapezoid = TrapezoidNode(segment, trapezoid.bottom_segment, trapezoid.left_point, None)
            else:
                upper_mid_trapezoid = TrapezoidNode(trapezoid.top_segment, segment, trapezoid.left_point, None)

            if segment.isPointAbove(trapezoid.right_point):
                upper_mid_trapezoid.right_point = trapezoid.right_point
                merge_upper = False
            else:
                lower_mid_trapezoid.right_point = trapezoid.right_point
                merge_upper = True

            seg_node = YNode(segment, upper_mid_trapezoid, lower_mid_trapezoid)
            trapezoid.replace_position_with(tzMap, seg_node)


def find_intersecting_trapezoids(node, segment, intersecting_trapezoids):
    """
    Recursive function that finds all existing trapezoids in the map
    that the new segment intersects.
    :param node: a node in the map. Initially it's the root
    :param segment: new segment to be added to the map
    :param intersecting_trapezoids: a list of intersecting trapezoids
                                    to be filled by the function.
                                    Initially empty
    :return: None
    """
    if node.is_leaf:
        if node.contains_segment(segment):
            if node not in intersecting_trapezoids:
                intersecting_trapezoids.append(node)

    elif node.type == 'xnode':
        if segment.left_point.x >= node.end_point.x:
            find_intersecting_trapezoids(node.right, segment, intersecting_trapezoids)
        else:
            find_intersecting_trapezoids(node.left, segment, intersecting_trapezoids)
            if segment.right_point.x >= node.end_point.x:
                find_intersecting_trapezoids(node.right, segment, intersecting_trapezoids)

    else:
        if node.lineSegment.isPointAbove(segment.left_point):
            find_intersecting_trapezoids(node.above, segment, intersecting_trapezoids)
        else:
            find_intersecting_trapezoids(node.below, segment, intersecting_trapezoids)


def traverse_tree_without_trapezoids(traversed_nodes, node):
    if node.type == 'xnode':
        traverse_tree_without_trapezoids(traversed_nodes, node.left)
        traversed_nodes.append(node)
        traverse_tree_without_trapezoids(traversed_nodes, node.right)
    if node.type == 'ynode':
        traverse_tree_without_trapezoids(traversed_nodes, node.above)
        traversed_nodes.append(node)
        traverse_tree_without_trapezoids(traversed_nodes, node.below)
    if node.type == 'tnode':
        traversed_nodes.append(node)

    return traversed_nodes

