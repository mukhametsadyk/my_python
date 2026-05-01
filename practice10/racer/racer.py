import pygame, sys
from pygame.locals import *
import random, time

pygame.init()


FPS = 60
FramePerSec = pygame.time.Clock()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COIN_SCORE = 0 


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)

DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game")


font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over_text = font.render("Game Over", True, BLACK)


background = pygame.image.load("background.png")

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        
        self.image = pygame.image.load("Enemy.png").convert_alpha()
        
        self.image.set_colorkey(WHITE)
        
        self.image = pygame.transform.scale(self.image, (40, 80))
        self.rect = self.image.get_rect()
        # Басында экранның төбесінен жоғары (көрінбейтін жерде) пайда болады
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
        self.image = pygame.image.load("Player.png").convert_alpha()
        self.image.set_colorkey(WHITE) # Ақ фонды жою
        self.image = pygame.transform.scale(self.image, (40, 80)) # Көлікті кішірейту
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
       
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0:
              if pressed_keys[K_LEFT]:
                  self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH:        
              if pressed_keys[K_RIGHT]:
                  self.rect.move_ip(5, 0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("coin.png").convert_alpha()
        self.image.set_colorkey(WHITE) # Ақ фонды жою
        self.image = pygame.transform.scale(self.image, (30, 30)) # Тиынды кішірейту
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -100)

    def move(self):
        self.rect.move_ip(0, SPEED)
        if (self.rect.top > SCREEN_HEIGHT):
            self.spawn()

    def spawn(self):
        self.rect.top = -100
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -100)

# Спрайттарды құру
P1 = Player()
E1 = Enemy()
C1 = Coin()

# Топтарды құру
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# Жылдамдықты арттыру оқиғасы
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Ойынның негізгі циклі
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
              SPEED += 0.5      
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Экранды жаңарту
    DISPLAYSURF.blit(background, (0,0))
    
    # Есептерді шығару
    scores = font_small.render("Score: " + str(SCORE), True, BLACK)
    coin_txt = font_small.render("Coins: " + str(COIN_SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10,10))
    DISPLAYSURF.blit(coin_txt, (SCREEN_WIDTH - 100, 10))

    # Қозғалыс және сурет салу
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # Тиын жинауды тексеру
    if pygame.sprite.spritecollideany(P1, coins):
        COIN_SCORE += 1
        C1.spawn()

    # Қарсыласпен соқтығысуды тексеру
    if pygame.sprite.spritecollideany(P1, enemies):
          try:
              # crash.wav немесе crash.mp3 екенін тексеріңіз
              pygame.mixer.Sound('crash.wav').play()
          except:
              pass
          
          time.sleep