import pygame
import time
import random

pygame.init()

WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)

WIDTH = 600
HEIGHT = 400
dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game Practice')

clock = pygame.time.Clock()
snake_block = 10 
initial_speed = 5 

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

def display_score(score, level):
    value = score_font.render("Score: " + str(score) + "  Level: " + str(level), True, YELLOW)
    dis.blit(value, [0, 0])

def draw_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, GREEN, [x[0], x[1], snake_block, snake_block])

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [WIDTH / 6, HEIGHT / 3])

def gameLoop():
    game_over = False
    game_close = False

    x1 = WIDTH / 2
    y1 = HEIGHT / 2
    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1
    score = 0
    level = 1
    speed = initial_speed

    foodx = round(random.randrange(0, WIDTH - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, HEIGHT - snake_block) / 10.0) * 10.0

    while not game_over:

        while game_close == True:
            dis.fill(BLUE)
            message("Ойын бітті! Q-шығу немесе C-қайта бастау", RED)
            display_score(score, level)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block
                    x1_change = 0

        if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
            game_close = True
        
        x1 += x1_change
        y1 += y1_change
        dis.fill(BLACK)
        
        pygame.draw.rect(dis, RED, [foodx, foody, snake_block, snake_block])
        
        snake_Head = []
        snake_Head.append(x1)
        snake_Head.append(y1)
        snake_List.append(snake_Head)
        
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        draw_snake(snake_block, snake_List)
        display_score(score, level)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            while True:
                foodx = round(random.randrange(0, WIDTH - snake_block) / 10.0) * 10.0
                foody = round(random.randrange(0, HEIGHT - snake_block) / 10.0) * 10.0
                if [foodx, foody] not in snake_List:
                    break
            
            Length_of_snake += 1
            score += 1
            
            if score % 3 == 0: 
                level += 1
                speed += 1 

        clock.tick(speed)

    pygame.quit()
    quit()

gameLoop()