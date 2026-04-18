import pygame
import sys
from player import MusicPlayer

def main():
    pygame.init()
    
    
    WIDTH, HEIGHT = 600, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame Music Player")
    
    
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    font = pygame.font.SysFont("Arial", 24)
    small_font = pygame.font.SysFont("Arial", 18)

    
    player = MusicPlayer("music") 

    running = True
    while running:
        screen.fill(WHITE)

    
        title_text = font.render("Music Player Controls:", True, BLACK)
        current_track_name = player.get_current_track_name()
        track_text = font.render(f"Track: {current_track_name}", True, (0, 100, 255))
        info_text = small_font.render("P: Play | S: Stop | N: Next | B: Back | Q: Quit", True, (100, 100, 100))
        
        screen.blit(title_text, (50, 50))
        screen.blit(track_text, (50, 150))
        screen.blit(info_text, (50, 300))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.prev_track()
                elif event.key == pygame.K_q:
                    running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()