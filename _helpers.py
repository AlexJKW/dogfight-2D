import pygame
import os, sys

# ***********************************************                        ***********************************************
# *********************************************** @START GENERIC CLASSES ***********************************************
# ***********************************************                        ***********************************************

# Define helper lists containing allowed resource extensions and resolution of the screen
graphics    = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]
sound       = [".wav", ".mp3"]

# Generic parent class for all game sprites containing commonly used functionalities
class GameSprite(pygame.sprite.Sprite):

    # Resource loader method available to all children classes 
    # (modified version of an exmaple provided by the official documentation)
    def resourceLoader(self, name, output=False):

        if os.path.splitext(name)[1] in graphics:

            filepath = os.path.join('sprites', name)

            try:

                if output:
                    return pygame.image.load(filepath).convert_alpha()
                
                self.image = pygame.image.load(filepath).convert_alpha()
                self.rect = self.image.get_rect()

            except pygame.error as message:
                print('Cannot load image:' + name)
                raise SystemExit(message)

        elif os.path.splitext(name)[1] in sound:

            filepath = os.path.join('sounds', name)

            class NoneSound:
                def play(self): pass

            if not pygame.mixer:
                return NoneSound()

            try:
                self.sound = pygame.mixer.Sound(filepath)

            except pygame.error as message:
                print ('Cannot load sound: ' + name)
                raise SystemExit(message)

    # Sound player: if loop is specified plays the `self.sound` repeatedly otherwise just once
    def playSound(self, loop=None):

        if loop is None:
            pygame.mixer.Sound.play(self.sound)

        else:
            pygame.mixer.Sound.play(self.sound, -1)