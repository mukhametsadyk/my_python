import pygame
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

current_color = BLUE
mode = 'brush'
canvas_color = WHITE

screen.fill(canvas_color)

def draw_menu():
    pygame.draw.rect(screen, GRAY, (0, 500, WIDTH, 100))
    pygame.draw.line(screen, BLACK, (0, 500), (WIDTH, 500), 2)

    colors = [RED, GREEN, BLUE, YELLOW, BLACK]
    color_rects = []
    for i, color in enumerate(colors):
        rect = pygame.Rect(20 + i * 60, 530, 50, 40)
        pygame.draw.rect(screen, color, rect)
        if current_color == color and mode != 'eraser':
            pygame.draw.rect(screen, BLACK, rect, 3)
        color_rects.append(rect)

    font = pygame.font.SysFont("Arial", 12, bold=True)
    
    eraser_rect = pygame.Rect(350, 530, 80, 40)
    pygame.draw.rect(screen, WHITE if mode == 'eraser' else (180, 180, 180), eraser_rect)
    screen.blit(font.render("ERASER", True, BLACK), (365, 542))

    rect_tool = pygame.Rect(440, 530, 80, 40)
    pygame.draw.rect(screen, WHITE if mode == 'rect' else (180, 180, 180), rect_tool)
    screen.blit(font.render("RECT", True, BLACK), (465, 542))

    circle_tool = pygame.Rect(530, 530, 80, 40)
    pygame.draw.rect(screen, WHITE if mode == 'circle' else (180, 180, 180), circle_tool)
    screen.blit(font.render("CIRCLE", True, BLACK), (550, 542))

    brush_tool = pygame.Rect(620, 530, 80, 40)
    pygame.draw.rect(screen, WHITE if mode == 'brush' else (180, 180, 180), brush_tool)
    screen.blit(font.render("BRUSH", True, BLACK), (640, 542))

    return color_rects, colors, eraser_rect, rect_tool, circle_tool, brush_tool

while True:
    color_rects, color_vals, eraser_btn, rect_btn, circle_btn, brush_btn = draw_menu()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            if mouse_pos[1] > 500:
                for i, rect in enumerate(color_rects):
                    if rect.collidepoint(mouse_pos):
                        current_color = color_vals[i]
                        mode = 'brush'
                
                if eraser_btn.collidepoint(mouse_pos): mode = 'eraser'
                if rect_btn.collidepoint(mouse_pos): mode = 'rect'
                if circle_btn.collidepoint(mouse_pos): mode = 'circle'
                if brush_btn.collidepoint(mouse_pos): mode = 'brush'
            
            else:
                draw_color = canvas_color if mode == 'eraser' else current_color
                if mode == 'rect':
                    pygame.draw.rect(screen, draw_color, (mouse_pos[0]-25, mouse_pos[1]-25, 50, 50))
                elif mode == 'circle':
                    pygame.draw.circle(screen, draw_color, mouse_pos, 25)

    if pygame.mouse.get_pressed()[0]:
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[1] < 500:
            draw_color = canvas_color if mode == 'eraser' else current_color
            if mode == 'brush':
                pygame.draw.circle(screen, draw_color, mouse_pos, 8)
            elif mode == 'eraser':
                pygame.draw.circle(screen, canvas_color, mouse_pos, 20)

    pygame.display.flip()
    clock.tick(120)
