import pygame
from Button import *
from Checkbox import *
from pygame.locals import *

class Planner:
    def __init__(self):
        menuPos = 0
        self.screen = pygame.display.get_surface()
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((50, 50, 50))

        self.buttons = {}

        self.buttons["run"] = Button(0, menuPos, 100, 40, "RUN")
        self.buttons["polygon"] = Button(0, menuPos + 40, 100,40,"POLYGON")
        self.buttons["remove"] = Button(0, menuPos + 80, 100, 40, "REMOVE")


        pygame.display.flip()

    def update(self):

        mouse = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, self

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mse = pygame.mouse.get_pos()

                if self.buttons["polygon"].onButton(*mse):

                    return True,self

                elif self.buttons["run"].onButton(*mse):
                    return True,self

                elif self.buttons["remove"].onButton(*mse):
                    return True,self


            elif event.type == pygame.MOUSEMOTION:
                mse = pygame.mouse.get_pos()

                pygame.mouse.set_cursor(*pygame.cursors.arrow)

                for button in self.buttons.values():
                    if button.onButton(*mse):
                        pygame.mouse.set_cursor(*pygame.cursors.tri_left)

        self.screen.blit(self.background, self.background.get_rect(), self.background.get_rect())



        for button in self.buttons.values():
            button.update()

        pygame.display.update()

        return True, self