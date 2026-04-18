import pygame
import sys
import os
from clock import get_angles, rotate_hand


pygame.init()
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Mouse Clock")
clock_timer = pygame.time.Clock()

current_dir = os.path.dirname(__file__)

def load_img(name):
    """Файлды папкадан немесе қасынан іздеп жүктеу"""
    path_here = os.path.join(current_dir, name)
    path_in_folder = os.path.join(current_dir, "images", name)
    
    target_path = ""
    if os.path.exists(path_here):
        target_path = path_here
    elif os.path.exists(path_in_folder):
        target_path = path_in_folder
    else:
        raise FileNotFoundError(f"Файл табылмады: {name}")
    
    return pygame.image.load(target_path).convert_alpha()


try:
    
    bg_raw = load_img("mickeybody.png")
    bg = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
    
    
    right_hand_img = load_img("righthand.png.png") 
    left_hand_img = load_img("lefthand.png.png")  
    

    right_hand_img = pygame.transform.scale(right_hand_img, (120, 380))
    left_hand_img = pygame.transform.scale(left_hand_img, (100, 320))
    
except Exception as e:
    print(f"Қате шықты: {e}")
    sys.exit()

CENTER = (WIDTH // 2, HEIGHT // 2)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    angle_sec, angle_min = get_angles()

    screen.fill((255, 255, 255)) 
    screen.blit(bg, (0, 0)) 

    
    rot_min, rect_min = rotate_hand(right_hand_img, angle_min, CENTER)
    screen.blit(rot_min, rect_min)

    
    rot_sec, rect_sec = rotate_hand(left_hand_img, angle_sec, CENTER)
    screen.blit(rot_sec, rect_sec)

    pygame.display.flip()
    clock_timer.tick(60)

pygame.quit()