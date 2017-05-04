import copy

from Button import *
from Checkbox import *
from DCEL import Dcel, Vertex, is_in_convex_polygon
from PolygonMesh import *
from TrapezoidalMap import build_tmap, traverse_tree
from poly_point_isect import isect_polygon, isect_segments


class Planner:
    def __init__(self):
        # Random Values
        menu_pos = 0
        self.debug_step = 0
        # Pygame objects
        self.screen = pygame.display.get_surface()
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        # Style vlaues
        self.debug_font = pygame.font.Font(None, 40)
        self.background_color = (50, 50, 50)
        self.shapeColor = (150, 150, 150)
        self.debugColor = (178, 34, 34)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.orange = (255, 99, 71)
        self.pink = (255, 105, 180)
        self.background.fill(self.background_color)
        # Data Structures
        self.polygons = []
        self.tz_map_vertical_segments = {'up': [], 'down': []}
        self.currentPolygon = None
        self.current_dcel = None
        self.tz_map = None

        # Debug Flags
        self.polygon_build = False
        self.remove_flag = False
        self.debug_point_flag = False

        # Debug path
        self.debug_path_segment = []
        self.debug_path_flag = False

        self.buttons = {}
        self.checkboxes = {}

        self.buttons["run"] = Button(0, menu_pos, 100, 40, "RUN")
        self.buttons["polygon"] = Button(0, menu_pos + 40, 100, 40, "POLYGON")
        self.buttons["remove"] = Button(0, menu_pos + 80, 100, 40, "REMOVE")
        self.buttons["debug_point"] = Button(0, menu_pos + 120, 100, 40, "Traversal Path")
        self.buttons["debug_step"] = Button(0, menu_pos + 160, 100, 40, "Debug step")
        self.buttons["debug_path"] = Button(0, menu_pos + 200, 100, 40, "Debug path")

        self.checkboxes['convex_hull'] = Checkbox(110, 0, "Convex Hull")
        self.checkboxes['tmap'] = Checkbox(110, 20, "Trapezoidal Map")
        self.checkboxes['robot_point'] = Checkbox(110, 40, "Robot is a point")

        pygame.display.flip()

    def debug_draw(self):
        if self.debug_path_flag:
            for vertex in self.debug_path_segment:
                pygame.draw.circle(self.screen, self.shapeColor, (vertex[0], vertex[1]), 5)

        if self.checkboxes['convex_hull'].is_checked():
            for shape in self.polygons:
                for line in shape.polygon_coordinates(ch=True):
                    pygame.draw.line(self.screen, self.debugColor, line[0], line[1], 5)

        if self.checkboxes['tmap'].is_checked() and self.tz_map:
            trav_tree = traverse_tree([], self.tz_map.root)

            if len(self.tz_map_vertical_segments['up']) > 0:
                for s in self.tz_map_vertical_segments['up']:
                    pygame.draw.line(self.screen, self.pink, s.right_point.coordinates, s.left_point.coordinates, 5)

            if len(self.tz_map_vertical_segments['down']) > 0:
                for s in self.tz_map_vertical_segments['down']:
                    pygame.draw.line(self.screen, self.pink, s.right_point.coordinates, s.left_point.coordinates, 5)

            for node in trav_tree:
                if node.type == 'tnode':
                    if node.name == "T" + str(self.debug_step):
                        t_coords = (int((node.bottom_segment.middle_point[0] + node.top_segment.middle_point[0]) / 2),
                                    int((node.bottom_segment.middle_point[1] + node.top_segment.middle_point[1]) / 2))
                        self.screen.blit(self.debug_font.render(node.name, True, self.debugColor), t_coords)
                        try:

                            pygame.draw.circle(self.screen, self.orange, node.left_point.coordinates, 10)
                            pygame.draw.circle(self.screen, self.orange, node.right_point.coordinates, 5)
                        except AttributeError:
                            print("Trying to access nonexistent node")
                        except Exception as e:
                            print(e)

                        pygame.draw.line(self.screen, self.blue, node.top_segment.left_point.coordinates,
                                         node.top_segment.right_point.coordinates, 5)
                        pygame.draw.line(self.screen, self.green, node.bottom_segment.left_point.coordinates,
                                         node.bottom_segment.right_point.coordinates, 5)

    def draw_polygons(self):
        for shape in self.polygons:
            pygame.draw.polygon(self.screen, self.shapeColor, shape.dcel_info()[0], 0)

        if self.polygon_build:
            for vertex in self.current_polygon.Vertices:
                pygame.draw.circle(self.screen, self.shapeColor, (vertex.x, vertex.y), 5)

    def cursor_update(self):
        mse = pygame.mouse.get_pos()
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

        for button in self.buttons.values():
            if button.on_button(*mse):
                pygame.mouse.set_cursor(*pygame.cursors.tri_left)

        for cb in self.checkboxes.values():
            if cb.on_checkbox(*mse):
                pygame.mouse.set_cursor(*pygame.cursors.tri_left)

        if self.debug_path_flag:
                pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        if self.polygon_build:
            pygame.mouse.set_cursor(*pygame.cursors.diamond)

        if self.remove_flag:
            pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        if self.debug_point_flag:
            pygame.mouse.set_cursor(*pygame.cursors.broken_x)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, self
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mse = pygame.mouse.get_pos()
                if self.buttons["polygon"].on_button(*mse):
                    if not self.polygon_build:
                        self.current_polygon = PolygonMesh()
                    else:
                        if len(self.current_polygon.Vertices) >= 3:
                            vertex, edge = self.current_polygon.dcel_info()
                            intersections = isect_polygon(vertex)

                            if len(intersections) == 0:
                                self.polygons.append(self.current_polygon)

                                new_vertices, new_edges = get_vertex_edge_relation(self.polygons)

                                self.current_dcel = Dcel(new_vertices, new_edges)
                                self.current_polygon.qhull()
                                self.compute_tz_map()
                            else:
                                print("Polygon intersects itself, create new polygon")
                        else:
                            int("Polygon too small")
                    self.polygon_build = not self.polygon_build
                    return True, self

                elif self.buttons["run"].on_button(*mse):
                    if self.checkboxes['robot_point'].is_checked():
                        self.compute_free_space()
                    return True, self

                elif self.buttons["remove"].on_button(*mse):

                    self.remove_flag = not self.remove_flag

                    return True, self

                elif self.buttons['debug_path'].on_button(*mse):
                    self.debug_path_flag = not self.debug_path_flag
                    return True, self

                elif self.buttons["debug_step"].on_button(*mse):
                    self.debug_step = (self.debug_step + 1) % self.tz_map.totTrapezoids if self.tz_map else 0
                    return True, self

                elif self.buttons["debug_point"].on_button(*mse):
                    self.debug_point_flag = not self.debug_point_flag
                    return True, self
                elif self.checkboxes['convex_hull'].on_checkbox(*mse):
                    self.checkboxes['convex_hull'].change_state()
                    return True, self

                elif self.checkboxes['robot_point'].on_checkbox(*mse):
                    self.checkboxes['robot_point'].change_state()
                    return True, self

                elif self.checkboxes['tmap'].on_checkbox(*mse):
                    self.checkboxes['tmap'].change_state()
                    return True, self

                elif self.polygon_build:
                    self.current_polygon.add_vertex(*mse)

                elif self.debug_point_flag:
                    if self.tz_map:
                        self.tz_map.print_traversal_path(Point("Test", *mse))
                        print("")
                    self.debug_point_flag = False

                elif self.debug_path_flag:
                    self.debug_path_segment.append(mse)
                    if self.debug_path_flag and len(self.debug_path_segment) % 2 == 0:
                        test_segment = Segment(Point("test", *self.debug_path_segment[0]),
                                               Point("test", *self.debug_path_segment[1]))

                        for indx, p in enumerate(self.polygons):
                            if any(p.contains_path(test_segment)):
                                print("Segment: ", test_segment.segment_coordinates, "is inside polygon: ", indx)
                        self.debug_path_flag = False
                elif self.remove_flag:
                    for index, polygon in enumerate(self.polygons):
                        if polygon.is_inside(mse):
                            self.remove_flag = not self.remove_flag
                            print("Removing polygon", index + 1)
                            self.polygons.pop(index)
                            self.compute_tz_map()
                            self.compute_free_space()
            elif event.type == pygame.MOUSEMOTION:
                self.cursor_update()

        self.screen.blit(self.background, self.background.get_rect(), self.background.get_rect())
        for button in self.buttons.values():
            button.update()

        for checkbox in self.checkboxes.values():
            checkbox.update()
        self.draw_polygons()

        if self.checkboxes['convex_hull'].is_checked() or self.checkboxes['tmap'].is_checked():
            self.debug_draw()
        pygame.display.update()

        return True, self

    def compute_free_space(self):
        # Get TZ_map segment vertices
        trav_tree = traverse_tree([], self.tz_map.root)
        segment_objects = [node.line_segment for node in trav_tree if node.type == "ynode"]
        vertex, edge = get_vertex_edge_relation(self.polygons)
        self.tz_map_vertical_segments = {'up': [], 'down': []}

        for idp, point in enumerate(vertex):
            up, down = [], []
            for ids, segment in enumerate(segment_objects + self.get_border_segments()):
                new_y = segment.getY(point[0], integer=True)
                if new_y is not None and new_y != point[1]:
                    name = "P" + str(idp) + "S" + str(ids)
                    new_segment = Segment(Point("p" + name, *point), Point("q" + name, point[0], new_y))
                    if new_y < point[1]:
                        up.append(new_segment)
                    else:
                        down.append(new_segment)

            for new_segment in up:
                intersects_any_polygon = any([any(p.contains_path(new_segment)) for p in self.polygons])
                if intersects_any_polygon:
                    up.remove(new_segment)

            for new_segment in down:
                intersects_any_polygon = any([any(p.contains_path(new_segment, up=False)) for p in self.polygons])
                if intersects_any_polygon:
                    down.remove(new_segment)

            up.sort(key=lambda seg: seg.length)
            down.sort(key=lambda seg: seg.length)

            if len(up) > 0:
                self.tz_map_vertical_segments['up'].append(up[0])
            if len(down) > 0:
                self.tz_map_vertical_segments['down'].append(down[0])

    def compute_tz_map(self):
        x, y = self.screen.get_size()
        new_vertices, new_edges = get_vertex_edge_relation(self.polygons)
        segments = []
        for edge in new_edges:
            segments.append((new_vertices[edge[0]], new_vertices[edge[1]]))
        bbox = (0, 0, x - 1, y - 1)
        self.tz_map = build_tmap(segments, bbox)

    def get_border_segments(self):
        x1, y1 = 0, 0
        x2, y2 = self.screen.get_size()
        lower_eft = Point('ll', x1, y1)
        upper_right = Point('ur', x2, y2)
        lower_right = Point('lr', x2, y1)
        upper_left = Point('ul', x1, y2)
        return [Segment(upper_left, upper_right, 'bT'), Segment(lower_eft, lower_right, 'bB')]


def get_vertex_edge_relation(polygons):
    """
    Creates edge relation to vertices needed for a DCEL using the polygon list
    """
    new_edges, new_vertices = [], []
    total_offset = 0

    for index, p in enumerate(polygons):
        curr_vert, curr_edges = p.dcel_info()

        if index > 0:
            for edge in curr_edges:
                new_edges.append((edge[0] + total_offset, edge[1] + total_offset))
        else:
            new_edges = curr_edges

        new_vertices = new_vertices + curr_vert
        total_offset += len(curr_edges)
    return new_vertices, new_edges
