import pygame
import random
import json
import os
from db import *
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLOCK_SIZE

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
f_small = pygame.font.SysFont("Verdana", 20)
f_mid = pygame.font.SysFont("Verdana", 30)
f_big = pygame.font.SysFont("Verdana", 50)

def load_settings():
    if os.path.exists("settings.json"):
        try:
            if os.path.getsize("settings.json") > 0:
                with open("settings.json", "r") as f: return json.load(f)
        except: pass
    return {"color": [0, 255, 0], "grid": True, "sound": True}

def save_settings(data):
    with open("settings.json", "w") as f: json.dump(data, f)

st = load_settings()

class Game:
    def __init__(self, user):
        self.user = user
        self.p_id = get_or_create_player(user)
        self.best = get_personal_best(self.p_id)
        self.snake = [[100, 100], [80, 100], [60, 100]]
        self.dir = [BLOCK_SIZE, 0]
        self.score = 0
        self.level = 1
        self.speed = 5
        self.obstacles = []
        self.food = self.spawn("food")
        self.poison = self.spawn("poison")
        self.power = None
        self.shield = False
        self.pu_end = 0

    def spawn(self, t):
        while True:
            p = [random.randrange(0, SCREEN_WIDTH//BLOCK_SIZE)*BLOCK_SIZE, 
                 random.randrange(0, SCREEN_HEIGHT//BLOCK_SIZE)*BLOCK_SIZE]
            if p not in self.snake and p not in self.obstacles: return {"p": p, "t": t, "s": pygame.time.get_ticks()}

    def update_level(self):
        self.level += 1
        self.speed += 1
        if self.level >= 3:
            self.obstacles = []
            for _ in range(self.level * 2):
                o = [random.randrange(0, SCREEN_WIDTH//BLOCK_SIZE)*BLOCK_SIZE, random.randrange(0, SCREEN_HEIGHT//BLOCK_SIZE)*BLOCK_SIZE]
                if o not in self.snake: self.obstacles.append(o)

    def logic(self):
        head = [self.snake[0][0] + self.dir[0], self.snake[0][1] + self.dir[1]]
        
        if head[0] < 0 or head[0] >= SCREEN_WIDTH or head[1] < 0 or head[1] >= SCREEN_HEIGHT or head in self.snake or head in self.obstacles:
            if self.shield:
                self.shield = False
                self.snake.pop()
                return True
            save_game_result(self.p_id, self.score, self.level)
            return False

        self.snake.insert(0, head)
        if head == self.food["p"]:
            self.score += 10
            if self.score % 30 == 0: self.update_level()
            self.food = self.spawn("food")
        else:
            self.snake.pop()

        if head == self.poison["p"]:
            if len(self.snake) <= 2:
                save_game_result(self.p_id, self.score, self.level)
                return False
            self.snake.pop(); self.snake.pop()
            self.poison = self.spawn("poison")

        now = pygame.time.get_ticks()
        if not self.power and random.random() < 0.02: self.power = self.spawn("pu")
        if self.power:
            if now - self.power["s"] > 8000: self.power = None
            elif head == self.power["p"]:
                self.shield = True
                self.power = None

        return True

    def draw(self):
        screen.fill((0, 0, 0))
        if st["grid"]:
            for x in range(0, SCREEN_WIDTH, BLOCK_SIZE): pygame.draw.line(screen, (30,30,30), (x,0), (x,SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE): pygame.draw.line(screen, (30,30,30), (0,y), (SCREEN_WIDTH,y))
        for b in self.snake: pygame.draw.rect(screen, st["color"], (*b, BLOCK_SIZE-2, BLOCK_SIZE-2))
        pygame.draw.rect(screen, (0, 255, 0), (*self.food["p"], BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(screen, (255, 0, 0), (*self.poison["p"], BLOCK_SIZE, BLOCK_SIZE))
        for o in self.obstacles: pygame.draw.rect(screen, (100, 100, 100), (*o, BLOCK_SIZE, BLOCK_SIZE))
        if self.power: pygame.draw.circle(screen, (255, 255, 0), (self.power["p"][0]+10, self.power["p"][1]+10), 10)
        txt = f_small.render(f"Score: {self.score} Lvl: {self.level} Best: {self.best} {'[SHIELD]' if self.shield else ''}", True, (255, 255, 255))
        screen.blit(txt, (10, 10))

def menu():
    user = ""
    while True:
        screen.fill((20, 20, 20))
        screen.blit(f_big.render("SNAKE DATABASE", True, (0, 255, 0)), (180, 100))
        screen.blit(f_mid.render(f"Username: {user}", True, (255, 255, 255)), (220, 250))
        screen.blit(f_small.render("ENTER: Play | L: Leaderboard | S: Settings", True, (150, 150, 150)), (180, 450))
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and user:
                    g = Game(user)
                    run = True
                    while run:
                        for ge in pygame.event.get():
                            if ge.type == pygame.QUIT: run = False
                            if ge.type == pygame.KEYDOWN:
                                if ge.key == pygame.K_UP and g.dir != [0, BLOCK_SIZE]: g.dir = [0, -BLOCK_SIZE]
                                if ge.key == pygame.K_DOWN and g.dir != [0, -BLOCK_SIZE]: g.dir = [0, BLOCK_SIZE]
                                if ge.key == pygame.K_LEFT and g.dir != [BLOCK_SIZE, 0]: g.dir = [-BLOCK_SIZE, 0]
                                if ge.key == pygame.K_RIGHT and g.dir != [-BLOCK_SIZE, 0]: g.dir = [BLOCK_SIZE, 0]
                        if not g.logic(): run = False
                        g.draw()
                        pygame.display.flip()
                        clock.tick(g.speed)
                elif e.key == pygame.K_l: leaderboard()
                elif e.key == pygame.K_s: settings_screen()
                elif e.key == pygame.K_BACKSPACE: user = user[:-1]
                else: 
                    if len(user) < 12 and e.unicode.isalnum(): user += e.unicode
        pygame.display.flip()

def leaderboard():
    while True:
        screen.fill((10, 10, 10))
        screen.blit(f_mid.render("TOP 10 SCORES", True, (255, 215, 0)), (280, 50))
        data = get_leaderboard()
        for i, r in enumerate(data):
            screen.blit(f_small.render(f"{i+1}. {r[0]} - {r[1]} (Lvl {r[2]})", True, (255,255,255)), (220, 120 + i*35))
        screen.blit(f_small.render("Press ESC to Back", True, (200, 0, 0)), (300, 520))
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
        pygame.display.flip()

def settings_screen():
    global st
    while True:
        screen.fill((30, 30, 30))
        screen.blit(f_mid.render("SETTINGS", True, (255, 255, 255)), (320, 100))
        screen.blit(f_small.render(f"1. Grid: {'ON' if st['grid'] else 'OFF'}", True, (255,255,255)), (300, 200))
        screen.blit(f_small.render(f"2. Snake Color: {st['color']}", True, (255,255,255)), (300, 250))
        screen.blit(f_small.render("Press G for Grid | C for Color | ESC to Save", True, (150,150,150)), (180, 400))
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_g: st["grid"] = not st["grid"]
                if e.key == pygame.K_c: st["color"] = [random.randint(50,255) for _ in range(3)]
                if e.key == pygame.K_ESCAPE: save_settings(st); return
        pygame.display.flip()

if __name__ == "__main__": menu()