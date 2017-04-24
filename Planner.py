from Button import *
from Checkbox import *
from DCEL import Dcel, Vertex, is_in_convex_polygon
from PolygonMesh import *
from poly_point_isect import isect_polygon


class Planner:
    def __init__(self):
        menuPos = 0
        self.screen = pygame.display.get_surface()
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()

        self.background_color = (50, 50, 50)
        self.shapeColor = (150, 150, 150)
        self.debugColor = (178, 34, 34)

        self.background.fill(self.background_color)

        self.polygons = []
        self.currentPolygon = None

        self.polygon_build = False
        self.remove_flag = False

        self.current_dcel = None

        self.buttons = {}
        self.checkboxes = {}

        self.buttons["run"] = Button(0, menuPos, 100, 40, "RUN")
        self.buttons["polygon"] = Button(0, menuPos + 40, 100, 40, "POLYGON")
        self.buttons["remove"] = Button(0, menuPos + 80, 100, 40, "REMOVE")

        self.checkboxes['debug'] = Checkbox(110, 0, "Debug Info")
        self.checkboxes['point'] = Checkbox(110, 20, "Robot is a point?")

        pygame.display.flip()

    def debug_draw(self):
        for shape in self.polygons:
            for line in shape.polygon_coordinates(ch=True):
                pygame.draw.line(self.screen, self.debugColor, line[0], line[1], 5)

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
                                new_vertices, new_edges = [], []
                                total_offset = 0
                                self.polygons.append(self.current_polygon)

                                """
                                Creates edge relation to vertices needed for a DCEL using the polygon list
                                """
                                for index, p in enumerate(self.polygons):
                                    curr_vert, curr_edges = p.dcel_info()

                                    if index > 0:
                                        for edge in curr_edges:
                                            new_edges.append((edge[0] + total_offset, edge[1] + total_offset))
                                    else:
                                        new_edges = curr_edges

                                    new_vertices = new_vertices + curr_vert
                                    total_offset += len(curr_edges)

                                self.current_dcel = Dcel(new_vertices, new_edges)
                                self.current_polygon.qhull()
                            else:
                                print("Polygon intersects itself, create new polygon")
                        else:
                            int("Polygon too small")
                    self.polygon_build = not self.polygon_build
                    return True, self

                elif self.buttons["run"].on_button(*mse):
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
