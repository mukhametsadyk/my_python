import pygame
import sys


W, H = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BALL_RADIUS = 25
STEP = 20

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Ball Game: Ultimate Logic")
clock = pygame.time.Clock()

ball_x, ball_y = W // 2, H // 2

running = True
while running:
    screen.fill(WHITE)
    
    
    at_top = (ball_y - BALL_RADIUS <= 0)
    at_bottom = (ball_y + BALL_RADIUS >= H)
    at_left = (ball_x - BALL_RADIUS <= 0)
    at_right = (ball_x + BALL_RADIUS >= W)
    
    if at_top or at_bottom or at_left or at_right:
        current_color = GREEN
    else:
        current_color = RED

    
    pygame.draw.circle(screen, current_color, (int(ball_x), int(ball_y)), BALL_RADIUS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_UP:
                ball_y -= STEP
                if ball_y < BALL_RADIUS: ball_y = BALL_RADIUS 
            
            if event.key == pygame.K_DOWN:
                ball_y += STEP
                if ball_y > H - BALL_RADIUS: ball_y = H - BALL_RADIUS 
            
            
            if event.key == pygame.K_LEFT:
                ball_x -= STEP
                if ball_x + BALL_RADIUS < 0:
                    ball_x = W + BALL_RADIUS 
            
            if event.key == pygame.K_RIGHT:
                ball_x += STEP
                if ball_x - BALL_RADIUS > W: 
                    ball_x = -BALL_RADIUS 

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()