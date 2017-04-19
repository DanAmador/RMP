import pygame, sys
from pygame.locals import *
from Planner import *
pygame.init()

class RMP():
	def __init__(self):
			screen_width = 1000
			screen_height = 600
			pygame.init()
			pygame.display.set_mode((screen_width, screen_height))
			pygame.display.set_caption("Robot Motion Planner")
			current_scene = Planner()

			clock = pygame.time.Clock()

			game = True

			while game:
				game = current_scene.update()
				clock.tick(60)
			pygame.quit()
if __name__ == '__main__':
	RMP()