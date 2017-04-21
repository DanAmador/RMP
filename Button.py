#!/usr/bin/python

import pygame


class Button:
    def __init__(self, x, y, width, height, text):
        self.screen = pygame.display.get_surface()
        self.text = text
        self.buttonRect = pygame.Rect(x, y, width, height)

        self.color = pygame.Color(150, 150, 150)

        if pygame.font:
            font = pygame.font.Font(None, 22)
            self.textDisp = font.render(self.text, 1, (100, 100, 100))

        self.textRect = self.textDisp.get_rect(centerx=x + width / 2, centery=y + height / 2 + 1)

    def update(self):
        pygame.draw.rect(self.screen, self.color, self.buttonRect)
        self.screen.blit(self.textDisp, self.textRect)

    def on_button(self, x, y):
        if self.get_x() <= x <= (self.get_x() + self.get_width()) and self.get_y() <= y <= (
                    self.get_y() + self.get_height()):
            return True
        else:
            return False

    def get_x(self):
        return self.buttonRect.x

    def get_y(self):
        return self.buttonRect.y

    def get_width(self):
        return self.buttonRect.w

    def get_height(self):
        return self.buttonRect.h

    def get_text(self):
        return self.text

    def set_y(self, y):
        self.buttonRect.y = y
        self.textRect = self.textDisp.get_rect(centerx=self.buttonRect.x + self.buttonRect.w / 2,
                                               centery=self.buttonRect.y + self.buttonRect.h / 2 + 1)

    def set_color(self, color):
        self.color = color
