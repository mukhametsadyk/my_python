
import pygame
from persistence import (
    load_leaderboard, save_leaderboard, add_entry,
    load_settings, save_settings,
)
from ui import (
    screen_username, screen_main_menu,
    screen_settings, screen_leaderboard,
    screen_game_over,
)
from racer import run_game, W, H


def main():
    pygame.init()
    pygame.display.set_caption("TSIS 3 — Racer")
    surf  = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()

    settings    = load_settings()
    leaderboard = load_leaderboard()

    
    username = settings.get("username", "").strip()
    if not username:
        username = screen_username(surf, clock, W, H)
        settings["username"] = username
        save_settings(settings)

    
    while True:
        action = screen_main_menu(surf, clock, W, H)

        if action == "quit":
            break

        elif action == "leaderboard":
            screen_leaderboard(surf, clock, W, H, leaderboard)

        elif action == "settings":
            settings = screen_settings(surf, clock, W, H, settings)
            save_settings(settings)

        elif action == "play":
            while True:
                result, score, distance, coins = run_game(surf, clock, settings, username)

                if result == "dead":
                    leaderboard = add_entry(leaderboard, username, score, distance)
                    choice = screen_game_over(surf, clock, W, H, score, distance, coins)
                    if choice == "retry":
                        continue     # play again immediately
                    else:
                        break        # back to main menu

                else:   # escaped to menu
                    break

    pygame.quit()


if __name__ == "__main__":
    main()