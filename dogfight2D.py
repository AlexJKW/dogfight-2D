# Import external modules
from _helpers import *
from _window  import *

import math, random


class Moveable(GameSprite):

    # Flag used to block newly spawned clones from infinite reproduction
    reproduceItself = True

    # Generic update method capable of handling animation of objects which should
    # animate only when the player moves (e.g. landscape, mountains, ground), and those that should animate
    # all the time (e.g. clouds, passive enemies)
    def update(self, motion=False, always=False):
        if not always:
            if motion == True:
                self.scroll()

            else:
                self.stop()
        else:
            self.scroll()

    # Motion generic method
    def scroll(self):

        if not isinstance(self, Ufo):
            
            # Rectangle of each subclass apart from Ufo is decremented by indivdually defined scrollingSpeed
            self.rect.left -= self.scrollingSpeed

        # Each subclass has specific `disappearCriteria` (i.e. when new object should be replicated)
        if self.disappearCriteria and self.reproduceItself == True:

            # Call spawn function on the self to create a copy of a game sprite that disappeared
            # and place the new object on the individualy defined in a subclass `destination` tuple
            # DEBUG print("Object: {}, Coordinates: {}".format(self.name, clonedProp.rect))
            clonedProp      = self.spawn()
            clonedProp.rect = clonedProp.rect.move(self.destination)
            
            # When clone was created set the flag back to the False to prevent infinite object creation
            self.reproduceItself = False

            # Increase newly created bombs' speed to make it more challenging
            if isinstance(self, Bomb):

                # Add random fraction to the parent' speed but if it exceeds defined threshold
                # lower it down
                increment = random.choice([1/5, 1/4, 1/2, 1]) + self.scrollingSpeed

                clonedProp.scrollingSpeed = increment if increment < 12 else 5
                
                # DEBUG print('Parent: ', self.scrollingSpeed, 'Child: ', clonedProp.scrollingSpeed)

            # Basic garbage collection: following cloning remove the old disappeared sprite 
            # from the sprite groups it belonged to (kill()) as well as the reference (del)
            # DEBUG print("Object killed: {}, Coordinates: {}".format(self.name, self.rect))
            if not screen.get_rect().contains(self.rect):
                self.kill()
                del self  
            
    # Motion stop
    def stop(self):
        self.scroolSpeed = 0

    # Flexibile method to reproduce the child objects which benefits from the special attribute `instance.__class__`. 
    # When referring `.__class__` on the `self` i.e. `self.__class__`, an instance of the class from where it was called
    # will be returned. This works because the method is inherited by all children classes and so the `self` refers to 
    # the subclass instances, thus the subclass instance is reproduced. For instance, if the new Ground segment needs
    # to be genereated this method will return a new Ground(...) object with the same arguments as its ancestor.
    # Note: it was crucial to achieve that a new object was produced and not merely a new reference to the old one
    
    # From official documentation section 9.4. Random Remarks: 
	    # "Each value is an object, and therefore has a class (also called its type). It is stored as object.__class__."

    def spawn(self):
        return self.__class__(self.name, self.groups, priority=self.priority)






# ***********************************************                            ***********************************************
# *********************************************** @START GAME ASSETS CLASSES ***********************************************
# ***********************************************                            ***********************************************

# Each consecutive landscape, mountain, and ground duplicates should have the same speed so class variable can be used to ensure that
# Each class defines only essential parameters that are specific for each child which are then handled by the parent

# Importantly the update method constantly refreshes two variables: 
    # 1) `self.disappearCriteria` which determines when the new object of the 
    #     same kind should be reproduced (e.g. when its left or perhaps right border will cross a particular edge of the screen)
    # 2) `self.destination` which determines where the newly reproduced instance should be position relative to the `self.disappearCriteria`

# Then the responsibility of moving an object and replicating it when necessary is handled by the parent class, hence the call to super().update(motion)
# where motion is the flag indicating if scrolling should occur or stop (for some classes it's always True, for others it changes in accordance with the player's state)
# i.e. background elements stop scrolling when the player stop moving, but clouds and dumb enemies keep moving constantly
class Landscape(Moveable):

    scrollingSpeed = 1

    def __init__(self, name, *groups, priority):

        self.name      = name
        self.priority  = priority
        self._layer    = self.priority
        self.groups    = groups
        GameSprite.__init__(self, *groups)

        self.resourceLoader(name)
        self.rect.bottomleft = (0,resolution['height'])

    def update(self, motion):

        self.disappearCriteria = self.rect.right <= resolution['width']
        self.direction = self.rect
        self.destination       = (0, 0)
        super().update(motion)


class Mountain(Moveable):

    scrollingSpeed = 2

    def __init__(self, name, *groups, priority):

        self.name      = name
        self.priority  = priority
        self._layer    = self.priority
        self.groups    = groups
        GameSprite.__init__(self, *groups)

        self.resourceLoader(name)
        self.rect.bottomright = (resolution['width'], resolution['height'])

    def update(self, motion):

        self.disappearCriteria = self.rect.right <= 0
        self.destination       = (resolution['width']+random.randint(0,500), 0)
        super().update(motion)


class Ground(Moveable):

    scrollingSpeed = 12

    def __init__(self, name, *groups, priority):

        self.name      = name
        self.priority  = priority
        self._layer    = self.priority
        self.groups    = groups
        GameSprite.__init__(self, *groups)

        self.resourceLoader(name)
        self.rect.bottomleft = (0, resolution['height'])

    def update(self, motion):

        self.disappearCriteria = self.rect.right <= resolution['width']
        self.destination       = (0, 0)
        super().update(motion)


class Cloud(Moveable):

    # Here, scrollng speed is defined as an instance variable to randomize speed of each cloud

    def __init__(self, name, *groups, priority):
        
        self.name       = name
        self.priority   = priority
        self._layer     = self.priority
        self.groups     = groups
        self.scrollingSpeed = random.randint(2,5)
        GameSprite.__init__(self, *groups)

        self.resourceLoader(name)
        self.rect.topright = (random.randint(resolution['width'], resolution['width']+600), random.randint(1, 250))

    def update(self, motion):

        self.disappearCriteria = self.rect.right <=0 
        self.destination       = (resolution['width']+random.randint(0,500), 0)
        super().update(motion=True, always=True)


class Enemy(Moveable):

    # Starting index for explosion animation and flag that indicates if enemy was striked
    frameIndex = 0
    striked    = False

    def __init__(self):
        self.resourceLoader('explosion.wav')

    # Basic method which is called from within the main loop when the player collides with the enemy
    # It sets the the `explode` flag of the striked enemy to True which used in the update method of that enemy
    # to determine if the explosion animation is to be played
    def explode(self):
        self.striked = True
        self.playSound()
    
    # Method used to play explosion animation following the collision with an enemy
    def animate(self):

        # Contains list of surfaces returned by the wrapper of the load_image() function which applied to each element of the list
        explosion = [self.resourceLoader(frame, output=True) for frame in ['explosion{}.png'.format((i)) for i in range(0, 9)]]

        # Increment index of the frame, check if it exceeds the size of a list and if it does than restart 
        # index and teleport the sprite outside the screen inducing its reproduction (see Moveable generic class and self.disappearCriteria condition)
        self.frameIndex += 1
        if self.frameIndex >= len(explosion):
            self.frameIndex = 0
            self.rect.x     = -500
        
        # Replace the image of the enemy for consecutive images of the explosion sequence
        self.image = explosion[self.frameIndex]

    def update(self, motion, always=False):
        super().update(motion, always)

        # If the bomb was striked
        if self.striked:

            # Remove the sprite from the dumb_enemies group immediately after the first collision
            # to prevent multiple damages (this sprite will disappear from the screen anyway, thus
            # the newly created object will belong to the dumb_enemies again by default again)
            dumb_enemies.remove(self)

            # Animate explosion
            self.animate()


class Bomb(Enemy):

    scrollingSpeed = 1
    damage         = -20   

    def __init__(self, name, *groups, priority):
        super().__init__()

        self.name       = name
        self.priority   = priority
        self._layer     = self.priority
        self.groups     = groups
        self.angle      = 0
        GameSprite.__init__(self, *groups)

        self.resourceLoader(name)
        self.rect.center = (resolution['width']+random.randint(0, 500), resolution['height']/2)

    def update(self, motion):

        self.disappearCriteria = self.rect.right <= 0
        self.destination       = (resolution['width']+random.randint(0,500), random.randint(-290, 100))
        super().update(motion=True, always=True)

        if not self.striked:

            # `pygame.transform.rotate` creates a new rotated image each time it is called,
            # therefore we need to apply it on the original file with increasingly bigger angle
            # of rotation instead of attempting to rotate the rotated copy as it leads to memory issues

            # From documentation: 
                # "Some of the transforms are considered destructive. 
                #  These means every time they are performed they lose pixel data. Common examples of this are resizing and rotating. 
                #  For this reason, it is better to retransform the original surface than to keep transforming an image multiple times."
            original    = self.resourceLoader(self.name, output=True)
            center      = self.rect.center
            self.angle += random.randint(1, 10)
            self.image = pygame.transform.rotate(original, self.angle)
            self.rect  = self.image.get_rect(center=center)
                    

class Cactus(Enemy):

    scrollingSpeed = 5
    damage         = -10

    def __init__(self, name, *groups, priority):
        super().__init__()

        self.name      = name
        self.priority  = priority
        self._layer    = self.priority
        self.groups    = groups
        GameSprite.__init__(self, *groups)

        self.resourceLoader(name)
        self.rect.bottomright = (resolution['width'], resolution['height']-160)   

    def update(self, motion):

        self.disappearCriteria = self.rect.right <= 0
        self.destination       = (resolution['width']+random.randint(0,1000), 0)
        super().update(motion)


class Ufo(Enemy):

    scrollingSpeed  = 1
    damage          = -100   
    counter         = 700
    

    def __init__(self, name, *groups, priority):
        super().__init__()

        self.name       = name
        self.priority   = priority
        self._layer     = self.priority
        self.groups     = groups
        self.counter    = 700
        self.swap       = True
        GameSprite.__init__(self, *groups)

        self.resourceLoader(name)
        self.rect.center = (300, -500)
        self.abducted = False
    

    def update(self, motion):

        if not self.abducted:

            self.disappearCriteria = self.rect.right <= 0
            self.destination       = (random.randint(self.image.get_size()[0], resolution['width']-self.image.get_size()[1]), 200)
            super().update(motion)
        
            #if collision between ufo and player, change the image of the UFO and 
            if pygame.sprite.collide_rect(self, player):
                self.resourceLoader('ufo2.png')
                self.abducted = True
                player.life = 0 # Sometimes the player deleted before health can be lowered
                player.kill()
                    
            else:

                # Define vectors for the aliens and the player
                character = pygame.math.Vector2(player.rect.x, player.rect.y)
                aliens    = pygame.math.Vector2(self.rect.x, self.rect.y)
        
                # Calculate the displacement between the ufo and the player i.e. direction of movement
                movement  = character - aliens

                # Normalize the vector to the length of 1 and multiply it by the inverse of a gradually decreasing counter
                # As a result, UFO's distance to the player decreases as a function of time (or counter which relies on FPS)
                movement.normalize()
                self.counter = self.counter - 1/5 if self.counter - 1/10 > 0 else 1
                movement    *= self.scrollingSpeed/self.counter

                # Gradually move the UFO towards the player
                self.rect.x += movement.x
                self.rect.y += movement.y        

                # Keep the original rect to align new graphics below in the same place
                original   = self.rect.topleft

                # Load up UFO's beam light on "THEY'VE SEEN YOU" event
                if self.counter < 400 and self.swap:
                    # Switch on the beam light
                    self.resourceLoader('ufo1.png')

                    # Place the modified UFO graphics on the same location as the previous one
                    self.rect  = self.image.get_rect(topleft=original)
                    self.swap  = False
                    self.resourceLoader('aliens.wav')
                    self.playSound()
                    self.resourceLoader('explosion.wav')


class Bullet(GameSprite):
    
    def __init__(self, name, coordinates, *groups, priority):
        
        self.priority = priority
        self._layer = self.priority
        GameSprite.__init__(self, *groups)
        
        self.resourceLoader(name)
        self.rect = coordinates
    
    # We just define argument so that it complies with the form of all other update() 
    # methods of objects belonging to the layers sprite group. This allowed bullet sprite
    # to be included within the `layers` group as well, thereby drawing and updating all sprites simultaneously
    def update(self, notused):
        self.rect.x += 20

        # Remove object from bullets group when it reaches edge of screen
        if self.rect.x >= resolution["width"]:
            self.kill()


class Cowboy(GameSprite):

    life = 100
    hit  = False
    dead = False

    def __init__(self, name, *groups, priority):

        self.priority       = priority
        self._layer         = self.priority
        self.frameIndex     = 0
        self.angle          = 0      
        self.previous_shot  = 0  
        self.current_shot   = pygame.time.get_ticks()
        self.action         = "idle"
       
        GameSprite.__init__(self, *groups)

        # Nested dictionary  provides a mapping between the key pressed and the desired animation as dictated by the action name and direction
        # Format: action->direction->property {play / move}; `play` contains list of surfaces returned by the wrapper of the load_image() function
        # whereas `move` includes change in displacement possible for each direction and action. Four pairs of tuples essentially define the degree of
        # freedom for each action.
        self.control = {"walk" : 
                                {
                                    "up"    : {"play" : [self.resourceLoader(frame, output=True) for frame in ['l_walk{}.png'.format((i)) for i in range(0, 1)]], "move" : ( 0,  0 )}, 
                                    "down"  : {"play" : [self.resourceLoader(frame, output=True) for frame in ['r_walk{}.png'.format((i)) for i in range(0, 1)]], "move" : ( 0,  0 )},
                                    "left"  : {"play" : [self.resourceLoader(frame, output=True) for frame in ['l_walk{}.png'.format(i)   for i in range(0, 8)]], "move" : ( 2,  0 )}, 
                                    "right" : {"play" : [self.resourceLoader(frame, output=True) for frame in ['r_walk{}.png'.format(i)   for i in range(0, 8)]], "move" : (-2,  0 )}
                                },

                          "fly" : 
                                {   "up"    : {"play" : [self.resourceLoader(frame, output=True) for frame in ['r_fly{}.png'.format((i))  for i in range(0, 1)]], "move" : ( 0,  5 )}, 
                                    "down"  : {"play" : [self.resourceLoader(frame, output=True) for frame in ['r_fly{}.png'.format((i))  for i in range(0, 1)]], "move" : ( 0,  0 )},
                                    "left"  : {"play" : [self.resourceLoader(frame, output=True) for frame in ['r_fly{}.png'.format((i))  for i in range(0, 1)]], "move" : ( 4, -4 )}, 
                                    "right" : {"play" : [self.resourceLoader(frame, output=True) for frame in ['r_fly{}.png'.format((i))  for i in range(0, 1)]], "move" : (-4, -4 )},
                                },

                          "idle" : 
                                {   "up"    : {"play" : [self.resourceLoader(frame, output=True) for frame in ['l_idle{}.png'.format((i)) for i in range(0, 1)]], "move" : ( 0,  0 )}, 
                                    "down"  : {"play" : [self.resourceLoader(frame, output=True) for frame in ['r_idle{}.png'.format((i)) for i in range(0, 1)]], "move" : ( 0,  0 )},
                                    "left"  : {"play" : [self.resourceLoader(frame, output=True) for frame in ['l_idle{}.png'.format((i)) for i in range(0, 1)]], "move" : ( 0,  0 )},
                                    "right" : {"play" : [self.resourceLoader(frame, output=True) for frame in ['r_idle{}.png'.format((i)) for i in range(0, 1)]], "move" : ( 0,  0 )}
                                },
                        
                          "shoot":
                                {  
                                    "space" : {"play" : [self.resourceLoader(frame, output=True) for frame in ['shoot{}.png'.format((i)) for i in range(0, 2)]],  "move" : (0, 0)}
                                }
                          }
        
        # Default action and orientation of the player
        self.image = self.control[self.action]["right"]["play"][self.frameIndex]
        self.rect  = self.image.get_rect(bottomleft=(0, 600-185))
        self.resourceLoader('shot.wav')

    
    # -------------- CONTROL RELATED METHODS --------------
    
    # Fly
    def fly(self):
        self.action = "fly"

    # Walk
    def walk(self):
        self.action = "walk"
    
    # Idle
    def idle(self):
        self.action = "idle"

    # Freefall method: defaultly allows the player to be controlled while falling (setting `self.action = "fly"`)
    # with speed of drop equal to also default value `1`. However, optional parameters allows the method to be used
    # on a `Game Over` event where we change the speed and disable player's control causing him to fall and disappear
    # from the screen
    def fall(self, speed=1, controllable=True):
        if controllable:
            self.action = "fly"
        
        self.rect.y += speed


    # Shoot function initialises bullet object
    def shoot(self, flying=False):
        self.playSound()

        self.action = "shoot"

        # Padding to adjust bullet position to spawn at barrel of gun
        xpadding = 0
        ypadding = 18
        
        # Set bullet's coordinates to that of player plus padding
        coordinates = player.rect.move(xpadding, ypadding)

        # Determine the timestamp of the current shot (ms)
        self.current_shot = pygame.time.get_ticks()

        # If the previous shot was longer than 250 ms ago, create a new one
        if self.current_shot - self.previous_shot > 250:

            # Instantiate bullet object
            Bullet('bullet.png', coordinates, [layers, bullets], priority=5)

            # Update the `previous_shot` variable
            self.previous_shot = pygame.time.get_ticks()


        # Change the player's image for the shooting pose which differs in flying and walking mode
        if not flying:
            self.image = self.control[self.action]["space"]["play"][0]

        else:
            self.image = self.control[self.action]["space"]["play"][1]

            # Passively (False flag) fall while shooting at the speed of `1`
            self.fall(1, False)

    # -------------- BEHAVIOUR RELATED METHODS --------------

    def harm(self):
        
        # Define the center of the player's rectangle and increment angle of rotation each clock tick
        # since this method operates inside the update method
        center      = self.rect.center
        self.angle += 30

        # If the player rotated the complete circle set the `angle` back to zero, restore the original image
        # and set the hit flag back to `false`
        if self.angle >= 720:
            self.angle = 0
            self.image = self.original
            self.hit   = False
        
        # Otherwise update the player's image rendering its rotated form and give it a slight push off 
        else:
            self.image = pygame.transform.rotate(self.original, self.angle)
            self.rect  = self.image.get_rect(center=center)
            self.rect  = self.rect.move(-4, -4)


    def gameover(self): 
        
        # Call internal method `fall()` which causes the player to fall downwards at speed `5`
        # at the same time disabling any steering (flag False)
        self.fall(5, False)

        myfont = pygame.font.Font("fonts/{}.ttf".format("west"), 100)
        textsurface = myfont.render('{}'.format("GAME OVER"), True, (102,0,0))
        screen.blit(textsurface, ((resolution['width']-textsurface.get_size()[0])/2, ((resolution['height']-textsurface.get_size()[1])-100)/2))
        textsurface = pygame.font.Font("fonts/{}.ttf".format("horseshoeslemonade"), 40).render('{}\t\t {}'.format("Q - Quit", "R - Play"), True, (0,0,0))
        screen.blit(textsurface, ((resolution['width']-textsurface.get_size()[0])/2, (resolution['height']-textsurface.get_size()[1]+100)/2))


    def attacked(self, damage):
        
        if self.life + damage <= 0:
            self.dead = True
            self.life = 0

        else:
            self.life += damage
        
        self.hit  = True
            

    def update(self, direction=None):
        
        if not direction:
            direction = "down"

        # Delete sprite if the player crossed the floor i.e. upon game over
        if self.rect.y > resolution['height']:
            self.kill()

        # Teleport the player to the opposite side of the screen when 
        # the screen's boundary was exceeded on either of the side
        #CHANGE THIS
        if self.rect.right >= resolution['width'] or self.rect.left <= 0:
            self.rect.x = self.rect.x%resolution['width']

        # Stop the player from flying through the ceiling
        if self.rect.top <= 0:
            self.rect.y = 0

        # ---

        # If the player got hit we invoke internal method `harm` which
        # animates the player causing him to rotate about transverse axis
        elif self.hit:
            self.harm()

        # Otherwise the method handles the player's movement control
        else:
            
            center = self.rect.center

            # Do not animate walk/fly/idle frames when the player is in shoot action
            # essentially, `freeze` the player for the shooting time
            if self.action != "shoot":
                
                # Change the animation frame and repeat when the sequence ended
                self.frameIndex += 1
                if self.frameIndex >= len(self.control[self.action][direction]["play"]):
                    self.frameIndex = 0

                # Make copy of the currently rendered image 
                # (used by the `harm` method to spin the player when got hit)
                self.original = self.image

                # Get the position before we change the animation and/or frame
                # so that new sequence will begin at the same location
                center      = self.rect.center
                self.image  = self.control[self.action][direction]["play"][self.frameIndex]
                self.rect   = self.image.get_rect(center=center)
                
                # Store displacement for current action and direction
                dx = self.control[self.action][direction]["move"][0]
                dy = self.control[self.action][direction]["move"][1]

                # Apply it
                self.rect.x -= dx
                self.rect.y -= dy





# ***********************************************                            ***********************************************
# *********************************************** @START GAME STATS CLASSES  ***********************************************
# ***********************************************                            ***********************************************

# Class for game statistics such as score and health
class Stats():

    def __init__(self):

        self.game_stats = list()


    def add(self, x, y, header, state=0, font="horseshoeslemonade"):
        self.game_stats.append({"position" : (x, y), "header" : header, "font" : font, "state" : state})


    def modify(self, stat, step):
        for statistic in self.game_stats:
            if statistic['header'] is stat:
                 change             = statistic['state'] + step
                 statistic['state'] = change if change >= 0 else 0
       

    def display(self):
        for statistic in self.game_stats:
            myfont      = pygame.font.Font("fonts/{}.ttf".format(statistic['font']), 40)
            textsurface = myfont.render('{}: {}'.format(statistic['header'], statistic['state']), True, (246, 220, 0))
            screen.blit(textsurface, statistic['position'])






# ***********************************************                      ***********************************************
# *********************************************** @START MENU CLASSES  ***********************************************
# ***********************************************                      ***********************************************

class Menu(GameSprite):

    def main(self):
         self.menu = self.resourceLoader('menu.png', output=True)

    def help(self):
         self.menu = self.resourceLoader('help.png', output=True)

    def display(self):
        global isMenu
        
        self.main()

        while isMenu:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONUP:
                    isMenu = False

                if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    self.help()

            screen.blit(self.menu, (0,0))
            pygame.display.update()






# ***********************************************                                  ***********************************************
# *********************************************** @START INITIALISE GAME VARIABLES ***********************************************
# ***********************************************                                  ***********************************************

def initialisation():
    
    # Instantiate menu object and its initial flag 
    global menu, isMenu
    
    menu = Menu()
    isMenu = True

    # Game stats
    global statistics
    statistics = Stats()
    
    # Add statistics and their specifications (x, y, header, state, [optional font])
    statistics.add(resolution['width']-240, resolution['height']-50, "Health", 100)
    statistics.add(10, resolution['height']-50, "Score")
    
    # Create sprite groups
    global layers, moveable, floor, dumb_enemies, bullets

    layers       = pygame.sprite.LayeredUpdates()
    moveable     = pygame.sprite.Group()
    floor        = pygame.sprite.Group()
    dumb_enemies = pygame.sprite.Group()
    bullets      = pygame.sprite.Group()
              
    
    # Allocate game objects to sprite groups, parameters passed in the constructor are:
    # 1) name of the filename, 2) list of layers to which particular sprite object will belong to,
    # 3) priority integer which will be assigned to the instance variable self._layer provided
    # by the pygame.sprite.LayeredUpdates object which uses this variable to order the sprites' drawing
    global landscape, mountain, ground, cactus, bomb, ufo, player, clouds

    landscape   = Landscape ('background.png', [layers, moveable],                         priority=0)
    mountain    = Mountain  ('mountain.png',   [layers, moveable],                         priority=2)
    ground      = Ground    ('ground.png',     [layers, moveable, floor],                  priority=3)
    cactus      = Cactus    ('cactus.png',     [layers, moveable, dumb_enemies],           priority=4)
    bomb        = Bomb      ('bomb.png',       [layers, moveable, dumb_enemies],           priority=4)
    ufo         = Ufo       ('ufo0.png',       [layers, moveable, dumb_enemies],           priority=4)
    player      = Cowboy    ('',               [layers],                                   priority=5)
    
    # Generate clouds (3 types cloud1.png, cloud2.png, cloud3 duplicated) using list comprehensions
    # and assign priority of drawing for each one randomly (-1, 3). As a result, some clouds will appear
    # in the background, others in foreground providing basic illusion of depth
    clouds = [
                Cloud(
                        'cloud{}.png'.format(random.randint(1,3)), 
                        [layers, moveable], 
                        priority=random.randint(-2,7)
                    )  for i in range(6)
            ]
    
    # Backing music track not in the initialisation method since it only needs to be loaded once and loop indefinitely
    pygame.mixer.music.load(os.path.join('sounds', 'main.wav'))

    # Input parameter is number of loops, -1 means indefinite loop
    pygame.mixer.music.play(-1)

    # Initialise the clock to constrain maximum FPS
    global clock
    clock = pygame.time.Clock()






# ***********************************************                         ***********************************************
# *********************************************** @START MAIN EVENT QUEUE ***********************************************
# ***********************************************                         ***********************************************

def main():

    initialisation()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


        # Show menu if necessary
        if isMenu:
            menu.display()

        # Check collision against dumb enemies (i.e. those which merely goes by starting from random 
        # locations and replicate themselves when exceed the windows's dimensions)
        player_collision = pygame.sprite.spritecollide(player, dumb_enemies, False)

        if player_collision:
            for enemy in player_collision:
                if enemy._layer > 1:
                    player.attacked(enemy.damage)
                    enemy.explode()
                    statistics.modify("Health", enemy.damage)

        # Check collisions between bullets and dumbe_enemies 
        bullets_collision = pygame.sprite.groupcollide(bullets, dumb_enemies, True, False)

        if bullets_collision:

            # The method items() returns a list of dict's (key, value) tuple pairs which we extract into two variables `bullet_item` and `enemy_item`
            # From documentation:
                # Every Sprite inside group1 is added to the return dictionary. The value for each item is the list of Sprites in group2 that intersect.
            for bullet_item, enemy_item in bullets_collision.items():
                enemy_item[0].explode()   
                statistics.modify("Score", 1)

            
        # Flag used to deactivate background scrolling when the player idles
        # Resets itself back to True after each cycle
        parallax = True   

        # Variable used to store the pressed key
        key      = None

        # When the player moves (key pressed), layers of background (grouped in a sprite's group moveable) 
        # undergo motion at various speeds whereas the player's state is modified in accordance with the type of the key pressed
        if event.type == pygame.KEYDOWN:
            
            if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE]:
            
                key = pygame.key.name(event.key)

                # IF THE PLAYER IS FLOATING
                if not pygame.sprite.spritecollide(player, floor, False):

                    # Ignore down arrow and simply fall
                    if event.key in [pygame.K_DOWN]:
                        player.fall()

                    elif event.key in [pygame.K_SPACE]:
                        player.shoot(True)

                    # Otherwise fly
                    else:
                        player.fly()
                
                # IF THE PLAYER IS ON THE GROUND
                else:

                    # Do nothing with the player on attempt to dig in the ground and stop parallax scrolling
                    if event.key in [pygame.K_DOWN]:
                        parallax = False
                        player.idle()
                    
                    # Walk horizontally when left or right arrows are pressed and stop parallax scrolling
                    elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                        parallax = False
                        player.walk()
                    
                    # Otherwise (i.e. K_UP), begin to fly
                    elif event.key in [pygame.K_UP]:
                        player.fly()
                    
                    else:
                        parallax = False
                        player.shoot()

            # IF THE PLAYER'S DIED AND THE R WAS PRESSED, PLAY AGAIN
            elif event.key in [pygame.K_r] and player.dead:
                player.dead = False
                initialisation()

            # IF THE PLAYER'S DIED AND THE Q WAS PRESSED, QUIT
            elif event.key in [pygame.K_q] and player.dead:
                sys.exit()

        # When the button is released, parallax effect ceases whereas player remains unchanged at this point
        elif event.type == pygame.KEYUP:

            # If the player is in the air and the keyboard is not used gradual fall should occur    
            if not pygame.sprite.spritecollide(player, floor, False):
                player.fall()

            # If the player is on the ground and the keyboard is not used player should idle
            else:
                parallax = False
                player.idle()
                

                
        # ---------------------- UPDATE ALL SPRITE GROUPS INDIVIDUALLY PASSING OPTIONAL PARAMETERS ----------------------

        # Update the background
        moveable.update(parallax)

        # Update all sprites belonging to the `layers` group (i.e. landscape, mountain, ground, clouds)
        # Pass the key name to the update() method which handles animation playback and reposition
        layers.update(key)

        # Update bullets
        #bullets.update()


        # ---------------------- DRAW ALL SPRITES ----------------------
        layers.draw(screen) 
        #bullets.draw(screen)
        

        # Display statistics (score & health)
        statistics.display()

        if player.dead:
            player.gameover()
        
        # UFO on the way!
        if ufo.counter < 400 and ufo.counter > 300:
            myfont = pygame.font.Font("fonts/{}.ttf".format("west"), 30)
            textsurface = myfont.render('{}'.format("THEY'VE SEEN YOU!"), True, (102,0,0))
            screen.blit(textsurface, ((resolution['width']-textsurface.get_size()[0])/2, (resolution['height']-textsurface.get_size()[1])/2))
            textsurface = myfont.render('{}'.format("FLY FORWARD AND TAKE THEM FROM THE BACK!"), True, (102,0,0))
            screen.blit(textsurface, ((resolution['width']-textsurface.get_size()[0])/2, ((resolution['height']-textsurface.get_size()[1])+80)/2))

        # Update the screen and erase
        pygame.display.update()
        screen.blit(background, (0,0))

        # Track how many frames were rendered in the current cycle
        # and force to utilise only 60
        clock.tick(60)



