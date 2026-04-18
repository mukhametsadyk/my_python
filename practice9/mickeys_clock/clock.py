import pygame
import datetime

def get_angles():
    now = datetime.datetime.now()
    
    angle_seconds = -(now.second * 6)

    angle_minutes = -(now.minute * 6 + now.second * 0.1)
    return angle_seconds, angle_minutes

def rotate_hand(image, angle, center_pos):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(center=center_pos).center)
    return rotated_image, new_rect
