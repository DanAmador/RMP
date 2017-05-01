import copy

from Button import *
from Checkbox import *
from DCEL import Dcel, Vertex, is_in_convex_polygon
from PolygonMesh import *
from TrapezoidalMap import build_Tmap
from poly_point_isect import isect_polygon, isect_segments


class Planner:
    def __init__(self):
        menuPos = 0
        self.screen = pygame.display.get_surface()
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()

        self.background_color = (50, 50, 50)
        self.shapeColor = (150, 150, 150)
        self.debugColor = (178, 34, 34)
        self.intersect_color = (0, 0, 255)

        self.background.fill(self.background_color)

        self.polygons = []
        self.currentPolygon = None

        self.intersections = []
        self.intersection_segments = []

        self.polygon_build = False
        self.remove_flag = False

        self.current_dcel = None

        self.tz_map = None

        self.buttons = {}
        self.checkboxes = {}

        self.buttons["run"] = Button(0, menuPos, 100, 40, "RUN")
        self.buttons["polygon"] = Button(0, menuPos + 40, 100, 40, "POLYGON")
        self.buttons["remove"] = Button(0, menuPos + 80, 100, 40, "REMOVE")

        self.checkboxes['debug'] = Checkbox(110, 0, "Debug Info")
        self.checkboxes['point'] = Checkbox(110, 20, "Robot is a point?")

        pygame.display.flip()

    def create_border_polygon(self):
        x, y = self.screen.get_size()
        border_poly = PolygonMesh()
        border_poly.add_vertex(0, 0)
        border_poly.add_vertex(x, 0)
        border_poly.add_vertex(x, y)
        border_poly.add_vertex(0, y)

        return border_poly

    def debug_draw(self):
        for shape in self.polygons:
            for line in shape.polygon_coordinates(ch=True):
                pygame.draw.line(self.screen, self.debugColor, line[0], line[1], 5)

        for inter in self.intersections:
            pygame.draw.circle(self.screen, self.intersect_color, inter, 5)

        for segment in self.intersection_segments:
            pygame.draw.line(self.screen, (0, 255, 0), segment[0], segment[1], 5)

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

        if self.polygon_build:
            pygame.mouse.set_cursor(*pygame.cursors.diamond)

        if self.remove_flag:
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
                            else:
                                print("Polygon intersects itself, create new polygon")
                        else:
                            int("Polygon too small")
                    self.polygon_build = not self.polygon_build
                    return True, self

                elif self.buttons["run"].on_button(*mse):
                    # TODO ADD
                    if self.checkboxes['point']:
                        self.compute_free_space()
                    return True, self

                elif self.buttons["remove"].on_button(*mse):

                    self.remove_flag = not self.remove_flag

                    return True, self

                elif self.checkboxes['debug'].on_checkbox(*mse):
                    self.checkboxes['debug'].change_state()
                    return True, self

                elif self.checkboxes['point'].on_checkbox(*mse):
                    self.checkboxes['point'].change_state()
                    return True, self

                elif self.polygon_build:
                    self.current_polygon.add_vertex(*mse)

                elif self.remove_flag:
                    for index, polygon in enumerate(self.polygons):
                        if is_in_convex_polygon(mse, polygon.polygon_coordinates(ch=True)):
                            self.remove_flag = not self.remove_flag
                            print("Removing polygon", index + 1)
                            self.polygons.pop(index)
                    self.compute_free_space()
            elif event.type == pygame.MOUSEMOTION:
                self.cursor_update()

        self.screen.blit(self.background, self.background.get_rect(), self.background.get_rect())
        for button in self.buttons.values():
            button.update()

        for checkbox in self.checkboxes.values():
            checkbox.update()
        self.draw_polygons()

        if self.checkboxes['debug'].is_checked():
            self.debug_draw()
        pygame.display.update()

        return True, self

    def compute_free_space(self):
        x, y = self.screen.get_size()
        new_vertices, new_edges = get_vertex_edge_relation(self.polygons)
        segments = []
        for edge in new_edges:
            segments.append((new_vertices[edge[0]], new_vertices[edge[1]]))
        bbox = (0, 0, x, y)
        self.tz_map = build_Tmap(segments, bbox)


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
