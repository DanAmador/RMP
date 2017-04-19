#!/usr/bin/python

import pygame
from pygame.locals import *

class Checkbox():
	def __init__(self, x, y, text, checked = False):
		self.screen = pygame.display.get_surface()
		self.checked = checked
		self.text = text

		self.checkboxRect = pygame.Rect(x, y, 15, 15)
		self.crossRect = pygame.Rect(x + 2, y + 2, 11, 11)
		self.color = pygame.Color(150, 150, 150)
		if pygame.font:
			font = pygame.font.Font(None, 22)
			self.textDisp = font.render(self.text, 1, self.color)

		self.textRect = self.textDisp.get_rect(x = x + 25, centery = y + 9)
	
	def update(self):
		pygame.draw.rect(self.screen, (150, 150, 150), self.checkboxRect)

		if self.checked:
			pygame.draw.rect(self.screen, (75, 75, 75), self.crossRect)

		self.screen.blit(self.textDisp, self.textRect)

	def onCheckbox(self, x, y):
		if x >= self.getX() and x <= (self.getX() + 25 + self.textRect.w) and y >= self.getY() and y <= (self.getY() + 15):
			return True
		else:
			return False

	def changeState(self):
		if self.isChecked():
			self.uncheck()
		else:
			self.check()

	def isChecked(self):
		return self.checked

	def check(self):
		self.checked = True

	def uncheck(self):
		self.checked = False

	def getX(self):
		return self.checkboxRect.x

	def getY(self):
		return self.checkboxRect.y