import pygame
from DCEL import Dcel, DcelError
from Button import *
from Checkbox import *
from pygame.locals import *
from PolygonMesh import *


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

        self.dcels = []
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
            pygame.draw.polygon(self.screen, self.shapeColor, shape.polygon_coordinates(), 0)
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
                        # TODO create intersection algorithm with dcel
                        self.current_dcel = Dcel(*self.current_polygon.dcel_info())
                        if not self.current_dcel.intersects_itself():
                            self.current_polygon.qhull()
                            self.polygons.append({
                                'convex_hull' : Dcel(*self.current_polygon.dcel_info(ch=True)),
                                'polygon': self.current_dcel
                            })
                            self.dcels.append(self.current_dcel)
                        else:
                            print("Polygon intersects itself, create new polygon")
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
