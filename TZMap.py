"""
This program defines a class that stores the trapezoidal map.
It also provides related helper functions.

Author: Ajinkya Dhaigude (ad8454@rit.edu)
"""


class TZMap:
    def __init__(self, root):
        self.root = root
        self.adjMatrix = None
        self.allPNames = []
        self.allQNames = []
        self.totSegments = 0
        self.totTrapezoids = 0

    def update_root(self, root):
        self.root = root

    def assign_trapezoid_names(self, id_num=0, node=None):
        """
        Recursive function that assigns a unique name to
        each trapezoid. This function should be called
        after the whole map is built as the trapezoids are
        constantly modified and deleted during the building
        process.
        :param id_num: sequential number part of the name
        :param node: current node under consideration
        :return: last assigned number
        """
        if node is None:
            node = self.root

        if node.is_leaf and node.name is None:
            id_num += 1
            node.name = 'T' + str(id_num)

        elif node.type == 'xnode':
            id_num = self.assign_trapezoid_names(id_num, node.left)
            id_num = self.assign_trapezoid_names(id_num, node.right)

        elif node.type == 'ynode':
            id_num = self.assign_trapezoid_names(id_num, node.above)
            id_num = self.assign_trapezoid_names(id_num, node.below)

        return id_num

    def print_traversal_path(self, user_point, node=None):
        """
        Print to console the traversal path of the given
        point in the map.
        :param user_point: destination point
        :param node: current node on the path to destination
        :return: None
        """
        if node is None:
            node = self.root
            print('Traversal Path:', end='')
        else:
            print(' -> ', end='')

        print(" " + node.get_name(), end='')

        if node.type == 'xnode':
            if user_point.x >= node.end_point.x:
                self.print_traversal_path(user_point, node.right)
            else:
                self.print_traversal_path(user_point, node.left)
        elif node.type == 'ynode':
            if node.line_segment.isPointAbove(user_point):
                self.print_traversal_path(user_point, node.above)
            else:
                self.print_traversal_path(user_point, node.below)

    def create_adj_matrix(self, unique_points, num_segments, num_trapezoids):
        """
        Convert trapezoidal map to an adjacency matrix and write the
        output to a file.
        :param unique_points: list of unique points in the map
        :param num_segments: total number of segments in the map
        :param num_trapezoids: total number of trapezoids in the map
        :return: None
        """
        for point in unique_points:
            if point.name[0] == 'P':
                self.allPNames.append(int(point.name[1:]))
            else:
                self.allQNames.append(int(point.name[1:]))
        self.totSegments = num_segments
        self.totTrapezoids = num_trapezoids
        n = len(unique_points) + num_segments + num_trapezoids + 2
        self.adjMatrix = [[0] * n for i in range(n)]

        self.header_for_adj_matrix(0, '   ')
        self.header_for_adj_matrix(len(self.adjMatrix) - 1, 'Sum')
        self.fill_adj_matrix()

        adjFileName = "adjMatrixOutput.txt"
        with open(adjFileName, 'w') as outFile:
            for arr in self.adjMatrix:
                for col, elem in enumerate(arr):
                    elem = str(elem)
                    if len(elem) == 1:
                        elem = ' ' + elem + ' '
                    if len(elem) == 2:
                        elem = ' ' + elem

                    outFile.write(elem + ' ')

                outFile.write('\n')


    def fill_adj_matrix(self, node=None):
        """
        Recursive function that traverses the map to fill in
        appropriate vales in the adjacency matrix.
        :param node: current node under consideration
        :return: None
        """
        if node is None:
            node = self.root

        col = self.get_idx(node)
        if node.type == 'xnode':
            self.add_to_adj_matrix(self.get_idx(node.left), col)
            self.fill_adj_matrix(node.left)
            self.add_to_adj_matrix(self.get_idx(node.right), col)
            self.fill_adj_matrix(node.right)

        if node.type == 'ynode':
            self.add_to_adj_matrix(self.get_idx(node.above), col)
            self.fill_adj_matrix(node.above)
            self.add_to_adj_matrix(self.get_idx(node.below), col)
            self.fill_adj_matrix(node.below)

    def get_idx(self, node):
        """
        Get corresponding index in the matrix of a node
        from its name.
        :param node: node to be indexed
        :return: index of node
        """
        name = node.get_name()
        if len(name) == 2:
            name += ' '
        idx = int(name[1:])

        if name[0] == 'P':
            idx = self.allPNames.index(idx) + 1
            self.header_for_adj_matrix(idx, name)
            return idx

        if name[0] == 'Q':
            idx = self.allQNames.index(idx) + 1
            idx += len(self.allPNames)
            self.header_for_adj_matrix(idx, name)
            return idx

        if name[0] == 'S':
            idx += len(self.allPNames) + len(self.allQNames)
            self.header_for_adj_matrix(idx, name)
            return idx

        if name[0] == 'T':
            idx += len(self.allPNames) + len(self.allQNames) + self.totSegments
            self.header_for_adj_matrix(idx, name)
            return idx

    def add_to_adj_matrix(self, row, col):
        if self.adjMatrix[row][col] == 0:
            self.adjMatrix[row][col] = 1
            self.adjMatrix[row][-1] += 1
            self.adjMatrix[-1][col] += 1

    def header_for_adj_matrix(self, idx, name):
        self.adjMatrix[0][idx] = name
        self.adjMatrix[idx][0] = name
