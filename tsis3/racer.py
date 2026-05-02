
import pygame, random, math


W, H       = 800, 650
ROAD_X     = 150          
ROAD_W     = 500         
LANE_COUNT = 4
LANE_W     = ROAD_W // LANE_COUNT

def lane_center(lane):  
    return ROAD_X + lane * LANE_W + LANE_W // 2

# ── Colours ──────────────────────────────────────────────
C_BG      = (20,  20,  30)
C_ROAD    = (50,  50,  60)
C_LANE    = (200, 200, 200)
C_GRASS   = (30,  80,  30)
C_WHITE   = (255, 255, 255)
C_YELLOW  = (255, 220,   0)
C_RED     = (220,  50,  50)
C_GREEN   = (50,  210, 100)
C_CYAN    = (0,   200, 255)
C_ORANGE  = (255, 140,   0)
C_PURPLE  = (180,  80, 220)


PLAYER_W, PLAYER_H     = 38, 64
TRAFFIC_W, TRAFFIC_H   = 36, 60
OBS_W,     OBS_H       = 44, 22
COIN_R                 = 10
PU_R                   = 14


DIFF = {
    "easy":   {"base_speed": 4,  "traffic_rate": 120, "obs_rate": 180, "score_mult": 1.0},
    "normal": {"base_speed": 6,  "traffic_rate": 80,  "obs_rate": 120, "score_mult": 1.5},
    "hard":   {"base_speed": 9,  "traffic_rate": 50,  "obs_rate": 80,  "score_mult": 2.0},
}


STRIPE_H    = 40
STRIPE_GAP  = 40



class PlayerCar:
    def __init__(self, lane, color):
        self.lane   = lane
        self.x      = lane_center(lane)
        self.y      = H - 110
        self.w, self.h = PLAYER_W, PLAYER_H
        self.color  = tuple(color)
        self.speed  = 0        
        self.nitro  = False
        self.shield = False

    def rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)

    def draw(self, surf):
        r = self.rect()
        # body
        pygame.draw.rect(surf, self.color, r, border_radius=6)
        
        pygame.draw.rect(surf, (180,220,255),
                         (r.x+6, r.y+10, r.w-12, 16), border_radius=3)
        
        for wx, wy in [(r.x-4, r.y+8), (r.x+r.w, r.y+8),
                       (r.x-4, r.y+r.h-20), (r.x+r.w, r.y+r.h-20)]:
            pygame.draw.rect(surf, (30,30,30), (wx, wy, 8, 14), border_radius=2)
        
        if self.shield:
            s = pygame.Surface((r.w+20, r.h+20), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (0,180,255,80), (0,0,r.w+20,r.h+20))
            surf.blit(s, (r.x-10, r.y-10))
        
        if self.nitro:
            pts = [(r.centerx-10, r.bottom),
                   (r.centerx,    r.bottom+24),
                   (r.centerx+10, r.bottom)]
            pygame.draw.polygon(surf, C_ORANGE, pts)


class TrafficCar:
    COLORS = [(200,60,60),(60,180,60),(200,160,0),(100,100,200),(180,80,200)]

    def __init__(self, lane, speed):
        self.lane  = lane
        self.x     = lane_center(lane)
        self.y     = -TRAFFIC_H
        self.speed = speed
        self.color = random.choice(self.COLORS)
        self.w, self.h = TRAFFIC_W, TRAFFIC_H

    def rect(self):
        return pygame.Rect(self.x-self.w//2, self.y-self.h//2, self.w, self.h)

    def update(self, road_speed):
        self.y += self.speed + road_speed

    def draw(self, surf):
        r = self.rect()
        pygame.draw.rect(surf, self.color, r, border_radius=5)
        pygame.draw.rect(surf, (180,220,255), (r.x+5, r.y+8, r.w-10, 12), border_radius=2)

    def off_screen(self):
        return self.y > H + self.h


class Obstacle:
    """Oil spill, pothole, or barrier."""
    KINDS = ["oil", "pothole", "barrier"]

    def __init__(self, lane, speed):
        self.lane  = lane
        self.x     = lane_center(lane)
        self.y     = -OBS_H
        self.speed = speed
        self.kind  = random.choice(self.KINDS)
        self.w, self.h = OBS_W, OBS_H

    def rect(self):
        return pygame.Rect(self.x-self.w//2, self.y-self.h//2, self.w, self.h)

    def update(self, road_speed):
        self.y += self.speed * 0.6 + road_speed

    def draw(self, surf):
        r = self.rect()
        if self.kind == "oil":
            pygame.draw.ellipse(surf, (40,40,80),   r)
            pygame.draw.ellipse(surf, (80,80,160),  r, 2)
        elif self.kind == "pothole":
            pygame.draw.ellipse(surf, (20,20,20),   r)
            pygame.draw.ellipse(surf, (60,60,60),   r, 2)
        else:  # barrier
            pygame.draw.rect(surf, C_RED, r, border_radius=4)
            pygame.draw.rect(surf, C_WHITE, r, 2, border_radius=4)
            pygame.draw.line(surf, C_WHITE, (r.x, r.centery), (r.right, r.centery), 2)

    def off_screen(self):
        return self.y > H + self.h


class Coin:
    VALUES = [1, 2, 5]
    COLORS = {1: C_YELLOW, 2: C_CYAN, 5: C_ORANGE}

    def __init__(self, lane, speed):
        self.lane  = lane
        self.x     = lane_center(lane)
        self.y     = -COIN_R
        self.speed = speed
        self.value = random.choices(self.VALUES, weights=[6,3,1])[0]

    def rect(self):
        return pygame.Rect(self.x-COIN_R, self.y-COIN_R, COIN_R*2, COIN_R*2)

    def update(self, road_speed):
        self.y += self.speed * 0.5 + road_speed

    def draw(self, surf):
        col = self.COLORS[self.value]
        pygame.draw.circle(surf, col, (self.x, self.y), COIN_R)
        pygame.draw.circle(surf, C_WHITE, (self.x, self.y), COIN_R, 2)
        f = pygame.font.SysFont("segoeui", 11, bold=True)
        t = f.render(str(self.value), True, (30,30,30))
        surf.blit(t, t.get_rect(center=(self.x, self.y)))

    def off_screen(self):
        return self.y > H + COIN_R*2


class PowerUp:
    KINDS = ["nitro", "shield", "repair"]
    COLORS = {"nitro": C_ORANGE, "shield": C_CYAN, "repair": C_GREEN}
    SYMBOLS = {"nitro": "N", "shield": "S", "repair": "R"}
    LIFETIME = 6000  # ms before disappearing

    def __init__(self, lane, speed):
        self.lane    = lane
        self.x       = lane_center(lane)
        self.y       = -PU_R
        self.speed   = speed
        self.kind    = random.choice(self.KINDS)
        self.born    = pygame.time.get_ticks()

    def rect(self):
        return pygame.Rect(self.x-PU_R, self.y-PU_R, PU_R*2, PU_R*2)

    def update(self, road_speed):
        self.y += self.speed * 0.4 + road_speed

    def draw(self, surf):
        col  = self.COLORS[self.kind]
        sym  = self.SYMBOLS[self.kind]
        pygame.draw.circle(surf, col, (self.x, self.y), PU_R)
        pygame.draw.circle(surf, C_WHITE, (self.x, self.y), PU_R, 2)
        f = pygame.font.SysFont("segoeui", 13, bold=True)
        t = f.render(sym, True, C_WHITE)
        surf.blit(t, t.get_rect(center=(self.x, self.y)))

    def expired(self):
        return pygame.time.get_ticks() - self.born > self.LIFETIME

    def off_screen(self):
        return self.y > H + PU_R*2


class NitroStrip:
    """Road event: a full-width speed-boost strip."""
    def __init__(self, speed):
        self.y     = -20
        self.h     = 20
        self.speed = speed

    def update(self, road_speed):
        self.y += self.speed * 0.5 + road_speed

    def draw(self, surf):
        s = pygame.Surface((ROAD_W, self.h), pygame.SRCALPHA)
        s.fill((255, 160, 0, 100))
        surf.blit(s, (ROAD_X, self.y))
        pygame.draw.line(surf, C_ORANGE, (ROAD_X, self.y), (ROAD_X+ROAD_W, self.y), 2)

    def off_screen(self):
        return self.y > H + self.h

    def rect(self):
        return pygame.Rect(ROAD_X, self.y, ROAD_W, self.h)




def draw_hud(surf, score, distance, coins, pu_kind, pu_timer_ms, shield, font_md, font_sm):
    
    lines = [
        (f"Score: {score}",        (255,220,  0)),
        (f"Dist:  {int(distance)}m",(200,200,200)),
        (f"Coins: {coins}",        (0, 220, 255)),
    ]
    for i, (txt, col) in enumerate(lines):
        t = font_sm.render(txt, True, col)
        surf.blit(t, (10, 10 + i*24))

    
    if pu_kind:
        col = PowerUp.COLORS.get(pu_kind, (200,200,200))
        sec = max(0, pu_timer_ms) / 1000
        msg = f"{pu_kind.upper()}"
        if pu_kind != "repair":
            msg += f"  {sec:.1f}s"
        t = font_sm.render(msg, True, col)
        surf.blit(t, (10, 82))
        if pu_kind != "repair":
            bar_w = int(80 * max(0, pu_timer_ms) / (4000 if pu_kind=="nitro" else 8000))
            pygame.draw.rect(surf, (50,50,70),  (10, 100, 80, 8), border_radius=4)
            pygame.draw.rect(surf, col,          (10, 100, bar_w, 8), border_radius=4)



def draw_road(surf, stripe_y):
    surf.fill((25, 70, 25))
    pygame.draw.rect(surf, C_ROAD, (ROAD_X, 0, ROAD_W, H))

    
    for lane in range(1, LANE_COUNT):
        lx = ROAD_X + lane * LANE_W
        y  = int(stripe_y) % (STRIPE_H + STRIPE_GAP) - (STRIPE_H + STRIPE_GAP)
        while y < H:
            pygame.draw.rect(surf, C_LANE, (lx-2, y, 4, STRIPE_H))
            y += STRIPE_H + STRIPE_GAP

    
    pygame.draw.line(surf, C_WHITE, (ROAD_X,          0), (ROAD_X,          H), 3)
    pygame.draw.line(surf, C_WHITE, (ROAD_X + ROAD_W, 0), (ROAD_X + ROAD_W, H), 3)




def run_game(surf, clock, settings, username):
    diff     = settings.get("difficulty", "normal")
    dp       = DIFF[diff]
    base_spd = dp["base_speed"]
    score_mult = dp["score_mult"]

    
    player   = PlayerCar(1, settings["car_color"])
    road_spd = base_spd
    stripe_y = 0.0
    distance = 0.0
    score    = 0
    coins_c  = 0
    frame    = 0

    traffic_list   = []
    obstacle_list  = []
    coin_list      = []
    pu_list        = []
    nitro_strips   = []

    traffic_timer  = 0
    obs_timer      = 0
    coin_timer     = 0
    pu_timer_sp    = 0   
    event_timer    = 0

    # Active power-up
    pu_active     = None   
    pu_end_ms     = 0

    font_md = pygame.font.SysFont("segoeui", 22, bold=True)
    font_sm = pygame.font.SysFont("segoeui", 18)

    def safe_lane_for_spawn():
        """Pick a lane not occupied by player at bottom."""
        occupied = {player.lane}
        return random.choice([l for l in range(LANE_COUNT) if l not in occupied])

    def difficulty_speed():
        """Scale road speed with distance."""
        bonus = min(distance / 500, 6)
        return base_spd + bonus

    def difficulty_traffic_interval():
        progress = min(distance / 1000, 1)
        return int(dp["traffic_rate"] * (1 - 0.5 * progress))

    def difficulty_obs_interval():
        progress = min(distance / 1000, 1)
        return int(dp["obs_rate"] * (1 - 0.5 * progress))

    running = True
    while running:
        dt = clock.tick(60)
        now = pygame.time.get_ticks()

        # ── Events ────────────────────────────────────────
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    if player.lane > 0: player.lane -= 1
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    if player.lane < LANE_COUNT-1: player.lane += 1
                if e.key == pygame.K_ESCAPE:
                    return "menu", score, distance, coins_c

        player.x = lane_center(player.lane)

        
        road_spd = difficulty_speed()
        if pu_active == "nitro":
            road_spd *= 1.8
        stripe_y += road_spd
        distance += road_spd * 0.05

        score = int((distance * 0.3 + coins_c * 10) * score_mult)

        
        player.nitro  = (pu_active == "nitro")
        player.shield = (pu_active == "shield")
        pu_timer_ms   = 0
        if pu_active in ("nitro", "shield"):
            pu_timer_ms = pu_end_ms - now
            if pu_timer_ms <= 0:
                pu_active = None

        
        frame += 1
        traffic_timer += 1
        obs_timer     += 1
        coin_timer    += 1
        pu_timer_sp   += 1
        event_timer   += 1

        if traffic_timer >= difficulty_traffic_interval():
            traffic_timer = 0
            lane = safe_lane_for_spawn()
            spd  = road_spd * random.uniform(0.4, 0.9)
            traffic_list.append(TrafficCar(lane, spd))

        if obs_timer >= difficulty_obs_interval():
            obs_timer = 0
            lane = safe_lane_for_spawn()
            obstacle_list.append(Obstacle(lane, road_spd))

        if coin_timer >= 45:
            coin_timer = 0
            lane = random.randint(0, LANE_COUNT-1)
            coin_list.append(Coin(lane, road_spd))

        if pu_timer_sp >= 200:
            pu_timer_sp = 0
            lane = random.randint(0, LANE_COUNT-1)
            pu_list.append(PowerUp(lane, road_spd))

        if event_timer >= 300:
            event_timer = 0
            nitro_strips.append(NitroStrip(road_spd))

       
        p_rect = player.rect()

        for t_car in traffic_list[:]:
            t_car.update(road_spd)
            if t_car.off_screen():
                traffic_list.remove(t_car); continue
            if p_rect.colliderect(t_car.rect()):
                if player.shield:
                    player.shield = False
                    pu_active = None
                    traffic_list.remove(t_car)
                else:
                    return "dead", score, distance, coins_c

        for obs in obstacle_list[:]:
            obs.update(road_spd)
            if obs.off_screen():
                obstacle_list.remove(obs); continue
            if p_rect.colliderect(obs.rect()):
                if player.shield:
                    player.shield = False
                    pu_active = None
                    obstacle_list.remove(obs)
                else:
                    return "dead", score, distance, coins_c

        for coin in coin_list[:]:
            coin.update(road_spd)
            if coin.off_screen():
                coin_list.remove(coin); continue
            if p_rect.colliderect(coin.rect()):
                coins_c += coin.value
                coin_list.remove(coin)

        for pu in pu_list[:]:
            pu.update(road_spd)
            if pu.off_screen() or pu.expired():
                pu_list.remove(pu); continue
            if p_rect.colliderect(pu.rect()):
                kind = pu.kind
                pu_list.remove(pu)
                if kind == "nitro":
                    pu_active = "nitro"
                    pu_end_ms = now + 4000
                elif kind == "shield":
                    pu_active = "shield"
                    pu_end_ms = now + 8000
                elif kind == "repair":
                    pu_active = "repair"
                    pu_end_ms = now + 1000   # brief display

        for ns in nitro_strips[:]:
            ns.update(road_spd)
            if ns.off_screen():
                nitro_strips.remove(ns); continue
            if p_rect.colliderect(ns.rect()) and pu_active != "nitro":
                pu_active = "nitro"
                pu_end_ms = now + 2000   # short boost

        
        draw_road(surf, stripe_y)

        for ns in nitro_strips: ns.draw(surf)
        for obs in obstacle_list: obs.draw(surf)
        for coin in coin_list:   coin.draw(surf)
        for pu  in pu_list:      pu.draw(surf)
        for t_car in traffic_list: t_car.draw(surf)
        player.draw(surf)

        draw_hud(surf, score, distance, coins_c,
                 pu_active, pu_timer_ms, player.shield,
                 font_md, font_sm)

        pygame.display.flip()

    return "menu", score, distance, coins_c