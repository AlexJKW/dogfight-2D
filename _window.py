import pygame

# ***********************************************                         ***********************************************
# *********************************************** @START WINDOW SETTINGS  ***********************************************
# ***********************************************                         ***********************************************


# Initialise the Pygame object
pygame.init()


# Initialise the window
resolution  = {"width" : 800, "height" : 600}

screen      = pygame.display.set_mode((resolution['width'], resolution['height']))
screen.fill(pygame.Color(126, 213, 234))

background  = pygame.Surface(screen.get_size())
background  = background.convert()
background.fill(pygame.Color(126, 213, 234))

pygame.mouse.set_visible(False)
pygame.display.set_caption("Dogfight2D (2018)")