
import pygame

# ── Colours ──────────────────────────────────────────────
C_BG      = (15,  15,  25)
C_PANEL   = (25,  25,  45)
C_ACCENT  = (0,  200, 255)
C_WARN    = (255, 180,  0)
C_RED     = (220,  50,  50)
C_GREEN   = (50,  210, 100)
C_WHITE   = (255, 255, 255)
C_GREY    = (140, 140, 160)
C_DARK    = (40,   40,  60)

DIFF_COLORS = {"easy": C_GREEN, "normal": C_WARN, "hard": C_RED}

CAR_COLOR_OPTIONS = {
    "Cyan":   [0,   180, 255],
    "Red":    [220,  50,  50],
    "Green":  [50,  200,  80],
    "Yellow": [255, 220,   0],
    "White":  [230, 230, 230],
}




def draw_rect_alpha(surf, color, rect, alpha=180, radius=8):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(s, (rect[0], rect[1]))


def button(surf, rect, label, font, active=False, color=None):
    col  = color if color else (C_ACCENT if active else C_DARK)
    bord = C_WHITE if active else C_GREY
    pygame.draw.rect(surf, col,  rect, border_radius=8)
    pygame.draw.rect(surf, bord, rect, 2, border_radius=8)
    t = font.render(label, True, C_WHITE)
    surf.blit(t, t.get_rect(center=(rect[0]+rect[2]//2, rect[1]+rect[3]//2)))


def text(surf, s, font, color, cx, cy):
    t = font.render(s, True, color)
    surf.blit(t, t.get_rect(center=(cx, cy)))




def screen_username(surf, clock, W, H):
    font_lg = pygame.font.SysFont("segoeui", 40, bold=True)
    font_md = pygame.font.SysFont("segoeui", 26)
    font_sm = pygame.font.SysFont("segoeui", 20)
    name = ""
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif e.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif e.unicode.isprintable() and len(name) < 16:
                    name += e.unicode

        surf.fill(C_BG)
        text(surf, "RACER", font_lg, C_ACCENT, W//2, H//2-100)
        text(surf, "Enter your name:", font_md, C_WHITE, W//2, H//2-40)
        box = pygame.Rect(W//2-150, H//2, 300, 44)
        pygame.draw.rect(surf, C_DARK, box, border_radius=8)
        pygame.draw.rect(surf, C_ACCENT, box, 2, border_radius=8)
        t = font_md.render(name + "|", True, C_WHITE)
        surf.blit(t, t.get_rect(center=box.center))
        text(surf, "Press Enter to continue", font_sm, C_GREY, W//2, H//2+60)
        pygame.display.flip(); clock.tick(60)




def screen_main_menu(surf, clock, W, H):
    font_lg = pygame.font.SysFont("segoeui", 52, bold=True)
    font_md = pygame.font.SysFont("segoeui", 28)
    btns = ["Play", "Leaderboard", "Settings", "Quit"]
    rects = [pygame.Rect(W//2-130, H//2-30+i*60, 260, 46) for i in range(4)]
    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for i, r in enumerate(rects):
                    if r.collidepoint(mx, my):
                        return btns[i].lower()

        surf.fill(C_BG)
        text(surf, "🏎  RACER", font_lg, C_ACCENT, W//2, H//2-120)
        for i, (lbl, r) in enumerate(zip(btns, rects)):
            hover = r.collidepoint(mx, my)
            button(surf, r, lbl, font_md, active=hover)
        pygame.display.flip(); clock.tick(60)



def screen_settings(surf, clock, W, H, settings):
    font_lg = pygame.font.SysFont("segoeui", 36, bold=True)
    font_md = pygame.font.SysFont("segoeui", 24)
    font_sm = pygame.font.SysFont("segoeui", 19)
    s = settings.copy()
    back_r = pygame.Rect(W//2-80, H-70, 160, 42)

    color_names = list(CAR_COLOR_OPTIONS.keys())
    diff_names  = ["easy", "normal", "hard"]

    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if back_r.collidepoint(mx, my):
                    return s
                # sound toggle
                sr = pygame.Rect(W//2+60, H//2-120, 100, 36)
                if sr.collidepoint(mx, my):
                    s["sound"] = not s["sound"]
                # car color cycle
                ccr = pygame.Rect(W//2+60, H//2-60, 140, 36)
                if ccr.collidepoint(mx, my):
                    cur = next((k for k,v in CAR_COLOR_OPTIONS.items() if v==s["car_color"]), color_names[0])
                    idx = (color_names.index(cur)+1) % len(color_names)
                    s["car_color"] = CAR_COLOR_OPTIONS[color_names[idx]]
                # difficulty cycle
                dr = pygame.Rect(W//2+60, H//2, 140, 36)
                if dr.collidepoint(mx, my):
                    idx = (diff_names.index(s["difficulty"])+1) % len(diff_names)
                    s["difficulty"] = diff_names[idx]

        surf.fill(C_BG)
        text(surf, "Settings", font_lg, C_ACCENT, W//2, H//2-170)

        rows = [
            ("Sound",      "ON" if s["sound"] else "OFF", H//2-120, C_GREEN if s["sound"] else C_RED),
            ("Car Color",  next((k for k,v in CAR_COLOR_OPTIONS.items() if v==s["car_color"]), "Custom"), H//2-60, tuple(s["car_color"])),
            ("Difficulty", s["difficulty"].title(), H//2,    DIFF_COLORS.get(s["difficulty"], C_WHITE)),
        ]
        for lbl, val, ry, col in rows:
            t = font_md.render(lbl + ":", True, C_GREY)
            surf.blit(t, t.get_rect(midright=(W//2+50, ry+18)))
            vr = pygame.Rect(W//2+60, ry, 140, 36)
            pygame.draw.rect(surf, C_DARK, vr, border_radius=7)
            pygame.draw.rect(surf, col,    vr, 2,  border_radius=7)
            vt = font_md.render(val, True, col)
            surf.blit(vt, vt.get_rect(center=vr.center))

        button(surf, back_r, "← Back", font_md, active=back_r.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)



def screen_leaderboard(surf, clock, W, H, entries):
    font_lg = pygame.font.SysFont("segoeui", 36, bold=True)
    font_md = pygame.font.SysFont("segoeui", 22)
    font_sm = pygame.font.SysFont("segoeui", 18)
    back_r  = pygame.Rect(W//2-80, H-65, 160, 42)

    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if back_r.collidepoint(mx, my):
                    return

        surf.fill(C_BG)
        text(surf, "🏆  Leaderboard", font_lg, C_ACCENT, W//2, 55)

        header = f"{'#':<4} {'Name':<16} {'Score':>8}  {'Dist(m)':>8}"
        ht = font_sm.render(header, True, C_GREY)
        surf.blit(ht, (W//2-220, 100))
        pygame.draw.line(surf, C_GREY, (W//2-220, 122), (W//2+220, 122), 1)

        for i, e2 in enumerate(entries[:10]):
            row = f"{i+1:<4} {e2['name']:<16} {e2['score']:>8}  {e2['distance']:>8}"
            col = C_WARN if i == 0 else (C_WHITE if i < 3 else C_GREY)
            rt  = font_md.render(row, True, col)
            surf.blit(rt, (W//2-220, 130 + i*38))

        if not entries:
            text(surf, "No scores yet!", font_md, C_GREY, W//2, H//2)

        button(surf, back_r, "← Back", font_md, active=back_r.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)




def screen_game_over(surf, clock, W, H, score, distance, coins):
    font_lg = pygame.font.SysFont("segoeui", 44, bold=True)
    font_md = pygame.font.SysFont("segoeui", 26)
    retry_r = pygame.Rect(W//2-170, H//2+80, 150, 46)
    menu_r  = pygame.Rect(W//2+20,  H//2+80, 150, 46)
    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if retry_r.collidepoint(mx, my): return "retry"
                if menu_r.collidepoint(mx, my):  return "menu"

        surf.fill(C_BG)
        text(surf, "GAME OVER", font_lg, C_RED, W//2, H//2-110)
        lines = [
            (f"Score:    {score}",    C_ACCENT),
            (f"Distance: {int(distance)} m", C_WHITE),
            (f"Coins:    {coins}",    C_WARN),
        ]
        for j, (s_txt, col) in enumerate(lines):
            text(surf, s_txt, font_md, col, W//2, H//2-40+j*38)

        button(surf, retry_r, "Retry",     font_md, active=retry_r.collidepoint(mx,my))
        button(surf, menu_r,  "Main Menu", font_md, active=menu_r.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)