import pygame
from Button import *
from Checkbox import *
from pygame.locals import *
from PolygonMesh import *
class Planner:
    def __init__(self):
        self.currentPolygon = None
        menuPos = 0
        self.screen = pygame.display.get_surface()
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background_color = (50,50,50)
        self.shapeColor = (150,150,150)
        self.debugColor = (178,34,34)
        self.background.fill(self.background_color)
        self.polygons = []
        self.buttons = {}
        self.checkboxes = {}
        self.polygon_build = False
        self.remove_flag = False
        self.buttons["run"] = Button(0, menuPos, 100, 40, "RUN")
        self.buttons["polygon"] = Button(0, menuPos + 40, 100,40,"POLYGON")
        self.buttons["remove"] = Button(0, menuPos + 80, 100, 40, "REMOVE")

        self.checkboxes['debug'] = Checkbox(110,0,"Debug Info")
        self.checkboxes['point'] = Checkbox(110,20, "Robot is a point?")

        pygame.display.flip()


    def drawDebug(self):
        for shape in self.polygons:
            for line in shape.polygonCoordinates(ch=True):
                pygame.draw.line(self.screen,self.debugColor,line[0],line[1],5)

    def drawPolygons(self):
        for shape in self.polygons:
            pygame.draw.polygon(self.screen, self.shapeColor, shape.polygonCoordinates(), 0)
        if self.polygon_build:
            for vertex in self.current_polygon.Vertices:
                    pygame.draw.circle(self.screen, self.shapeColor,(vertex.x, vertex.y),5)

    def cursorUpdate(self):
        mse = pygame.mouse.get_pos()
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

        for button in self.buttons.values():
            if button.onButton(*mse):
                pygame.mouse.set_cursor(*pygame.cursors.tri_left)

        for cb in self.checkboxes.values():
            if cb.onCheckbox(*mse):
                pygame.mouse.set_cursor(*pygame.cursors.tri_left)

        if self.polygon_build:
            pygame.mouse.set_cursor(*pygame.cursors.diamond)

        if self.remove_flag:
            pygame.mouse.set_cursor(*pygame.cursors.broken_x)

    def update(self):
        mouse = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, self

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mse = pygame.mouse.get_pos()
                if self.buttons["polygon"].onButton(*mse):
                    if not self.polygon_build:
                        self.current_polygon = PolygonMesh()
                    else:
                        self.current_polygon.qhull()
                        self.polygons.append(self.current_polygon)
                    self.polygon_build = not self.polygon_build
                    return True,self
                elif self.buttons["run"].onButton(*mse):
                    return True,self
                elif self.buttons["remove"].onButton(*mse):
                    self.remove_flag = not self.remove_flag
                    return True,self
                elif self.checkboxes['debug'].onCheckbox(*mse):
                    self.checkboxes['debug'].changeState()
                    return True, self
                elif self.checkboxes['point'].onCheckbox(*mse):
                    self.checkboxes['point'].changeState()
                    return True, self
                elif self.polygon_build:
                    self.current_polygon.addVertex(*mse)
            elif event.type == pygame.MOUSEMOTION:
                self.cursorUpdate()


        self.screen.blit(self.background, self.background.get_rect(), self.background.get_rect())
        for button in self.buttons.values():
            button.update()

        for checkbox in self.checkboxes.values():
            checkbox.update()
        self.drawPolygons()

        if self.checkboxes['debug'].isChecked():
            self.drawDebug()
        pygame.display.update()

        return True, self