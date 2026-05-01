import pygame, sys
from pygame.locals import *
import random, time


pygame.init()


FPS = 60
FramePerSec = pygame.time.Clock()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 3  
SCORE = 0
COIN_SCORE = 0 


BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY  = (50, 50, 50)


DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game - Slow Version")


font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over_text = font.render("Game Over", True, WHITE)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        # Суретсіз, жай ғана қызыл төртбұрыш
        self.image = pygame.Surface((40, 70))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -100)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > SCREEN_HEIGHT):
            SCORE += 1
            self.rect.top = -100
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -100)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        
        self.image = pygame.Surface((40, 70))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (200, 520)
       
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0:
              if pressed_keys[K_LEFT]:
                  self.rect.move_ip(-6, 0) 
        if self.rect.right < SCREEN_WIDTH:        
              if pressed_keys[K_RIGHT]:
                  self.rect.move_ip(6, 0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -100)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > SCREEN_HEIGHT):
            self.spawn()

    def spawn(self):
        self.rect.top = -100
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -100)


P1 = Player()
E1 = Enemy()
C1 = Coin()

enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)


INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 3000)


while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
              SPEED += 0.2     
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
    DISPLAYSURF.fill(GREY)
    
    
    pygame.draw.line(DISPLAYSURF, WHITE, (200, 0), (200, 600), 5)
    
    
    scores = font_small.render("Score: " + str(SCORE), True, WHITE)
    coin_txt = font_small.render("Coins: " + str(COIN_SCORE), True, WHITE)
    curr_speed = font_small.render("Speed: " + str(round(SPEED, 1)), True, WHITE)
    
    DISPLAYSURF.blit(scores, (10,10))
    DISPLAYSURF.blit(coin_txt, (SCREEN_WIDTH - 100, 10))
    DISPLAYSURF.blit(curr_speed, (10, 35))

    
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    
    if pygame.sprite.spritecollideany(P1, coins):
        COIN_SCORE += 1
        C1.spawn()

    
    if pygame.sprite.spritecollideany(P1, enemies):
          time.sleep(0.5)
          DISPLAYSURF.fill(RED)
          DISPLAYSURF.blit(game_over_text, (30, 250))
          pygame.display.update()
          time.sleep(2)
          pygame.quit()
          sys.exit()        
        
    pygame.display.update()
    FramePerSec.tick(FPS)